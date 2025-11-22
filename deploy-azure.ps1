# Azure Deployment Quick Setup Script for Windows
# Run this script to quickly set up your Azure deployment

Write-Host "🚀 Azure Deployment Setup" -ForegroundColor Cyan
Write-Host "=========================" -ForegroundColor Cyan
Write-Host ""

# Check if Azure CLI is installed
Write-Host "1. Checking Azure CLI..." -ForegroundColor Yellow
if (!(Get-Command az -ErrorAction SilentlyContinue)) {
    Write-Host "❌ Azure CLI not found!" -ForegroundColor Red
    Write-Host "   Install from: https://aka.ms/installazurecliwindows" -ForegroundColor White
    exit 1
}
Write-Host "✅ Azure CLI found" -ForegroundColor Green
Write-Host ""

# Login to Azure
Write-Host "2. Azure Login" -ForegroundColor Yellow
Write-Host "   Opening browser for authentication..." -ForegroundColor White
az login
if ($LASTEXITCODE -ne 0) {
    Write-Host "❌ Login failed" -ForegroundColor Red
    exit 1
}
Write-Host "✅ Logged in successfully" -ForegroundColor Green
Write-Host ""

# Get configuration
Write-Host "3. Configuration" -ForegroundColor Yellow
$appName = Read-Host "Enter Web App name (default: diabetes-predictor-ai)"
if ([string]::IsNullOrWhiteSpace($appName)) {
    $appName = "diabetes-predictor-ai"
}

$resourceGroup = Read-Host "Enter Resource Group name (default: diabetes-predictor-rg)"
if ([string]::IsNullOrWhiteSpace($resourceGroup)) {
    $resourceGroup = "diabetes-predictor-rg"
}

$location = Read-Host "Enter Azure region (default: eastus)"
if ([string]::IsNullOrWhiteSpace($location)) {
    $location = "eastus"
}

Write-Host ""
Write-Host "Configuration:" -ForegroundColor Cyan
Write-Host "  App Name: $appName" -ForegroundColor White
Write-Host "  Resource Group: $resourceGroup" -ForegroundColor White
Write-Host "  Location: $location" -ForegroundColor White
Write-Host ""

$confirm = Read-Host "Continue? (y/n)"
if ($confirm -ne 'y') {
    Write-Host "Cancelled" -ForegroundColor Yellow
    exit 0
}
Write-Host ""

# Create Resource Group
Write-Host "4. Creating Resource Group..." -ForegroundColor Yellow
az group create --name $resourceGroup --location $location
if ($LASTEXITCODE -eq 0) {
    Write-Host "✅ Resource Group created" -ForegroundColor Green
} else {
    Write-Host "⚠️  Resource Group might already exist or error occurred" -ForegroundColor Yellow
}
Write-Host ""

# Create App Service Plan
Write-Host "5. Creating App Service Plan..." -ForegroundColor Yellow
$planName = "$appName-plan"
az appservice plan create `
    --name $planName `
    --resource-group $resourceGroup `
    --sku B1 `
    --is-linux

if ($LASTEXITCODE -eq 0) {
    Write-Host "✅ App Service Plan created" -ForegroundColor Green
} else {
    Write-Host "⚠️  Error creating App Service Plan" -ForegroundColor Yellow
}
Write-Host ""

# Create Web App
Write-Host "6. Creating Web App..." -ForegroundColor Yellow
az webapp create `
    --resource-group $resourceGroup `
    --plan $planName `
    --name $appName `
    --runtime "PYTHON:3.11"

if ($LASTEXITCODE -eq 0) {
    Write-Host "✅ Web App created" -ForegroundColor Green
} else {
    Write-Host "❌ Error creating Web App" -ForegroundColor Red
    exit 1
}
Write-Host ""

# Configure startup command
Write-Host "7. Configuring startup command..." -ForegroundColor Yellow
az webapp config set `
    --resource-group $resourceGroup `
    --name $appName `
    --startup-file "startup.sh"

Write-Host "✅ Startup command configured" -ForegroundColor Green
Write-Host ""

# Get publish profile
Write-Host "8. Getting publish profile..." -ForegroundColor Yellow
$publishProfile = az webapp deployment list-publishing-profiles `
    --name $appName `
    --resource-group $resourceGroup `
    --xml

Write-Host "✅ Publish profile retrieved" -ForegroundColor Green
Write-Host ""

# Save publish profile to file
$profilePath = "azure-publish-profile.xml"
$publishProfile | Out-File -FilePath $profilePath -Encoding UTF8
Write-Host "📄 Publish profile saved to: $profilePath" -ForegroundColor Cyan
Write-Host ""

# Instructions
Write-Host "================================" -ForegroundColor Cyan
Write-Host "✅ Azure Setup Complete!" -ForegroundColor Green
Write-Host "================================" -ForegroundColor Cyan
Write-Host ""
Write-Host "Next Steps:" -ForegroundColor Yellow
Write-Host ""
Write-Host "1. Add Environment Variables in Azure Portal:" -ForegroundColor White
Write-Host "   https://portal.azure.com" -ForegroundColor Cyan
Write-Host "   Go to: $appName → Configuration → Application settings" -ForegroundColor White
Write-Host ""
Write-Host "2. Add GitHub Secret:" -ForegroundColor White
Write-Host "   - Go to: GitHub Repository → Settings → Secrets → Actions" -ForegroundColor White
Write-Host "   - Click: New repository secret" -ForegroundColor White
Write-Host "   - Name: AZURE_WEBAPP_PUBLISH_PROFILE" -ForegroundColor White
Write-Host "   - Value: Contents of $profilePath" -ForegroundColor Cyan
Write-Host ""
Write-Host "3. Update workflow file:" -ForegroundColor White
Write-Host "   Edit .github/workflows/azure-deploy.yml" -ForegroundColor White
Write-Host "   Change AZURE_WEBAPP_NAME to: $appName" -ForegroundColor Cyan
Write-Host ""
Write-Host "4. Push to GitHub to trigger deployment:" -ForegroundColor White
Write-Host "   git add ." -ForegroundColor Cyan
Write-Host "   git commit -m 'Deploy to Azure'" -ForegroundColor Cyan
Write-Host "   git push origin main" -ForegroundColor Cyan
Write-Host ""
Write-Host "Your app URL: https://$appName.azurewebsites.net" -ForegroundColor Green
Write-Host ""
Write-Host "📚 Full guide: AZURE_DEPLOYMENT.md" -ForegroundColor Yellow
Write-Host ""
