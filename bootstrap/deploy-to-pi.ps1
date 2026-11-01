[CmdletBinding()]
param(
    [Parameter(Mandatory = $true)]
    [string]$HostName,

    [string]$UserName = "pi",

    [int]$SshPort = 22,

    [string]$ProjectRoot = (Resolve-Path (Join-Path $PSScriptRoot "..")).Path,

    [string]$RemoteTempDir = "/tmp/openspoofen-deploy",

    [string]$LocalEnvFile,

    [string]$LocalWifiEnvFile,

    [string]$LocalTvModeEnvFile,

    [switch]$TunePiOs,

    [switch]$RebootAfterInstall
)

$ErrorActionPreference = "Stop"

$excludeNames = @(
    ".git",
    ".github",
    ".idea",
    ".mypy_cache",
    ".pytest_cache",
    ".ruff_cache",
    ".venv",
    ".vscode",
    "build",
    "dist",
    "htmlcov",
    "logs",
    "secrets",
    "tmp",
    "var",
    "__pycache__"
)

function Require-Command {
    param([Parameter(Mandatory = $true)][string]$Name)

    if (-not (Get-Command $Name -ErrorAction SilentlyContinue)) {
        throw "Required command '$Name' was not found. Install OpenSSH client tooling on Windows first."
    }
}

function Invoke-FrontendBuild {
    param([Parameter(Mandatory = $true)][string]$SourceRoot)

    $packageJson = Join-Path $SourceRoot "package.json"
    if (-not (Test-Path $packageJson)) {
        return
    }

    Require-Command -Name "npm"

    Push-Location $SourceRoot
    try {
        if (Test-Path "package-lock.json") {
            & npm ci
            if ($LASTEXITCODE -ne 0) {
                throw "npm ci failed."
            }
        }
        else {
            & npm install
            if ($LASTEXITCODE -ne 0) {
                throw "npm install failed."
            }
        }

        & npm run build
        if ($LASTEXITCODE -ne 0) {
            throw "npm run build failed."
        }
    }
    finally {
        Pop-Location
    }
}

function New-StagingArchive {
    param([Parameter(Mandatory = $true)][string]$SourceRoot)

    $stagingRoot = Join-Path ([System.IO.Path]::GetTempPath()) ("openspoofen-stage-" + [guid]::NewGuid().ToString("N"))
    $contentRoot = Join-Path $stagingRoot "repo"
    $archivePath = Join-Path $stagingRoot "openspoofen.zip"

    New-Item -ItemType Directory -Path $contentRoot | Out-Null

    Get-ChildItem -Path $SourceRoot -Force | Where-Object {
        $excludeNames -notcontains $_.Name
    } | ForEach-Object {
        Copy-Item -Path $_.FullName -Destination $contentRoot -Recurse -Force
    }

    Compress-Archive -Path (Join-Path $contentRoot "*") -DestinationPath $archivePath -CompressionLevel Optimal

    return @{
        StagingRoot = $stagingRoot
        ArchivePath = $archivePath
    }
}

function Test-IsIpAddress {
    param([string]$Value)

    $parsedAddress = $null
    return [System.Net.IPAddress]::TryParse($Value, [ref]$parsedAddress)
}

function Add-HostCandidate {
    param(
        [Parameter(Mandatory = $true)]$Hosts,
        [string]$Value
    )

    if ([string]::IsNullOrWhiteSpace($Value)) {
        return
    }

    $normalized = $Value.Trim()
    if (-not $Hosts.Contains($normalized)) {
        $Hosts.Add($normalized) | Out-Null
    }
}

function Get-EnvValue {
    param(
        [Parameter(Mandatory = $true)][string]$Path,
        [Parameter(Mandatory = $true)][string]$Key
    )

    foreach ($rawLine in Get-Content -Path $Path -ErrorAction SilentlyContinue) {
        $line = $rawLine.Trim()
        if (-not $line -or $line.StartsWith("#") -or -not $line.Contains("=")) {
            continue
        }

        $entryKey, $entryValue = $line.Split("=", 2)
        if ($entryKey.Trim() -eq $Key) {
            return $entryValue.Trim().Trim([char]34).Trim([char]39)
        }
    }

    return $null
}

function Resolve-DeploymentHosts {
    param(
        [Parameter(Mandatory = $true)][string]$PrimaryHost,
        [string]$EnvFilePath
    )

    $hosts = New-Object System.Collections.Generic.List[string]

    Add-HostCandidate -Hosts $hosts -Value $PrimaryHost

    if (-not (Test-IsIpAddress -Value $PrimaryHost)) {
        if ($PrimaryHost.Contains(".")) {
            if ($PrimaryHost.EndsWith(".local")) {
                Add-HostCandidate -Hosts $hosts -Value $PrimaryHost.Substring(0, $PrimaryHost.Length - 6)
            }
        }
        else {
            Add-HostCandidate -Hosts $hosts -Value "$PrimaryHost.local"
        }
    }

    if ($EnvFilePath -and (Test-Path $EnvFilePath)) {
        $deviceHostName = Get-EnvValue -Path $EnvFilePath -Key "RP_DEVICE_HOSTNAME"
        if ($deviceHostName) {
            Add-HostCandidate -Hosts $hosts -Value $deviceHostName
            if (-not (Test-IsIpAddress -Value $deviceHostName)) {
                Add-HostCandidate -Hosts $hosts -Value "$deviceHostName.local"
            }
        }
    }

    foreach ($candidate in @($hosts.ToArray())) {
        if (Test-IsIpAddress -Value $candidate) {
            continue
        }

        try {
            [System.Net.Dns]::GetHostAddresses($candidate) |
                Where-Object { $_.AddressFamily -eq [System.Net.Sockets.AddressFamily]::InterNetwork } |
                ForEach-Object {
                    Add-HostCandidate -Hosts $hosts -Value $_.IPAddressToString
                }
        }
        catch {
        }
    }

    return $hosts.ToArray()
}

function Test-IsTransientSshFailure {
    param([string]$ErrorText)

    if ([string]::IsNullOrWhiteSpace($ErrorText)) {
        return $false
    }

    return $ErrorText -match "No route to host|Could not resolve hostname|Name or service not known|Temporary failure in name resolution|Connection refused|Connection timed out|Operation timed out|Connection reset by peer|Connection closed by remote host|Connection closed by .* port 22"
}

function Invoke-WithHostFallback {
    param(
        [Parameter(Mandatory = $true)][scriptblock]$Operation,
        [Parameter(Mandatory = $true)][string]$CommandLabel,
        [int]$RetrySeconds = 45
    )

    $deadline = (Get-Date).AddSeconds($RetrySeconds)
    $lastFailure = $null
    $announcedRetry = $false

    while ($true) {
        foreach ($targetHost in $script:DeploymentHosts) {
            $output = & $Operation $targetHost 2>&1
            $exitCode = $LASTEXITCODE
            if ($exitCode -eq 0) {
                if ($script:ActiveHostName -ne $targetHost) {
                    Write-Host "Using deployment host $targetHost"
                }

                $script:ActiveHostName = $targetHost
                return $output
            }

            $lastFailure = ($output | Out-String).Trim()
            if (-not (Test-IsTransientSshFailure -ErrorText $lastFailure)) {
                throw "$CommandLabel failed on ${targetHost}: $lastFailure"
            }
        }

        if ((Get-Date) -ge $deadline) {
            break
        }

        if (-not $announcedRetry) {
            Write-Warning "Transient SSH reachability failure detected. Retrying across: $([string]::Join(', ', $script:DeploymentHosts))"
            $announcedRetry = $true
        }

        Start-Sleep -Seconds 3
    }

    throw "$CommandLabel failed after retrying $([string]::Join(', ', $script:DeploymentHosts)). Last error: $lastFailure"
}

function Invoke-Ssh {
    param([Parameter(Mandatory = $true)][string]$CommandText)

    Invoke-WithHostFallback -CommandLabel "SSH command" -Operation {
        param($TargetHost)
        & ssh -o StrictHostKeyChecking=accept-new -o ConnectTimeout=5 -p $SshPort "$UserName@$TargetHost" $CommandText
    } | Out-Null
}

function Test-SshCommand {
    param([Parameter(Mandatory = $true)][string]$CommandText)

    foreach ($targetHost in $script:DeploymentHosts) {
        & ssh -o StrictHostKeyChecking=accept-new -o ConnectTimeout=5 -p $SshPort "$UserName@$targetHost" $CommandText *> $null
        if ($LASTEXITCODE -eq 0) {
            $script:ActiveHostName = $targetHost
            return $true
        }
    }

    return $false
}

function Wait-ForSshReady {
    param([int]$TimeoutSeconds = 240)

    $deadline = (Get-Date).AddSeconds($TimeoutSeconds)
    while ((Get-Date) -lt $deadline) {
        if (Test-SshCommand -CommandText "true") {
            return
        }
        Start-Sleep -Seconds 3
    }

    throw "Timed out waiting for SSH on $HostName"
}

function Wait-ForWebHealth {
    param([int]$TimeoutSeconds = 180)

    $deadline = (Get-Date).AddSeconds($TimeoutSeconds)
    while ((Get-Date) -lt $deadline) {
        if (Test-SshCommand -CommandText "curl -fsS http://127.0.0.1:8080/healthz >/dev/null") {
            return
        }
        Start-Sleep -Seconds 3
    }

    throw "Timed out waiting for openspoofen-web.service health on $HostName"
}

function Invoke-RemoteReboot {
    param([int]$TimeoutSeconds = 300)

    Invoke-WithHostFallback -CommandLabel "Remote reboot request" -Operation {
        param($TargetHost)
        & ssh -o StrictHostKeyChecking=accept-new -o ConnectTimeout=5 -p $SshPort "$UserName@$TargetHost" "sudo nohup bash -lc 'sleep 2; systemctl reboot' >/dev/null 2>&1 &"
    } | Out-Null

    Start-Sleep -Seconds 5
    $deadline = (Get-Date).AddSeconds([Math]::Min($TimeoutSeconds, 90))
    $sawOffline = $false
    while ((Get-Date) -lt $deadline) {
        if (-not (Test-SshCommand -CommandText "true")) {
            $sawOffline = $true
            break
        }
        Start-Sleep -Seconds 2
    }

    if (-not $sawOffline) {
        Write-Warning "Did not observe the host go offline after requesting reboot; continuing to wait for SSH availability."
    }

    Wait-ForSshReady -TimeoutSeconds $TimeoutSeconds
}

function Copy-ToPi {
    param(
        [Parameter(Mandatory = $true)][string]$LocalPath,
        [Parameter(Mandatory = $true)][string]$RemotePath
    )

    Invoke-WithHostFallback -CommandLabel "SCP upload" -Operation {
        param($TargetHost)
        & scp -o StrictHostKeyChecking=accept-new -o ConnectTimeout=5 -P $SshPort $LocalPath "${UserName}@${TargetHost}:${RemotePath}"
    } | Out-Null
}

Require-Command -Name "ssh"
Require-Command -Name "scp"

$script:DeploymentHosts = Resolve-DeploymentHosts -PrimaryHost $HostName -EnvFilePath $LocalEnvFile
$script:ActiveHostName = $script:DeploymentHosts[0]

if (-not (Test-Path (Join-Path $ProjectRoot "bootstrap\install.sh"))) {
    throw "ProjectRoot does not look like this repository: $ProjectRoot"
}

Invoke-FrontendBuild -SourceRoot $ProjectRoot

$archive = New-StagingArchive -SourceRoot $ProjectRoot

try {
    $remoteArchive = "$RemoteTempDir/package.zip"
    $remoteSourceDir = "$RemoteTempDir/src"

    Invoke-Ssh "mkdir -p '$RemoteTempDir'"
    Copy-ToPi -LocalPath $archive.ArchivePath -RemotePath $remoteArchive

    if ($LocalEnvFile) {
        if (-not (Test-Path $LocalEnvFile)) {
            throw "Local env file not found: $LocalEnvFile"
        }
        Copy-ToPi -LocalPath (Resolve-Path $LocalEnvFile).Path -RemotePath "$RemoteTempDir/openspoofen.env"
        Invoke-Ssh "sudo install -d -m 755 '/etc/openspoofen' && sudo install -m 600 '$RemoteTempDir/openspoofen.env' '/etc/openspoofen/openspoofen.env'"
    }

    if ($LocalWifiEnvFile) {
        if (-not (Test-Path $LocalWifiEnvFile)) {
            throw "Local Wi-Fi env file not found: $LocalWifiEnvFile"
        }
        Copy-ToPi -LocalPath (Resolve-Path $LocalWifiEnvFile).Path -RemotePath "$RemoteTempDir/wifi-uplink.local.env"
    }

    if ($LocalTvModeEnvFile) {
        if (-not (Test-Path $LocalTvModeEnvFile)) {
            throw "Local TV mode env file not found: $LocalTvModeEnvFile"
        }
        Copy-ToPi -LocalPath (Resolve-Path $LocalTvModeEnvFile).Path -RemotePath "$RemoteTempDir/tv-ethernet-mode.env"
    }

    Invoke-Ssh "rm -rf '$remoteSourceDir' && mkdir -p '$remoteSourceDir' && python3 -m zipfile -e '$remoteArchive' '$remoteSourceDir'"
    Invoke-Ssh "cd '$remoteSourceDir' && chmod +x bootstrap/install.sh && sudo bash bootstrap/install.sh"

    if ($TunePiOs) {
        Write-Host "Applying Pi OS performance tuning ..."
        Invoke-Ssh "sudo bash '$RemoteTempDir/src/bootstrap/tune-pi-os.sh'"
    }

    if ($LocalEnvFile) {
        Invoke-Ssh "sudo install -m 600 '$RemoteTempDir/openspoofen.env' '/etc/openspoofen/openspoofen.env' && sudo systemctl restart openspoofen-web.service"
    }

    if ($LocalWifiEnvFile) {
        Invoke-Ssh "sudo install -d -m 700 '/etc/openspoofen/secrets' && sudo install -m 600 '$RemoteTempDir/wifi-uplink.local.env' '/etc/openspoofen/secrets/wifi-uplink.local.env' && sudo systemctl restart openspoofen-wifi-uplink.service"
    }

    if ($LocalTvModeEnvFile) {
        Invoke-Ssh "sudo install -d -m 755 '/etc/openspoofen' && sudo install -m 600 '$RemoteTempDir/tv-ethernet-mode.env' '/etc/openspoofen/tv-ethernet-mode.env' && sudo systemctl restart openspoofen-tv-lan.service && sudo systemctl restart openspoofen-web.service"
    }

    if ($RebootAfterInstall) {
        Invoke-RemoteReboot
    }

    Wait-ForWebHealth

    Write-Host "Deployment completed."
    Write-Host "Open http://$script:ActiveHostName`:8080 or https://$script:ActiveHostName`:8080 if RP_ENABLE_HTTPS=true."
    if ($RebootAfterInstall) {
        Write-Host "Remote host rebooted after deployment and passed the post-reboot web health check."
    }
    if ($LocalWifiEnvFile) {
        Write-Host "Installed Wi-Fi uplink env to /etc/openspoofen/secrets/wifi-uplink.local.env"
    }
    if ($LocalTvModeEnvFile) {
        Write-Host "Installed TV LAN env to /etc/openspoofen/tv-ethernet-mode.env"
    }
}
finally {
    if ($archive -and (Test-Path $archive.StagingRoot)) {
        Remove-Item -Path $archive.StagingRoot -Recurse -Force
    }

    try {
        Invoke-Ssh "rm -rf '$RemoteTempDir'"
    }
    catch {
        Write-Warning "Remote temp cleanup failed: $($_.Exception.Message)"
    }
}