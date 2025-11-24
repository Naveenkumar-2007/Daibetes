# ============================================================================
# GitHub Actions Setup Script for Azure Deployment
# Run this ONCE to set up everything
# ============================================================================

param(
    [string]$AppName = "diabetes-predictor-ai",
    [string]$ResourceGroup = "diabetes-predictor-rg",
    [string]$Location = "eastus"
)

$ErrorActionPreference = "Stop"

Write-Host @"
╔════════════════════════════════════════════════════════════╗
║  🚀 GitHub Actions Azure Deployment Setup                  ║
║  Diabetes Predictor - Automated CI/CD                      ║
╚════════════════════════════════════════════════════════════╝
"@ -ForegroundColor Cyan

# Check prerequisites
Write-Host "`n📋 Checking prerequisites..." -ForegroundColor Yellow
try {
    az --version | Out-Null
    Write-Host "✅ Azure CLI installed" -ForegroundColor Green
} catch {
    Write-Host "❌ Azure CLI not installed" -ForegroundColor Red
    Write-Host "Install from: https://aka.ms/installazurecliwindows" -ForegroundColor Yellow
    exit 1
}

try {
    git --version | Out-Null
    Write-Host "✅ Git installed" -ForegroundColor Green
} catch {
    Write-Host "❌ Git not installed" -ForegroundColor Red
    Write-Host "Install from: https://git-scm.com/download/win" -ForegroundColor Yellow
    exit 1
}

# Login to Azure
Write-Host "`n🔐 Logging into Azure..." -ForegroundColor Yellow
az login

# Get subscription ID
$subscriptionId = az account show --query id --output tsv
Write-Host "✅ Subscription ID: $subscriptionId" -ForegroundColor Green

# Create resource group
Write-Host "`n🏗️ Creating resource group: $ResourceGroup" -ForegroundColor Yellow
az group create --name $ResourceGroup --location $Location --output table

# Create App Service Plan
Write-Host "`n📦 Creating App Service Plan..." -ForegroundColor Yellow
az appservice plan create `
    --name "diabetes-plan" `
    --resource-group $ResourceGroup `
    --is-linux `
    --sku B1 `
    --output table

# Create Web App
Write-Host "`n🌍 Creating Web App: $AppName" -ForegroundColor Yellow
az webapp create `
    --resource-group $ResourceGroup `
    --plan "diabetes-plan" `
    --name $AppName `
    --runtime "PYTHON:3.11" `
    --output table

# Create Service Principal
Write-Host "`n🔑 Creating Service Principal for GitHub Actions..." -ForegroundColor Yellow
$spOutput = az ad sp create-for-rbac `
    --name "diabetes-predictor-github-$((Get-Date).ToString('yyyyMMddHHmmss'))" `
    --role contributor `
    --scopes "/subscriptions/$subscriptionId/resourceGroups/$ResourceGroup" `
    --sdk-auth

Write-Host "`n╔════════════════════════════════════════════════════════════╗" -ForegroundColor Green
Write-Host "║  ✅ Azure Resources Created Successfully!                  ║" -ForegroundColor Green
Write-Host "╚════════════════════════════════════════════════════════════╝" -ForegroundColor Green

# Collect secrets
Write-Host "`n📝 Now let's collect your secrets..." -ForegroundColor Cyan
Write-Host "`nPlease enter the following information:" -ForegroundColor Yellow

$groqKey = Read-Host "`n1️⃣ Enter your GROQ_API_KEY (from https://console.groq.com)"
$firebaseUrl = Read-Host "2️⃣ Enter FIREBASE_DATABASE_URL (or press Enter for default)"
if ([string]::IsNullOrWhiteSpace($firebaseUrl)) {
    $firebaseUrl = "https://diabetes-prediction-22082-default-rtdb.firebaseio.com"
}

Write-Host "`n3️⃣ Generating SECRET_KEY..." -ForegroundColor Yellow
$secretKey = -join ((65..90) + (97..122) + (48..57) | Get-Random -Count 32 | ForEach-Object {[char]$_})
Write-Host "Generated: $secretKey" -ForegroundColor Green

# Display instructions
Write-Host @"

╔════════════════════════════════════════════════════════════╗
║  📋 GitHub Secrets Configuration                           ║
╚════════════════════════════════════════════════════════════╝

⚠️  IMPORTANT: Copy these values to GitHub Secrets

Go to: https://github.com/Naveenkumar-2007/Daibetes/settings/secrets/actions

Add these 4 secrets:

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

1️⃣  Secret Name: AZURE_CREDENTIALS
    Value: 
$spOutput

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

2️⃣  Secret Name: GROQ_API_KEY
    Value: $groqKey

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

3️⃣  Secret Name: FIREBASE_DATABASE_URL
    Value: $firebaseUrl

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

4️⃣  Secret Name: SECRET_KEY
    Value: $secretKey

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

"@ -ForegroundColor Cyan

# Save to file for reference
$secretsFile = "github-secrets.txt"
@"
GitHub Secrets for Diabetes Predictor
Generated: $(Get-Date)
======================================

1. AZURE_CREDENTIALS
$spOutput

2. GROQ_API_KEY
$groqKey

3. FIREBASE_DATABASE_URL
$firebaseUrl

4. SECRET_KEY
$secretKey

======================================
App URL: https://$AppName.azurewebsites.net
Resource Group: $ResourceGroup
======================================
"@ | Out-File -FilePath $secretsFile -Encoding UTF8

Write-Host "💾 Secrets saved to: $secretsFile" -ForegroundColor Green
Write-Host "⚠️  Keep this file secure and delete after copying to GitHub!" -ForegroundColor Yellow

# Git setup
Write-Host "`n📦 Would you like to initialize Git and push to GitHub now? (Y/N)" -ForegroundColor Cyan
$gitChoice = Read-Host

if ($gitChoice -eq "Y" -or $gitChoice -eq "y") {
    Write-Host "`n🔧 Setting up Git..." -ForegroundColor Yellow
    
    if (-not (Test-Path ".git")) {
        git init
        Write-Host "✅ Git initialized" -ForegroundColor Green
    }
    
    Write-Host "`n📝 Enter your GitHub repository URL:" -ForegroundColor Cyan
    Write-Host "   Example: https://github.com/Naveenkumar-2007/Daibetes.git" -ForegroundColor Gray
    $repoUrl = Read-Host "URL"
    
    if ($repoUrl) {
        # Check if remote exists
        $remoteExists = git remote -v 2>$null | Select-String "origin"
        if ($remoteExists) {
            git remote set-url origin $repoUrl
        } else {
            git remote add origin $repoUrl
        }
        
        Write-Host "`n📦 Adding files to Git..." -ForegroundColor Yellow
        git add .
        git commit -m "Setup Azure deployment with GitHub Actions"
        
        Write-Host "`n🚀 Pushing to GitHub..." -ForegroundColor Yellow
        git push -u origin main
        
        Write-Host "✅ Code pushed to GitHub!" -ForegroundColor Green
    }
}

Write-Host @"

╔════════════════════════════════════════════════════════════╗
║  ✅ Setup Complete!                                        ║
╚════════════════════════════════════════════════════════════╝

📋 Next Steps:

1. Copy secrets from $secretsFile to GitHub:
   👉 https://github.com/Naveenkumar-2007/Daibetes/settings/secrets/actions

2. Push code to GitHub (if not done already):
   git add .
   git commit -m "Deploy to Azure"
   git push origin main

3. Watch deployment:
   👉 https://github.com/Naveenkumar-2007/Daibetes/actions

4. Access your app:
   👉 https://$AppName.azurewebsites.net

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

🔄 From now on, every push to main branch will auto-deploy!

"@ -ForegroundColor Green

Write-Host "Press any key to exit..." -ForegroundColor Gray
$null = $Host.UI.RawUI.ReadKey("NoEcho,IncludeKeyDown")
