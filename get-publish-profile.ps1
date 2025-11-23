# Quick Azure Publish Profile Setup
# This script will help you get your publish profile for GitHub Actions

Write-Host "Azure Publish Profile Setup" -ForegroundColor Cyan
Write-Host "===============================" -ForegroundColor Cyan
Write-Host ""

$appName = Read-Host "Enter your Azure Web App name (default: diabetes-predictor-ai)"
if ([string]::IsNullOrWhiteSpace($appName)) {
    $appName = "diabetes-predictor-ai"
}

$resourceGroup = Read-Host "Enter Resource Group name (default: diabetes-predictor-rg)"
if ([string]::IsNullOrWhiteSpace($resourceGroup)) {
    $resourceGroup = "diabetes-predictor-rg"
}

Write-Host ""
Write-Host "Configuration:" -ForegroundColor Yellow
Write-Host "  App Name: $appName" -ForegroundColor White
Write-Host "  Resource Group: $resourceGroup" -ForegroundColor White
Write-Host ""

# Check if logged in
Write-Host "1. Checking Azure login..." -ForegroundColor Yellow
try {
    $account = az account show 2>$null | ConvertFrom-Json
    Write-Host "Logged in as: $($account.user.name)" -ForegroundColor Green
} catch {
    Write-Host "Not logged in to Azure" -ForegroundColor Red
    Write-Host "Logging in..." -ForegroundColor White
    az login
    if ($LASTEXITCODE -ne 0) {
        Write-Host "Login failed" -ForegroundColor Red
        exit 1
    }
}
Write-Host ""

# Check if Web App exists
Write-Host "2. Checking if Web App exists..." -ForegroundColor Yellow
$webAppExists = az webapp show --name $appName --resource-group $resourceGroup 2>$null
if ($LASTEXITCODE -ne 0) {
    Write-Host "Web App not found: $appName" -ForegroundColor Red
    Write-Host ""
    Write-Host "Please create the Web App first:" -ForegroundColor Yellow
    Write-Host "  1. Go to https://portal.azure.com" -ForegroundColor White
    Write-Host "  2. Create a Web App with Python 3.11" -ForegroundColor White
    Write-Host "  OR run: .\deploy-azure.ps1" -ForegroundColor White
    exit 1
}
Write-Host "Web App found" -ForegroundColor Green
Write-Host ""

# Get publish profile
Write-Host "3. Downloading publish profile..." -ForegroundColor Yellow
$publishProfile = az webapp deployment list-publishing-profiles --name $appName --resource-group $resourceGroup --xml

if ($LASTEXITCODE -eq 0) {
    # Save to file
    $profilePath = "azure-publish-profile.xml"
    $publishProfile | Out-File -FilePath $profilePath -Encoding UTF8
    
    Write-Host "Publish profile downloaded" -ForegroundColor Green
    Write-Host ""
    Write-Host "File saved to: $profilePath" -ForegroundColor Cyan
    Write-Host ""
    
    # Copy to clipboard
    try {
        $publishProfile | Set-Clipboard
        Write-Host "Publish profile copied to clipboard!" -ForegroundColor Green
    } catch {
        Write-Host "Could not copy to clipboard" -ForegroundColor Yellow
    }
    
    Write-Host ""
    Write-Host "Next Steps:" -ForegroundColor Cyan
    Write-Host "==============" -ForegroundColor Cyan
    Write-Host ""
    Write-Host "1. Go to: https://github.com/Naveenkumar-2007/Daibetes/settings/secrets/actions" -ForegroundColor Cyan
    Write-Host ""
    Write-Host "2. Click 'New repository secret'" -ForegroundColor White
    Write-Host ""
    Write-Host "3. Add secret:" -ForegroundColor White
    Write-Host "   Name: AZURE_WEBAPP_PUBLISH_PROFILE" -ForegroundColor Yellow
    Write-Host "   Value: Paste from clipboard or file" -ForegroundColor Yellow
    Write-Host ""
    Write-Host "4. Click 'Add secret'" -ForegroundColor White
    Write-Host ""
    Write-Host "5. Re-run GitHub Actions workflow" -ForegroundColor White
    Write-Host ""
    
} else {
    Write-Host "Failed to get publish profile" -ForegroundColor Red
    Write-Host ""
    Write-Host "Manual steps:" -ForegroundColor Yellow
    Write-Host "1. Go to https://portal.azure.com" -ForegroundColor White
    Write-Host "2. Find your Web App: $appName" -ForegroundColor White
    Write-Host "3. Click 'Get publish profile' in top toolbar" -ForegroundColor White
    Write-Host "4. Add to GitHub Secrets as AZURE_WEBAPP_PUBLISH_PROFILE" -ForegroundColor White
}

Write-Host ""
