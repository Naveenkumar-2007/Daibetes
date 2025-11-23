#!/usr/bin/env pwsh
# Azure Deployment Configuration Verifier
# This script checks if your deployment is properly configured

param(
    [string]$WebAppName = "diabetes-predictor-ai",
    [switch]$Fix
)

$ErrorActionPreference = "Stop"

Write-Host "`n🔍 Azure Deployment Configuration Checker" -ForegroundColor Cyan
Write-Host "=========================================`n" -ForegroundColor Cyan

$issues = @()
$warnings = @()

# Check 1: Verify Azure CLI is installed (optional but helpful)
Write-Host "Checking Azure CLI..." -NoNewline
try {
    $null = Get-Command az -ErrorAction Stop
    Write-Host " ✅" -ForegroundColor Green
} catch {
    Write-Host " ⚠️  Not installed (optional)" -ForegroundColor Yellow
    $warnings += "Azure CLI not installed. Install from: https://aka.ms/InstallAzureCLIDirect"
}

# Check 2: Verify required files exist
Write-Host "Checking required files..." -NoNewline
$requiredFiles = @(
    "flask_app.py",
    "requirements.txt",
    "startup.sh",
    ".github/workflows/azure-deploy.yml",
    ".deployment"
)

$missingFiles = @()
foreach ($file in $requiredFiles) {
    if (-not (Test-Path $file)) {
        $missingFiles += $file
    }
}

if ($missingFiles.Count -eq 0) {
    Write-Host " ✅" -ForegroundColor Green
} else {
    Write-Host " ❌" -ForegroundColor Red
    $issues += "Missing files: $($missingFiles -join ', ')"
}

# Check 3: Verify GitHub workflow configuration
Write-Host "Checking GitHub workflow..." -NoNewline
if (Test-Path ".github/workflows/azure-deploy.yml") {
    $workflow = Get-Content ".github/workflows/azure-deploy.yml" -Raw
    
    if ($workflow -match "AZURE_WEBAPP_NAME:\s*'?`"?$WebAppName'?`"?") {
        Write-Host " ✅" -ForegroundColor Green
    } else {
        Write-Host " ⚠️" -ForegroundColor Yellow
        $warnings += "Workflow may not have correct app name. Expected: $WebAppName"
    }
    
    if ($workflow -notmatch "slot-name:\s*'production'") {
        Write-Host "`n  ⚠️  Missing slot-name configuration" -ForegroundColor Yellow
    }
} else {
    Write-Host " ❌" -ForegroundColor Red
    $issues += "GitHub workflow file not found"
}

# Check 4: Verify frontend build
Write-Host "Checking frontend..." -NoNewline
if (Test-Path "frontend/package.json") {
    if (Test-Path "frontend/dist" -or Test-Path "frontend/build") {
        Write-Host " ✅ Built" -ForegroundColor Green
    } else {
        Write-Host " ⚠️  Not built" -ForegroundColor Yellow
        $warnings += "Frontend not built. Run: cd frontend && npm install && npm run build"
    }
} else {
    Write-Host " ❌" -ForegroundColor Red
    $issues += "Frontend package.json not found"
}

# Check 5: Verify startup.sh is executable (on Unix systems)
Write-Host "Checking startup.sh permissions..." -NoNewline
if (Test-Path "startup.sh") {
    # On Windows, we can't really check Unix permissions, but we verify it exists
    Write-Host " ✅" -ForegroundColor Green
} else {
    Write-Host " ❌" -ForegroundColor Red
    $issues += "startup.sh not found"
}

# Check 6: Verify publish profile
Write-Host "Checking publish profile files..." -NoNewline
$publishProfiles = @(Get-ChildItem -Filter "*publish-profile*.xml" -ErrorAction SilentlyContinue)
if ($publishProfiles.Count -gt 0) {
    Write-Host " ✅ Found $($publishProfiles.Count) profile(s)" -ForegroundColor Green
    
    # Parse the first publish profile to get app name
    $profileContent = Get-Content $publishProfiles[0].FullName -Raw
    if ($profileContent -match 'profileName="([^"]+)"') {
        $profileAppName = $matches[1] -replace ' - .*$', ''
        Write-Host "  📋 Profile app name: $profileAppName" -ForegroundColor Gray
        
        if ($profileAppName -ne $WebAppName) {
            Write-Host "  ⚠️  Profile app name doesn't match expected: $WebAppName" -ForegroundColor Yellow
            $warnings += "Publish profile app name mismatch. Expected: $WebAppName, Got: $profileAppName"
        }
    }
} else {
    Write-Host " ⚠️  No publish profile found" -ForegroundColor Yellow
    $warnings += "Download publish profile from Azure Portal and save it"
}

# Check 7: Check if logged into Azure
Write-Host "Checking Azure login status..." -NoNewline
try {
    $null = Get-Command az -ErrorAction Stop
    $accountInfo = az account show 2>&1 | ConvertFrom-Json -ErrorAction Stop
    Write-Host " ✅ Logged in as $($accountInfo.user.name)" -ForegroundColor Green
} catch {
    Write-Host " ⚠️  Not logged in" -ForegroundColor Yellow
    $warnings += "Not logged into Azure CLI. Run: az login"
}

# Summary
Write-Host "`n" -NoNewline
Write-Host "================================================" -ForegroundColor Cyan
Write-Host "Summary" -ForegroundColor Cyan
Write-Host "================================================`n" -ForegroundColor Cyan

if ($issues.Count -eq 0) {
    Write-Host "✅ No critical issues found!`n" -ForegroundColor Green
} else {
    Write-Host "❌ Critical Issues ($($issues.Count)):`n" -ForegroundColor Red
    foreach ($issue in $issues) {
        Write-Host "  • $issue" -ForegroundColor Red
    }
    Write-Host ""
}

if ($warnings.Count -gt 0) {
    Write-Host "⚠️  Warnings ($($warnings.Count)):`n" -ForegroundColor Yellow
    foreach ($warning in $warnings) {
        Write-Host "  • $warning" -ForegroundColor Yellow
    }
    Write-Host ""
}

# Next Steps
Write-Host "================================================" -ForegroundColor Cyan
Write-Host "Next Steps for Deployment" -ForegroundColor Cyan
Write-Host "================================================`n" -ForegroundColor Cyan

Write-Host "1. 📥 Download Publish Profile from Azure Portal:" -ForegroundColor White
Write-Host "   - Go to: https://portal.azure.com" -ForegroundColor Gray
Write-Host "   - Navigate to your Web App: $WebAppName" -ForegroundColor Gray
Write-Host "   - Click 'Download publish profile'" -ForegroundColor Gray
Write-Host ""

Write-Host "2. 🔑 Add Publish Profile to GitHub Secrets:" -ForegroundColor White
Write-Host "   - Go to: https://github.com/YOUR-USERNAME/YOUR-REPO/settings/secrets/actions" -ForegroundColor Gray
Write-Host "   - Click 'New repository secret'" -ForegroundColor Gray
Write-Host "   - Name: AZURE_WEBAPP_PUBLISH_PROFILE" -ForegroundColor Yellow
Write-Host "   - Value: [Paste entire contents of publish profile XML]" -ForegroundColor Gray
Write-Host ""

Write-Host "3. 🏗️  Build Frontend (if needed):" -ForegroundColor White
Write-Host "   cd frontend" -ForegroundColor Gray
Write-Host "   npm install" -ForegroundColor Gray
Write-Host "   npm run build" -ForegroundColor Gray
Write-Host ""

Write-Host "4. 🚀 Push to GitHub to trigger deployment:" -ForegroundColor White
Write-Host "   git add ." -ForegroundColor Gray
Write-Host "   git commit -m 'Fix Azure deployment configuration'" -ForegroundColor Gray
Write-Host "   git push origin main" -ForegroundColor Gray
Write-Host ""

Write-Host "5. 📊 Monitor Deployment:" -ForegroundColor White
Write-Host "   - GitHub Actions: https://github.com/YOUR-USERNAME/YOUR-REPO/actions" -ForegroundColor Gray
Write-Host "   - Azure Portal: https://portal.azure.com" -ForegroundColor Gray
Write-Host ""

if ($issues.Count -eq 0 -and $warnings.Count -eq 0) {
    Write-Host "🎉 Your deployment is ready! Push to GitHub to deploy." -ForegroundColor Green
} elseif ($issues.Count -eq 0) {
    Write-Host "✅ Configuration looks good. Address warnings for best results." -ForegroundColor Green
} else {
    Write-Host "⚠️  Fix critical issues before deploying." -ForegroundColor Yellow
}

Write-Host ""
