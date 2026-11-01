[CmdletBinding()]
param(
    [string]$HostName,
    [string]$UserName,
    [string]$SshIdentityFile,
    [switch]$SkipBuild,
    [switch]$SkipTune,
    [switch]$NoReboot
)

$ErrorActionPreference = "Stop"
$ScriptRoot = $PSScriptRoot
$ProjectRoot = (Resolve-Path (Join-Path $ScriptRoot "..")).Path

# Auto-detect from bootstrap secrets

# Credentials come from Infisical (Personal:/openspoofen): infisical run --env dev --path /openspoofen -- ./bootstrap/quick-deploy.ps1
if (-not $PSBoundParameters.ContainsKey("HostName") -and $env:PI_BOOTSTRAP_HOSTNAME) { $HostName = $env:PI_BOOTSTRAP_HOSTNAME }
if (-not $PSBoundParameters.ContainsKey("UserName") -and $env:PI_BOOTSTRAP_USERNAME) { $UserName = $env:PI_BOOTSTRAP_USERNAME }

if (-not $HostName) {
    $HostName = "openspoofen.local"
    Write-Host "[quick-deploy] No hostname found; using default: $HostName"
}
if (-not $UserName) {
    $UserName = "proxyadmin"
    Write-Host "[quick-deploy] No username found; using default: $UserName"
}

Write-Host "[quick-deploy] Target: $UserName@$HostName"

# SSH identity

$sshArgs = @()
if ($SshIdentityFile) {
    if (-not (Test-Path $SshIdentityFile)) {
        Write-Warning "SSH identity file not found: $SshIdentityFile"
    } else {
        $sshArgs = @("-i", (Resolve-Path $SshIdentityFile).Path)
        Write-Host "[quick-deploy] Using SSH identity: $SshIdentityFile"
    }
} else {
    $defaultKey = Join-Path (Join-Path $HOME ".ssh") "openspoofen-deploy"
    if (Test-Path $defaultKey) {
        $sshArgs = @("-i", $defaultKey)
        Write-Host "[quick-deploy] Using auto-detected SSH key: $defaultKey"
    }
}

# Test SSH

Write-Host "[quick-deploy] Testing SSH reachability ..."
$sshResult = & ssh @sshArgs -o StrictHostKeyChecking=accept-new -o ConnectTimeout=5 -o BatchMode=yes "$UserName@$HostName" "hostname" 2>&1
if ($LASTEXITCODE -ne 0) {
    Write-Warning "SSH test failed ($sshResult). The deploy script will retry with fallback host resolution."
} else {
    Write-Host "[quick-deploy] SSH OK: $sshResult"
}

# Build frontend (unless skipped)

if (-not $SkipBuild) {
    Write-Host "[quick-deploy] Building frontend ..."
    Push-Location $ProjectRoot
    try {
        & npm run build
        if ($LASTEXITCODE -ne 0) { throw "npm run build failed." }
    } finally { Pop-Location }
}

# Deploy

$deployScript = Join-Path $ScriptRoot "deploy-to-pi.ps1"
$envExample = Join-Path (Join-Path $ProjectRoot "configs") "openspoofen.env.example"
$wifiExample = Join-Path (Join-Path $ProjectRoot "configs") "wifi-uplink.env.example"
$tvExample = Join-Path (Join-Path $ProjectRoot "configs") "tv-ethernet-mode.env.example"

Write-Host "[quick-deploy] Running deploy-to-pi.ps1 ..."

$psArgs = @()
$psArgs += "& '$deployScript'"
$psArgs += "-HostName '$HostName'"
$psArgs += "-UserName '$UserName'"
$psArgs += "-LocalEnvFile '$envExample'"
$psArgs += "-LocalWifiEnvFile '$wifiExample'"
$psArgs += "-LocalTvModeEnvFile '$tvExample'"
if (-not $NoReboot) { $psArgs += "-RebootAfterInstall" }
if (-not $SkipTune) { $psArgs += "-TunePiOs" }

$cmd = $psArgs -join " "
Write-Host "  $cmd"
Invoke-Expression $cmd

# NordVPN secrets (if available)

$NordVpnSecretFile = $null
if ($env:NORDVPN_ACCESS_TOKEN) {
    $NordVpnSecretFile = Join-Path ([IO.Path]::GetTempPath()) "nordvpn.local.env"
    Set-Content -Path $NordVpnSecretFile -Value "NORDVPN_ACCESS_TOKEN=$($env:NORDVPN_ACCESS_TOKEN)" -NoNewline
}
if ($NordVpnSecretFile) {
    Write-Host "[quick-deploy] Deploying NordVPN secrets ..."
    $remoteSecretDir = "/etc/openspoofen/secrets"
    & ssh @sshArgs -o StrictHostKeyChecking=accept-new -o ConnectTimeout=5 "$UserName@$HostName" "sudo mkdir -p '$remoteSecretDir'" 2>&1 | Out-Null
    & scp @sshArgs -o StrictHostKeyChecking=accept-new -o ConnectTimeout=5 (Resolve-Path $NordVpnSecretFile).Path "${UserName}@${HostName}:${remoteSecretDir}/nordvpn.local.env"
    if ($LASTEXITCODE -eq 0) {
        & ssh @sshArgs -o StrictHostKeyChecking=accept-new -o ConnectTimeout=5 "$UserName@$HostName" "sudo systemctl restart openspoofen-nordvpn-bootstrap.service || true; sudo systemctl restart openspoofen-web.service" 2>&1 | Out-Null
        Write-Host "[quick-deploy] NordVPN secrets deployed and services restarted."
    } else {
        Write-Warning "[quick-deploy] NordVPN secret upload failed. Deploy the file manually."
    }
    if ($env:NORDVPN_ACCESS_TOKEN) { Remove-Item $NordVpnSecretFile -Force -ErrorAction SilentlyContinue }
} else {
    Write-Host "[quick-deploy] NORDVPN_ACCESS_TOKEN not in environment -- skipped."
}

Write-Host "[quick-deploy] Done."
