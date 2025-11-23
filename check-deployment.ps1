#!/usr/bin/env pwsh
# Simple Azure Deployment Configuration Checker

param(
    [string]$WebAppName = "diabetes-predictor-ai"
)

Write-Host "`n" -NoNewline
Write-Host "========================================" -ForegroundColor Cyan
Write-Host "Azure Deployment Configuration Checker" -ForegroundColor Cyan
Write-Host "========================================`n" -ForegroundColor Cyan

$issues = @()
$warnings = @()

# Check 1: Required files
Write-Host "Checking required files..." -NoNewline
$requiredFiles = @("flask_app.py", "requirements.txt", "startup.sh", ".github/workflows/azure-deploy.yml", ".deployment")
$missingFiles = @()
foreach ($file in $requiredFiles) {
    if (-not (Test-Path $file)) {
        $missingFiles += $file
    }
}

if ($missingFiles.Count -eq 0) {
    Write-Host " OK" -ForegroundColor Green
} else {
    Write-Host " MISSING FILES" -ForegroundColor Red
    foreach ($file in $missingFiles) {
        Write-Host "  - $file" -ForegroundColor Red
    }
    $issues += "Missing files: $($missingFiles -join ', ')"
}

# Check 2: Workflow file
Write-Host "Checking workflow configuration..." -NoNewline
if (Test-Path ".github/workflows/azure-deploy.yml") {
    $workflow = Get-Content ".github/workflows/azure-deploy.yml" -Raw
    
    if ($workflow -match $WebAppName) {
        Write-Host " OK" -ForegroundColor Green
    } else {
        Write-Host " WARNING" -ForegroundColor Yellow
        $warnings += "App name not found in workflow"
    }
    
    if ($workflow -match "slot-name") {
        Write-Host "  slot-name configured: YES" -ForegroundColor Green
    } else {
        Write-Host "  slot-name configured: NO" -ForegroundColor Yellow
    }
} else {
    Write-Host " MISSING" -ForegroundColor Red
    $issues += "Workflow file missing"
}

# Check 3: Frontend
Write-Host "Checking frontend..." -NoNewline
if (Test-Path "frontend/package.json") {
    if ((Test-Path "frontend/dist") -or (Test-Path "frontend/build")) {
        Write-Host " BUILT" -ForegroundColor Green
    } else {
        Write-Host " NOT BUILT" -ForegroundColor Yellow
        $warnings += "Frontend needs to be built"
    }
} else {
    Write-Host " NO PACKAGE.JSON" -ForegroundColor Red
    $issues += "Frontend package.json missing"
}

# Check 4: Publish profiles
Write-Host "Checking publish profile files..." -NoNewline
$profiles = Get-ChildItem -Filter "*publish-profile*.xml" -ErrorAction SilentlyContinue
if ($profiles.Count -gt 0) {
    Write-Host " FOUND ($($profiles.Count) file(s))" -ForegroundColor Green
    $profileContent = Get-Content $profiles[0].FullName -Raw
    if ($profileContent -match $WebAppName) {
        Write-Host "  Profile matches app name: YES" -ForegroundColor Green
    } else {
        Write-Host "  Profile matches app name: NO" -ForegroundColor Yellow
        $warnings += "Publish profile may not match app name"
    }
} else {
    Write-Host " NOT FOUND" -ForegroundColor Yellow
    $warnings += "No publish profile file found locally"
}

# Summary
Write-Host "`n" -NoNewline
Write-Host "========================================" -ForegroundColor Cyan
Write-Host "Summary" -ForegroundColor Cyan
Write-Host "========================================`n" -ForegroundColor Cyan

if ($issues.Count -eq 0) {
    Write-Host "CRITICAL ISSUES: None" -ForegroundColor Green
} else {
    Write-Host "CRITICAL ISSUES: $($issues.Count)" -ForegroundColor Red
    foreach ($issue in $issues) {
        Write-Host "  - $issue" -ForegroundColor Red
    }
}

Write-Host ""

if ($warnings.Count -eq 0) {
    Write-Host "WARNINGS: None" -ForegroundColor Green
} else {
    Write-Host "WARNINGS: $($warnings.Count)" -ForegroundColor Yellow
    foreach ($warning in $warnings) {
        Write-Host "  - $warning" -ForegroundColor Yellow
    }
}

Write-Host "`n" -NoNewline
Write-Host "========================================" -ForegroundColor Cyan
Write-Host "Next Steps" -ForegroundColor Cyan
Write-Host "========================================`n" -ForegroundColor Cyan

Write-Host "1. Get publish profile:" -ForegroundColor White
Write-Host "   Run: .\get-publish-profile-enhanced.ps1`n" -ForegroundColor Gray

Write-Host "2. Add to GitHub Secrets:" -ForegroundColor White
Write-Host "   Name: AZURE_WEBAPP_PUBLISH_PROFILE" -ForegroundColor Yellow
Write-Host "   URL: https://github.com/Naveenkumar-2007/Daibetes/settings/secrets/actions`n" -ForegroundColor Gray

Write-Host "3. Push to deploy:" -ForegroundColor White
Write-Host "   git add ." -ForegroundColor Gray
Write-Host "   git commit -m `"Fix deployment`"" -ForegroundColor Gray
Write-Host "   git push origin main`n" -ForegroundColor Gray

if ($issues.Count -eq 0) {
    Write-Host "STATUS: Ready to deploy!" -ForegroundColor Green
} else {
    Write-Host "STATUS: Fix issues before deploying" -ForegroundColor Yellow
}

Write-Host ""
