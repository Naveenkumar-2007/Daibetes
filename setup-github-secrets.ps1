# ============================================================================
# GitHub Secrets Setup Script for Diabetes Health Predictor
# ============================================================================
# This script automatically configures all required GitHub secrets for deployment
# Prerequisites: GitHub CLI (gh) must be installed
# Install: winget install GitHub.cli
# ============================================================================

Write-Host "🔐 GitHub Secrets Setup for Diabetes Health Predictor" -ForegroundColor Cyan
Write-Host "=" * 70 -ForegroundColor Cyan
Write-Host ""

# Check if GitHub CLI is installed
if (-not (Get-Command gh -ErrorAction SilentlyContinue)) {
    Write-Host "❌ GitHub CLI (gh) is not installed!" -ForegroundColor Red
    Write-Host "📥 Please install it using: winget install GitHub.cli" -ForegroundColor Yellow
    exit 1
}

# Login check
Write-Host "🔍 Checking GitHub authentication..." -ForegroundColor Yellow
$authStatus = gh auth status 2>&1
if ($LASTEXITCODE -ne 0) {
    Write-Host "❌ Not logged in to GitHub!" -ForegroundColor Red
    Write-Host "🔑 Please login using: gh auth login" -ForegroundColor Yellow
    exit 1
}

Write-Host "✅ GitHub CLI authenticated" -ForegroundColor Green
Write-Host ""

# Set repository
$REPO = "Naveenkumar-2007/Daibetes"
Write-Host "📦 Repository: $REPO" -ForegroundColor Cyan
Write-Host ""

# Confirm before proceeding
$confirm = Read-Host "⚠️  This will add/update secrets in your repository. Continue? (Y/N)"
if ($confirm -ne "Y" -and $confirm -ne "y") {
    Write-Host "❌ Cancelled by user" -ForegroundColor Red
    exit 0
}

Write-Host ""

# Load environment variables from .env file
Write-Host "📖 Reading secrets from .env file..." -ForegroundColor Yellow
if (-not (Test-Path ".env")) {
    Write-Host "❌ .env file not found!" -ForegroundColor Red
    exit 1
}

# Parse .env file
$envVars = @{}
Get-Content .env | ForEach-Object {
    if ($_ -match '^([^#=]+)="?([^"]*)"?$') {
        $key = $matches[1].Trim()
        $value = $matches[2].Trim()
        $envVars[$key] = $value
    }
}

Write-Host "✅ Loaded secrets from .env" -ForegroundColor Green
Write-Host ""

# AI Service Keys
Write-Host "  📝 Adding GROQ_API_KEY..." -NoNewline
gh secret set GROQ_API_KEY -b $envVars['GROQ_API_KEY'] -R $REPO 2>&1 | Out-Null
if ($LASTEXITCODE -eq 0) { Write-Host " ✅" -ForegroundColor Green } else { Write-Host " ❌" -ForegroundColor Red }

Write-Host "  📝 Adding PINECONE_API_KEY..." -NoNewline
gh secret set PINECONE_API_KEY -b $envVars['PINECONE_API_KEY'] -R $REPO 2>&1 | Out-Null
if ($LASTEXITCODE -eq 0) { Write-Host " ✅" -ForegroundColor Green } else { Write-Host " ❌" -ForegroundColor Red }

# Firebase Configuration
Write-Host "  📝 Adding FIREBASE_API_KEY..." -NoNewline
gh secret set FIREBASE_API_KEY -b $envVars['FIREBASE_API_KEY'] -R $REPO 2>&1 | Out-Null
if ($LASTEXITCODE -eq 0) { Write-Host " ✅" -ForegroundColor Green } else { Write-Host " ❌" -ForegroundColor Red }

Write-Host "  📝 Adding FIREBASE_PROJECT_ID..." -NoNewline
gh secret set FIREBASE_PROJECT_ID -b $envVars['FIREBASE_PROJECT_ID'] -R $REPO 2>&1 | Out-Null
if ($LASTEXITCODE -eq 0) { Write-Host " ✅" -ForegroundColor Green } else { Write-Host " ❌" -ForegroundColor Red }

Write-Host "  📝 Adding FIREBASE_PRIVATE_KEY_ID..." -NoNewline
gh secret set FIREBASE_PRIVATE_KEY_ID -b $envVars['FIREBASE_PRIVATE_KEY_ID'] -R $REPO 2>&1 | Out-Null
if ($LASTEXITCODE -eq 0) { Write-Host " ✅" -ForegroundColor Green } else { Write-Host " ❌" -ForegroundColor Red }

Write-Host "  📝 Adding FIREBASE_CLIENT_EMAIL..." -NoNewline
gh secret set FIREBASE_CLIENT_EMAIL -b $envVars['FIREBASE_CLIENT_EMAIL'] -R $REPO 2>&1 | Out-Null
if ($LASTEXITCODE -eq 0) { Write-Host " ✅" -ForegroundColor Green } else { Write-Host " ❌" -ForegroundColor Red }

Write-Host "  📝 Adding FIREBASE_CLIENT_ID..." -NoNewline
gh secret set FIREBASE_CLIENT_ID -b $envVars['FIREBASE_CLIENT_ID'] -R $REPO 2>&1 | Out-Null
if ($LASTEXITCODE -eq 0) { Write-Host " ✅" -ForegroundColor Green } else { Write-Host " ❌" -ForegroundColor Red }

Write-Host "  📝 Adding FIREBASE_AUTH_DOMAIN..." -NoNewline
gh secret set FIREBASE_AUTH_DOMAIN -b $envVars['FIREBASE_AUTH_DOMAIN'] -R $REPO 2>&1 | Out-Null
if ($LASTEXITCODE -eq 0) { Write-Host " ✅" -ForegroundColor Green } else { Write-Host " ❌" -ForegroundColor Red }

Write-Host "  📝 Adding FIREBASE_DATABASE_URL..." -NoNewline
gh secret set FIREBASE_DATABASE_URL -b $envVars['FIREBASE_DATABASE_URL'] -R $REPO 2>&1 | Out-Null
if ($LASTEXITCODE -eq 0) { Write-Host " ✅" -ForegroundColor Green } else { Write-Host " ❌" -ForegroundColor Red }

Write-Host "  📝 Adding FIREBASE_STORAGE_BUCKET..." -NoNewline
gh secret set FIREBASE_STORAGE_BUCKET -b $envVars['FIREBASE_STORAGE_BUCKET'] -R $REPO 2>&1 | Out-Null
if ($LASTEXITCODE -eq 0) { Write-Host " ✅" -ForegroundColor Green } else { Write-Host " ❌" -ForegroundColor Red }

# Application Secrets
Write-Host "  📝 Adding SECRET_KEY..." -NoNewline
gh secret set SECRET_KEY -b $envVars['SECRET_KEY'] -R $REPO 2>&1 | Out-Null
if ($LASTEXITCODE -eq 0) { Write-Host " ✅" -ForegroundColor Green } else { Write-Host " ❌" -ForegroundColor Red }

# Google OAuth
Write-Host "  📝 Adding GOOGLE_CLIENT_ID..." -NoNewline
gh secret set GOOGLE_CLIENT_ID -b $envVars['GOOGLE_CLIENT_ID'] -R $REPO 2>&1 | Out-Null
if ($LASTEXITCODE -eq 0) { Write-Host " ✅" -ForegroundColor Green } else { Write-Host " ❌" -ForegroundColor Red }

Write-Host "  📝 Adding GOOGLE_CLIENT_SECRET..." -NoNewline
gh secret set GOOGLE_CLIENT_SECRET -b $envVars['GOOGLE_CLIENT_SECRET'] -R $REPO 2>&1 | Out-Null
if ($LASTEXITCODE -eq 0) { Write-Host " ✅" -ForegroundColor Green } else { Write-Host " ❌" -ForegroundColor Red }

# SMTP Configuration
Write-Host "  📝 Adding SMTP_FROM_EMAIL..." -NoNewline
gh secret set SMTP_FROM_EMAIL -b $envVars['SMTP_FROM_EMAIL'] -R $REPO 2>&1 | Out-Null
if ($LASTEXITCODE -eq 0) { Write-Host " ✅" -ForegroundColor Green } else { Write-Host " ❌" -ForegroundColor Red }

Write-Host "  📝 Adding SMTP_HOST..." -NoNewline
gh secret set SMTP_HOST -b $envVars['SMTP_HOST'] -R $REPO 2>&1 | Out-Null
if ($LASTEXITCODE -eq 0) { Write-Host " ✅" -ForegroundColor Green } else { Write-Host " ❌" -ForegroundColor Red }

Write-Host "  📝 Adding SMTP_PASSWORD..." -NoNewline
gh secret set SMTP_PASSWORD -b $envVars['SMTP_PASSWORD'] -R $REPO 2>&1 | Out-Null
if ($LASTEXITCODE -eq 0) { Write-Host " ✅" -ForegroundColor Green } else { Write-Host " ❌" -ForegroundColor Red }

Write-Host "  📝 Adding SMTP_PORT..." -NoNewline
gh secret set SMTP_PORT -b $envVars['SMTP_PORT'] -R $REPO 2>&1 | Out-Null
if ($LASTEXITCODE -eq 0) { Write-Host " ✅" -ForegroundColor Green } else { Write-Host " ❌" -ForegroundColor Red }

Write-Host "  📝 Adding SMTP_USE_TLS..." -NoNewline
gh secret set SMTP_USE_TLS -b $envVars['SMTP_USE_TLS'] -R $REPO 2>&1 | Out-Null
if ($LASTEXITCODE -eq 0) { Write-Host " ✅" -ForegroundColor Green } else { Write-Host " ❌" -ForegroundColor Red }

Write-Host "  📝 Adding SMTP_USERNAME..." -NoNewline
gh secret set SMTP_USERNAME -b $envVars['SMTP_USERNAME'] -R $REPO 2>&1 | Out-Null
if ($LASTEXITCODE -eq 0) { Write-Host " ✅" -ForegroundColor Green } else { Write-Host " ❌" -ForegroundColor Red }

# Firebase Service Account JSON (Base64 encoded)
Write-Host "  📝 Adding FIREBASE_SERVICE_ACCOUNT_JSON..." -NoNewline
gh secret set FIREBASE_SERVICE_ACCOUNT_JSON -b $envVars['FIREBASE_SERVICE_ACCOUNT_JSON'] -R $REPO 2>&1 | Out-Null
if ($LASTEXITCODE -eq 0) { Write-Host " ✅" -ForegroundColor Green } else { Write-Host " ❌" -ForegroundColor Red }

Write-Host ""
Write-Host "=" * 70 -ForegroundColor Cyan
Write-Host "✅ All secrets have been configured!" -ForegroundColor Green
Write-Host ""
Write-Host "📋 Next Steps:" -ForegroundColor Yellow
Write-Host "  1. Add AZURE_CREDENTIALS secret manually (see GITHUB_SECRETS_SETUP.md)" -ForegroundColor White
Write-Host "  2. Push your code to GitHub: git push origin main" -ForegroundColor White
Write-Host "  3. Monitor deployment: GitHub → Actions tab" -ForegroundColor White
Write-Host "  4. Access your app: https://diabetes-predictor-ai.azurewebsites.net" -ForegroundColor White
Write-Host ""
Write-Host "💡 To verify secrets were added:" -ForegroundColor Cyan
Write-Host "   gh secret list -R $REPO" -ForegroundColor White
Write-Host ""
