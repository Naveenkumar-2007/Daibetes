# ============================================================================
# Windows PowerShell Azure Deployment Script for Diabetes Predictor
# ============================================================================

param(
    [string]$ResourceGroup = "diabetes-predictor-rg",
    [string]$ACRName = "diabetesacr",
    [string]$AppName = "diabetes-predictor-ai",
    [string]$PlanName = "diabetes-plan",
    [string]$Location = "eastus",
    [string]$ImageTag = "latest"
)

$ErrorActionPreference = "Stop"

Write-Host "🚀 Starting Azure Deployment for Diabetes Predictor" -ForegroundColor Cyan
Write-Host "==================================================" -ForegroundColor Cyan

# Check prerequisites
Write-Host "`n📋 Checking prerequisites..." -ForegroundColor Yellow
try {
    az --version | Out-Null
    Write-Host "✅ Azure CLI installed" -ForegroundColor Green
} catch {
    Write-Host "❌ Azure CLI not installed. Install from: https://aka.ms/installazurecliwindows" -ForegroundColor Red
    exit 1
}

try {
    docker --version | Out-Null
    Write-Host "✅ Docker installed" -ForegroundColor Green
} catch {
    Write-Host "❌ Docker not installed. Install from: https://www.docker.com/products/docker-desktop" -ForegroundColor Red
    exit 1
}

try {
    node --version | Out-Null
    Write-Host "✅ Node.js installed" -ForegroundColor Green
} catch {
    Write-Host "❌ Node.js not installed. Install from: https://nodejs.org/" -ForegroundColor Red
    exit 1
}

# Login to Azure
Write-Host "`n🔐 Logging into Azure..." -ForegroundColor Yellow
az login

# Optional: Set subscription
# $subscriptionId = Read-Host "Enter your Azure Subscription ID (or press Enter to use default)"
# if ($subscriptionId) {
#     az account set --subscription $subscriptionId
# }

# Create Resource Group
Write-Host "`n🏗️ Creating resource group: $ResourceGroup" -ForegroundColor Yellow
az group create --name $ResourceGroup --location $Location --output table

# Create Azure Container Registry
Write-Host "`n📦 Creating Azure Container Registry: $ACRName" -ForegroundColor Yellow
az acr create `
    --resource-group $ResourceGroup `
    --name $ACRName `
    --sku Basic `
    --admin-enabled true `
    --output table

# Build Frontend
Write-Host "`n📦 Building React frontend..." -ForegroundColor Yellow
Push-Location frontend
if (-not (Test-Path "node_modules")) {
    Write-Host "Installing npm dependencies..." -ForegroundColor Yellow
    npm install
}
npm run build
Pop-Location
Write-Host "✅ Frontend built successfully" -ForegroundColor Green

# Build Docker Image
Write-Host "`n🐳 Building Docker image..." -ForegroundColor Yellow
docker build -t "$ACRName.azurecr.io/diabetes-predictor:$ImageTag" .
Write-Host "✅ Docker image built" -ForegroundColor Green

# Login to ACR and Push Image
Write-Host "`n📤 Pushing Docker image to ACR..." -ForegroundColor Yellow
az acr login --name $ACRName
docker push "$ACRName.azurecr.io/diabetes-predictor:$ImageTag"
Write-Host "✅ Image pushed to registry" -ForegroundColor Green

# Get ACR Credentials
Write-Host "`n🔑 Retrieving ACR credentials..." -ForegroundColor Yellow
$acrCreds = az acr credential show --name $ACRName | ConvertFrom-Json
$acrUser = $acrCreds.username
$acrPass = $acrCreds.passwords[0].value

# Create App Service Plan
Write-Host "`n🌐 Creating App Service Plan: $PlanName" -ForegroundColor Yellow
az appservice plan create `
    --name $PlanName `
    --resource-group $ResourceGroup `
    --is-linux `
    --sku B1 `
    --output table

# Create Web App
Write-Host "`n🌍 Creating Web App: $AppName" -ForegroundColor Yellow
az webapp create `
    --resource-group $ResourceGroup `
    --plan $PlanName `
    --name $AppName `
    --deployment-container-image-name "$ACRName.azurecr.io/diabetes-predictor:$ImageTag" `
    --output table

# Configure Container Settings
Write-Host "`n⚙️ Configuring container settings..." -ForegroundColor Yellow
az webapp config container set `
    --name $AppName `
    --resource-group $ResourceGroup `
    --docker-custom-image-name "$ACRName.azurecr.io/diabetes-predictor:$ImageTag" `
    --docker-registry-server-url "https://$ACRName.azurecr.io" `
    --docker-registry-server-user $acrUser `
    --docker-registry-server-password $acrPass

# Prompt for environment variables
Write-Host "`n🔧 Setting environment variables..." -ForegroundColor Yellow
Write-Host "Please enter your configuration:" -ForegroundColor Cyan
$groqKey = Read-Host "GROQ_API_KEY"
$firebaseUrl = Read-Host "FIREBASE_DATABASE_URL (or press Enter for default)"
if ([string]::IsNullOrWhiteSpace($firebaseUrl)) {
    $firebaseUrl = "https://diabetes-prediction-22082-default-rtdb.firebaseio.com"
}
$secretKey = Read-Host "SECRET_KEY (or press Enter to generate)"
if ([string]::IsNullOrWhiteSpace($secretKey)) {
    $secretKey = -join ((65..90) + (97..122) + (48..57) | Get-Random -Count 32 | ForEach-Object {[char]$_})
}

# Set App Settings
az webapp config appsettings set `
    --resource-group $ResourceGroup `
    --name $AppName `
    --settings `
        GROQ_API_KEY="$groqKey" `
        FIREBASE_DATABASE_URL="$firebaseUrl" `
        SECRET_KEY="$secretKey" `
        WEBSITES_PORT=8080 `
        FLASK_ENV=production `
        PYTHONUNBUFFERED=1 `
    --output table

# Enable HTTPS Only
Write-Host "`n🔒 Enabling HTTPS only..." -ForegroundColor Yellow
az webapp update `
    --resource-group $ResourceGroup `
    --name $AppName `
    --https-only true

# Enable Container Logging
Write-Host "`n📋 Enabling container logging..." -ForegroundColor Yellow
az webapp log config `
    --name $AppName `
    --resource-group $ResourceGroup `
    --docker-container-logging filesystem `
    --level information

# Restart App
Write-Host "`n🔄 Restarting application..." -ForegroundColor Yellow
az webapp restart `
    --name $AppName `
    --resource-group $ResourceGroup

# Show deployment info
Write-Host "`n==================================================" -ForegroundColor Green
Write-Host "✅ Deployment Completed Successfully!" -ForegroundColor Green
Write-Host "==================================================" -ForegroundColor Green

Write-Host "`n📊 Deployment Information:" -ForegroundColor Cyan
Write-Host "Resource Group: " -NoNewline; Write-Host $ResourceGroup -ForegroundColor Green
Write-Host "App Name: " -NoNewline; Write-Host $AppName -ForegroundColor Green
Write-Host "Container Registry: " -NoNewline; Write-Host $ACRName -ForegroundColor Green
Write-Host "App Service Plan: " -NoNewline; Write-Host $PlanName -ForegroundColor Green

Write-Host "`n🌍 Your application is available at:" -ForegroundColor Cyan
Write-Host "https://$AppName.azurewebsites.net" -ForegroundColor Green

Write-Host "`n📝 Useful commands:" -ForegroundColor Yellow
Write-Host "View logs: " -NoNewline; Write-Host "az webapp log tail -n $AppName -g $ResourceGroup" -ForegroundColor Cyan
Write-Host "Restart app: " -NoNewline; Write-Host "az webapp restart -n $AppName -g $ResourceGroup" -ForegroundColor Cyan
Write-Host "SSH into container: " -NoNewline; Write-Host "az webapp ssh -n $AppName -g $ResourceGroup" -ForegroundColor Cyan
Write-Host "Delete resources: " -NoNewline; Write-Host "az group delete -n $ResourceGroup --yes" -ForegroundColor Cyan

Write-Host "`n⏳ Note: It may take 2-3 minutes for the app to start." -ForegroundColor Yellow
Write-Host "Monitor logs with: az webapp log tail -n $AppName -g $ResourceGroup" -ForegroundColor Yellow
