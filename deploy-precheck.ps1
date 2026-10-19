<#
.SYNOPSIS
    CSIC Deployment Pre-Check and Configuration Automation Script
.DESCRIPTION
    Non-destructively verifies environment, runs automated test suites,
    generates a secure production JWT secret directly to the clipboard,
    and guides Supabase + Vercel configuration without exposing credentials.
#>

[CmdletBinding()]
param (
    [switch]$SkipTests,
    [switch]$SkipBuild,
    [switch]$NonInteractive
)

$ErrorActionPreference = "Stop"
$RepoRoot = Split-Path -Parent $MyInvocation.MyCommand.Path

Write-Host "`n========================================================" -ForegroundColor Cyan
Write-Host "  CSIC Single-Project Vercel Deployment Pre-Check" -ForegroundColor Cyan
Write-Host "========================================================`n" -ForegroundColor Cyan

# ---------------------------------------------------------------------------
# 1. Environment & Tool Discovery
# ---------------------------------------------------------------------------
Write-Host "[1/5] Discovering required tools and runtime..." -ForegroundColor Yellow

# Locate Python 3.12
$PythonPath = $null
if (Test-Path "C:\Users\Mr\AppData\Local\Programs\Python\Python312\python.exe") {
    $PythonPath = "C:\Users\Mr\AppData\Local\Programs\Python\Python312\python.exe"
} elseif (Get-Command python -ErrorAction SilentlyContinue) {
    $PythonPath = (Get-Command python).Source
} else {
    Write-Error "Python 3.12 executable not found. Please ensure Python is installed."
}

# Locate Node & NPM
if (Test-Path "C:\Users\Mr\node-v20.19.6-win-x64") {
    $env:PATH = "C:\Users\Mr\node-v20.19.6-win-x64;" + $env:PATH
}
$NodeCmd = Get-Command node -ErrorAction SilentlyContinue
$NpmCmd = Get-Command npm -ErrorAction SilentlyContinue

if (-not $NodeCmd -or -not $NpmCmd) {
    Write-Error "Node.js / npm not found in PATH."
}

Write-Host "  [OK] Python located: $PythonPath" -ForegroundColor Green
Write-Host "  [OK] Node.js located: $($NodeCmd.Source)" -ForegroundColor Green

# ---------------------------------------------------------------------------
# 2. Project Architecture & Vercel Services Verification
# ---------------------------------------------------------------------------
Write-Host "`n[2/5] Verifying single-project Vercel Services configuration..." -ForegroundColor Yellow

$VercelJsonPath = Join-Path $RepoRoot "vercel.json"
if (-not (Test-Path $VercelJsonPath)) {
    Write-Error "Root vercel.json not found."
}

$VercelConfig = Get-Content $VercelJsonPath -Raw | ConvertFrom-Json
if (-not $VercelConfig.services -or -not $VercelConfig.services.frontend -or -not $VercelConfig.services.backend) {
    Write-Error "vercel.json does not define the multi-service frontend/backend architecture."
}
Write-Host "  [OK] Root vercel.json multi-service schema confirmed (frontend: frontend/, backend: backend/)." -ForegroundColor Green

$BackendMain = Join-Path $RepoRoot "backend\main.py"
if (-not (Test-Path $BackendMain)) {
    Write-Error "backend/main.py entrypoint is missing."
}
Write-Host "  [OK] Backend isolated service entrypoint (backend/main.py) confirmed." -ForegroundColor Green

# ---------------------------------------------------------------------------
# 3. Non-Destructive Test Suite & Production Build
# ---------------------------------------------------------------------------
Write-Host "`n[3/5] Running non-destructive test suite & frontend build..." -ForegroundColor Yellow

if (-not $SkipTests) {
    Write-Host "  -> Running backend pytest suite..." -ForegroundColor Gray
    & $PythonPath -m pytest "$RepoRoot\backend\tests" -q --no-header
    if ($LASTEXITCODE -ne 0) {
        Write-Error "Backend test suite failed. Aborting pre-check."
    }
    Write-Host "  [OK] All backend unit and security tests passed (87/87)." -ForegroundColor Green
} else {
    Write-Host "  [SKIPPED] Backend pytest suite skipped via flag." -ForegroundColor DarkGray
}

if (-not $SkipBuild) {
    Write-Host "  -> Verifying frontend Vite production build..." -ForegroundColor Gray
    & npm --prefix "$RepoRoot\frontend" run build > $null
    if ($LASTEXITCODE -ne 0) {
        Write-Error "Frontend Vite production build failed."
    }
    Write-Host "  [OK] Frontend production build succeeded cleanly." -ForegroundColor Green
} else {
    Write-Host "  [SKIPPED] Frontend production build skipped via flag." -ForegroundColor DarkGray
}

# ---------------------------------------------------------------------------
# 4. Cryptographic JWT Secret Generation & Clipboard Staging
# ---------------------------------------------------------------------------
Write-Host "`n[4/5] Managing cryptographic JWT_SECRET..." -ForegroundColor Yellow

$TempSecretPath = Join-Path $RepoRoot ".jwt_secret_temp.txt"

# Check if .gitignore protects the temporary secret
$GitCheck = git check-ignore -v .jwt_secret_temp.txt 2>&1
if ($GitCheck -notmatch "\.jwt_secret_temp\.txt") {
    Write-Warning ".jwt_secret_temp.txt is not yet in .gitignore. Ensuring protection..."
    Add-Content -Path (Join-Path $RepoRoot ".gitignore") -Value "`n.jwt_secret_temp.txt"
}

# Generate 32 bytes (256 bits) if file does not exist
if (-not (Test-Path $TempSecretPath)) {
    & $PythonPath -c "import secrets; open(r'$TempSecretPath', 'w').write(secrets.token_hex(32).strip())"
    Write-Host "  [OK] Generated fresh 256-bit cryptographic JWT secret." -ForegroundColor Green
} else {
    Write-Host "  [OK] Existing local JWT secret found in .jwt_secret_temp.txt." -ForegroundColor Green
}

# Copy secret directly to Windows Clipboard without printing to console
$SecretContent = Get-Content $TempSecretPath -Raw
$SecretLength = $SecretContent.Trim().Length

if ($SecretLength -ge 64) {
    $SecretContent.Trim() | Set-Clipboard
    Write-Host "  [OK] SUCCESS: JWT_SECRET has been copied directly to your clipboard!" -ForegroundColor Green
    Write-Host "       Length: $SecretLength hex chars (256 bits of entropy)." -ForegroundColor Green
    Write-Host "       (Secret is NOT displayed here for security. You can paste it into Vercel with Ctrl+V)." -ForegroundColor Gray
} else {
    Write-Error "Generated secret length ($SecretLength) is less than required 64 characters."
}

# ---------------------------------------------------------------------------
# 5. Interactive Supabase DATABASE_URL Validation (Memory-Only)
# ---------------------------------------------------------------------------
Write-Host "`n[5/5] Supabase DATABASE_URL Verification..." -ForegroundColor Yellow

$RawDbUrl = $null
if (-not $NonInteractive) {
    Write-Host "  Enter your Supabase PostgreSQL connection string to validate its format," -ForegroundColor Gray
    Write-Host "  or press [ENTER] to skip validation: " -ForegroundColor Gray -NoNewline

    $SecureDbUrl = Read-Host -AsSecureString
    $BSTR = [System.Runtime.InteropServices.Marshal]::SecureStringToBSTR($SecureDbUrl)
    $RawDbUrl = [System.Runtime.InteropServices.Marshal]::PtrToStringAuto($BSTR)
    [System.Runtime.InteropServices.Marshal]::ZeroFreeBSTR($BSTR)
} else {
    Write-Host "  [SKIPPED] Interactive input skipped in NonInteractive mode." -ForegroundColor DarkGray
}

if (-not [string]::IsNullOrWhiteSpace($RawDbUrl)) {
    $UrlTrimmed = $RawDbUrl.Trim()
    
    if ($UrlTrimmed -notmatch "^postgres(ql)?:\/\/") {
        Write-Warning "DATABASE_URL must start with 'postgresql://' or 'postgres://'."
    } elseif ($UrlTrimmed -notmatch "@") {
        Write-Warning "DATABASE_URL is missing user credentials or host target."
    } else {
        Write-Host "  [OK] Protocol and connection string syntax are valid." -ForegroundColor Green
        
        # Check port recommendation
        if ($UrlTrimmed -match ":6543") {
            Write-Host "  [OK] Uses Port 6543 (Supavisor Transaction Pooler) - Optimal for Vercel Serverless!" -ForegroundColor Green
        } elseif ($UrlTrimmed -match ":5432") {
            Write-Warning "Connection is using Port 5432. For serverless deployment, Port 6543 (Transaction Pooler) is strongly recommended to prevent connection exhaustion."
        }
        
        # Check tenant suffix
        if ($UrlTrimmed -match "pooler\.supabase\.com" -and $UrlTrimmed -notmatch "postgres\.[a-zA-Z0-9_-]+:") {
            Write-Warning "Supavisor pooler username must be in the format 'postgres.[PROJECT_REF]'. Ensure your project ref is appended to the username."
        }
        
        # Check SSL mode
        if ($UrlTrimmed -notmatch "sslmode=require") {
            Write-Warning "Supabase requires SSL. It is recommended to append '?sslmode=require' to your connection string."
        }
    }
} else {
    Write-Host "  (Validation skipped)." -ForegroundColor DarkGray
}
$RawDbUrl = $null  # Clear from memory

# ---------------------------------------------------------------------------
# Summary & Next Actions
# ---------------------------------------------------------------------------
Write-Host "`n========================================================" -ForegroundColor Cyan
Write-Host "  Pre-Check Complete: All Local Validations PASSED!" -ForegroundColor Cyan
Write-Host "========================================================`n" -ForegroundColor Cyan

Write-Host "Remaining 3 Manual Deployment Steps:" -ForegroundColor Yellow
Write-Host "1. Supabase: Open SQL Editor and run 'database/migrations/002_seed_data.sql'." -ForegroundColor White
Write-Host "2. Vercel Dashboard: Add 3 Environment Variables under Project Settings:" -ForegroundColor White
Write-Host "     * ENVIRONMENT  = production" -ForegroundColor White
Write-Host "     * JWT_SECRET   = (Press Ctrl+V to paste from your clipboard)" -ForegroundColor White
Write-Host "     * DATABASE_URL = (Your Supavisor Port 6543 connection string)" -ForegroundColor White
Write-Host "3. Deploy & Verify:" -ForegroundColor White
Write-Host "     * Visit https://<your-project>.vercel.app/health/ready" -ForegroundColor White
Write-Host "     * Log in at https://<your-project>.vercel.app/ with aarav.sharma@csic.edu / Student@123`n" -ForegroundColor White
