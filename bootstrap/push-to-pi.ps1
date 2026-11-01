[CmdletBinding()]
param(
    [Parameter(Mandatory = $true)]
    [string]$HostName,

    [string]$UserName = "pi",

    [int]$SshPort = 22,

    [switch]$PythonOnly,

    [switch]$FrontendOnly,

    [switch]$TunePiOs
)

$ErrorActionPreference = "Stop"
$RemoteAppRoot = "/opt/openspoofen"
$RemoteStaticDir = "$RemoteAppRoot/src/openspoofen/static"

$script:ActiveHostName = $HostName

function Invoke-Ssh {
    param([string]$CommandText)
    & ssh -o StrictHostKeyChecking=accept-new -o ConnectTimeout=5 -p $SshPort "$UserName@$script:ActiveHostName" $CommandText
}

function Copy-ToPi {
    param([string]$LocalPath, [string]$RemotePath)
    & scp -o StrictHostKeyChecking=accept-new -o ConnectTimeout=5 -P $SshPort $LocalPath "${UserName}@${script:ActiveHostName}:${RemotePath}"
}

Write-Host "Pushing to $HostName ..."

if (-not $PythonOnly) {
    Write-Host "[frontend] Building ..."
    Push-Location (Join-Path $PSScriptRoot "..")
    try {
        & npm run build
        if ($LASTEXITCODE -ne 0) {
            throw "npm run build failed."
        }
    }
    finally {
        Pop-Location
    }

    Write-Host "[frontend] Uploading static assets ..."
    $staticFiles = Get-ChildItem -Path (Join-Path $PSScriptRoot ".." "src" "openspoofen" "static") -Recurse -File | Where-Object {
        $_.Name -match "dashboard-app\.(js|css)$" -or $_.Name -eq "dashboard-app.css"
    }
    foreach ($file in $staticFiles) {
        $remotePath = "$RemoteStaticDir/$($file.Name)"
        Copy-ToPi -LocalPath $file.FullName -RemotePath $remotePath
        Write-Host "  $($file.Name) -> $RemoteStaticDir/"
    }
}

if (-not $FrontendOnly) {
    Write-Host "[python] Uploading changed source files ..."
    $pythonDir = Join-Path $PSScriptRoot ".." "src" "openspoofen"
    $pythonFiles = Get-ChildItem -Path $pythonDir -Recurse -File -Include "*.py" | Where-Object {
        $_.FullName -notmatch "__pycache__|\.egg-info"
    }
    foreach ($file in $pythonFiles) {
        $relativePath = $file.FullName.Substring($pythonDir.Length + 1)
        $remotePath = "$RemoteAppRoot/src/openspoofen/$relativePath"
        $remoteDir = Split-Path $remotePath -Parent
        Invoke-Ssh "mkdir -p '$remoteDir'"
        Copy-ToPi -LocalPath $file.FullName -RemotePath $remotePath
        Write-Host "  $relativePath"
    }
}

Write-Host "[service] Restarting web service ..."
Invoke-Ssh "sudo systemctl restart openspoofen-web.service"

if ($TunePiOs) {
    Write-Host "[os-tune] Applying Pi OS performance tuning ..."
    $remoteTunePath = "$RemoteAppRoot/bootstrap/tune-pi-os.sh"
    Copy-ToPi -LocalPath (Join-Path $PSScriptRoot "tune-pi-os.sh") -RemotePath $remoteTunePath
    Invoke-Ssh "sudo bash '$remoteTunePath'"
}
Write-Host "Done. Open http://$HostName`:8080"
