# One-click Windows deployment script for Self-Healing Cloud Deployment Platform.
# Runs natively in PowerShell (no WSL/bash required).
#
# Usage:
#   powershell -NoProfile -ExecutionPolicy Bypass -File .\scripts\deploy-windows.ps1

$ErrorActionPreference = "Stop"
$ProgressPreference = "SilentlyContinue"

function Write-Info {
    param([string]$Message)
    Write-Host "[INFO] $Message" -ForegroundColor Cyan
}

function Write-Success {
    param([string]$Message)
    Write-Host "[SUCCESS] $Message" -ForegroundColor Green
}

function Invoke-Native {
    param(
        [Parameter(Mandatory = $true)][string]$File,
        [Parameter(Mandatory = $false)][string[]]$Arguments = @(),
        [Parameter(Mandatory = $false)][switch]$AllowFailure
    )

    & $File @Arguments
    $exitCode = $LASTEXITCODE
    if (-not $AllowFailure -and $exitCode -ne 0) {
        throw "Command failed: $File $($Arguments -join ' ') (exit code: $exitCode)"
    }
    return $exitCode
}

function Ensure-Command {
    param(
        [Parameter(Mandatory = $true)][string]$CommandName,
        [Parameter(Mandatory = $true)][string]$WingetId
    )

    if (Get-Command $CommandName -ErrorAction SilentlyContinue) {
        return
    }

    Write-Info "$CommandName not found. Installing via winget: $WingetId"
    try {
        Invoke-Native -File "winget" -Arguments @(
            "install", "-e", "--id", $WingetId, "--scope", "user",
            "--accept-source-agreements", "--accept-package-agreements"
        )
    }
    catch {
        Invoke-Native -File "winget" -Arguments @(
            "install", "-e", "--id", $WingetId,
            "--accept-source-agreements", "--accept-package-agreements"
        )
    }

    $env:Path = [Environment]::GetEnvironmentVariable("Path", "Machine") + ";" +
                [Environment]::GetEnvironmentVariable("Path", "User")

    if (-not (Get-Command $CommandName -ErrorAction SilentlyContinue)) {
        throw "Required command '$CommandName' is still missing. Open PowerShell as Administrator and rerun."
    }
}

function Test-DockerEngine {
    if (-not (Get-Command docker -ErrorAction SilentlyContinue)) {
        return $false
    }
    Invoke-Native -File "docker" -Arguments @("info") -AllowFailure | Out-Null
    return ($LASTEXITCODE -eq 0)
}

function Test-KubeConnectivity {
    Invoke-Native -File "kubectl" -Arguments @("get", "nodes") -AllowFailure | Out-Null
    return ($LASTEXITCODE -eq 0)
}

$ProjectRoot = Split-Path -Parent $PSScriptRoot
Set-Location $ProjectRoot

$Namespace = "self-healing-platform"
$LocalPort = 50080
$Profile = "minikube"
$ImageTag = "self-healing-api:2.0.0"

Write-Info "Project root: $ProjectRoot"
Write-Info "Validating prerequisites..."
Ensure-Command -CommandName "minikube" -WingetId "Kubernetes.minikube"
Ensure-Command -CommandName "kubectl" -WingetId "Kubernetes.kubectl"

if (-not (Test-KubeConnectivity)) {
    Write-Info "Kubernetes cluster not reachable. Starting Minikube..."

    if (Get-Command podman -ErrorAction SilentlyContinue) {
        Invoke-Native -File "podman" -Arguments @("machine", "inspect") -AllowFailure | Out-Null
        if ($LASTEXITCODE -ne 0) {
            Invoke-Native -File "podman" -Arguments @("machine", "init")
        }
        Invoke-Native -File "podman" -Arguments @("machine", "start") -AllowFailure | Out-Null
        Invoke-Native -File "minikube" -Arguments @("start", "-p", $Profile, "--driver=podman", "--cpus=2", "--memory=4096")
    }
    elseif (Test-DockerEngine) {
        Invoke-Native -File "minikube" -Arguments @("start", "-p", $Profile, "--driver=docker", "--cpus=2", "--memory=4096")
    }
    else {
        throw "No running container driver found (Podman or Docker). Start Docker Desktop or Podman, then rerun."
    }
}
else {
    Write-Info "Kubernetes cluster is reachable. Continuing deployment."
}

Write-Info "Setting kubectl context..."
Invoke-Native -File "kubectl" -Arguments @("config", "use-context", $Profile) -AllowFailure | Out-Null

Write-Info "Enabling required Minikube addons..."
Invoke-Native -File "minikube" -Arguments @("addons", "enable", "ingress", "-p", $Profile) -AllowFailure | Out-Null
if ($LASTEXITCODE -ne 0) {
    Invoke-Native -File "minikube" -Arguments @("addons", "enable", "ingress")
}
Invoke-Native -File "minikube" -Arguments @("addons", "enable", "metrics-server", "-p", $Profile) -AllowFailure | Out-Null
if ($LASTEXITCODE -ne 0) {
    Invoke-Native -File "minikube" -Arguments @("addons", "enable", "metrics-server")
}

Write-Info "Building image $ImageTag in Minikube runtime..."
Invoke-Native -File "minikube" -Arguments @("image", "build", "-p", $Profile, "-t", $ImageTag, ".") -AllowFailure | Out-Null
if ($LASTEXITCODE -ne 0) {
    Invoke-Native -File "minikube" -Arguments @("image", "build", "-t", $ImageTag, ".")
}

Write-Info "Applying Kubernetes manifests..."
Invoke-Native -File "kubectl" -Arguments @("apply", "-f", ".\kubernetes\namespace.yaml")
Invoke-Native -File "kubectl" -Arguments @("apply", "-f", ".\kubernetes\deployment.yaml")
Invoke-Native -File "kubectl" -Arguments @("apply", "-f", ".\kubernetes\service.yaml")
Invoke-Native -File "kubectl" -Arguments @("apply", "-f", ".\kubernetes\ingress.yaml")

Write-Info "Restarting deployment..."
Invoke-Native -File "kubectl" -Arguments @("rollout", "restart", "deployment/self-healing-api", "-n", $Namespace)

Write-Info "Waiting for deployment rollout..."
try {
    Invoke-Native -File "kubectl" -Arguments @("rollout", "status", "deployment/self-healing-api", "-n", $Namespace, "--timeout=300s")
}
catch {
    Write-Host "[ERROR] Rollout failed. Diagnostics:" -ForegroundColor Red
    Invoke-Native -File "kubectl" -Arguments @("get", "pods", "-n", $Namespace, "-o", "wide") -AllowFailure | Out-Null
    Invoke-Native -File "kubectl" -Arguments @("describe", "deployment", "self-healing-api", "-n", $Namespace) -AllowFailure | Out-Null
    throw
}

Write-Info "Stopping old kubectl port-forward processes (if any)..."
Get-Process kubectl -ErrorAction SilentlyContinue | Stop-Process -Force -ErrorAction SilentlyContinue

Write-Info "Starting background port-forward on localhost:$LocalPort ..."
$portForwardOut = Join-Path $env:TEMP "self-healing-portforward.out.log"
$portForwardErr = Join-Path $env:TEMP "self-healing-portforward.err.log"

Start-Process `
    -FilePath "kubectl" `
    -ArgumentList @("port-forward", "-n", $Namespace, "service/self-healing-api-service", "$LocalPort`:80", "--address", "127.0.0.1") `
    -WindowStyle Hidden `
    -RedirectStandardOutput $portForwardOut `
    -RedirectStandardError $portForwardErr | Out-Null

Write-Info "Waiting for application on http://127.0.0.1:$LocalPort ..."
$reachable = $false
for ($i = 1; $i -le 40; $i++) {
    Start-Sleep -Seconds 2
    $statusCode = (curl.exe -s -o NUL -w "%{http_code}" "http://127.0.0.1:$LocalPort/health")
    if ($statusCode -eq "200") {
        $reachable = $true
        break
    }
}

if ($reachable) {
    Write-Success "Deployment completed. Opening dashboard in browser..."
    Start-Process "http://127.0.0.1:$LocalPort/"
}
else {
    Write-Host "[WARN] App is not reachable yet on localhost:$LocalPort." -ForegroundColor Yellow
    Write-Host "[WARN] Port-forward logs:" -ForegroundColor Yellow
    Write-Host "       $portForwardOut"
    Write-Host "       $portForwardErr"
}

Write-Host ""
Write-Host "Self-healing demo command:" -ForegroundColor Magenta
Write-Host "curl.exe -X POST http://127.0.0.1:$LocalPort/crash"
Write-Host "kubectl get pods -n $Namespace -w"
Write-Host "Stop background forwarding: Get-Process kubectl | Stop-Process -Force"
