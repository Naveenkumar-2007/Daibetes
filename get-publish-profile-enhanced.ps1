#!/usr/bin/env pwsh
# Enhanced Azure Publish Profile Retriever
# Helps diagnose and fix publish profile issues

param(
    [string]$WebAppName = "diabetes-predictor-ai",
    [string]$ResourceGroup = "diabetes-predictor-rg",
    [switch]$SaveToFile
)

$ErrorActionPreference = "Stop"

Write-Host "`n🔐 Azure Publish Profile Retriever & Validator" -ForegroundColor Cyan
Write-Host "================================================`n" -ForegroundColor Cyan

# Check if Azure CLI is installed
Write-Host "[1/6] Checking Azure CLI..." -NoNewline
try {
    $azVersion = az version --output json 2>&1 | ConvertFrom-Json
    Write-Host " ✅ v$($azVersion.'azure-cli')" -ForegroundColor Green
} catch {
    Write-Host " ❌" -ForegroundColor Red
    Write-Host "`n❌ Azure CLI is not installed.`n" -ForegroundColor Red
    Write-Host "📥 Install from: https://aka.ms/InstallAzureCLIDirect`n" -ForegroundColor Yellow
    Write-Host "📋 Manual alternative:" -ForegroundColor Yellow
    Write-Host "  1. Go to: https://portal.azure.com" -ForegroundColor Gray
    Write-Host "  2. Navigate to: $WebAppName" -ForegroundColor Gray
    Write-Host "  3. Click 'Download publish profile'`n" -ForegroundColor Gray
    exit 1
}

# Check if logged in
Write-Host "[2/6] Checking Azure login..." -NoNewline
try {
    $account = az account show 2>&1 | ConvertFrom-Json
    Write-Host " ✅" -ForegroundColor Green
    Write-Host "      Account: $($account.user.name)" -ForegroundColor Gray
    Write-Host "      Subscription: $($account.name)" -ForegroundColor Gray
} catch {
    Write-Host " ❌" -ForegroundColor Red
    Write-Host "`n🔑 Logging in to Azure...`n" -ForegroundColor Yellow
    try {
        az login --only-show-errors
        $account = az account show 2>&1 | ConvertFrom-Json
        Write-Host "✅ Login successful: $($account.user.name)`n" -ForegroundColor Green
    } catch {
        Write-Host "❌ Login failed.`n" -ForegroundColor Red
        exit 1
    }
}

# Check if resource group exists
Write-Host "[3/6] Verifying resource group..." -NoNewline
try {
    $rg = az group show --name $ResourceGroup 2>&1 | ConvertFrom-Json
    Write-Host " ✅" -ForegroundColor Green
    Write-Host "      Name: $($rg.name)" -ForegroundColor Gray
    Write-Host "      Location: $($rg.location)" -ForegroundColor Gray
} catch {
    Write-Host " ❌" -ForegroundColor Red
    Write-Host "`n❌ Resource group '$ResourceGroup' not found.`n" -ForegroundColor Red
    
    Write-Host "📋 Available resource groups:" -ForegroundColor Yellow
    $groups = az group list --query "[].{name:name, location:location}" -o json | ConvertFrom-Json
    if ($groups.Count -gt 0) {
        foreach ($g in $groups) {
            Write-Host "  • $($g.name) ($($g.location))" -ForegroundColor Gray
        }
    } else {
        Write-Host "  No resource groups found." -ForegroundColor Gray
    }
    Write-Host ""
    exit 1
}

# Check if web app exists
Write-Host "[4/6] Verifying web app..." -NoNewline
try {
    $webapp = az webapp show --name $WebAppName --resource-group $ResourceGroup 2>&1 | ConvertFrom-Json
    Write-Host " ✅" -ForegroundColor Green
    Write-Host "      Name: $($webapp.name)" -ForegroundColor Gray
    Write-Host "      URL: https://$($webapp.defaultHostName)" -ForegroundColor Gray
    Write-Host "      Runtime: $($webapp.siteConfig.linuxFxVersion)" -ForegroundColor Gray
    Write-Host "      State: $($webapp.state)" -ForegroundColor Gray
} catch {
    Write-Host " ❌" -ForegroundColor Red
    Write-Host "`n❌ Web app '$WebAppName' not found.`n" -ForegroundColor Red
    
    Write-Host "📋 Web apps in '$ResourceGroup':" -ForegroundColor Yellow
    try {
        $webapps = az webapp list --resource-group $ResourceGroup --query "[].{name:name, url:defaultHostName, state:state}" -o json | ConvertFrom-Json
        if ($webapps.Count -gt 0) {
            foreach ($app in $webapps) {
                Write-Host "  • $($app.name) - $($app.state)" -ForegroundColor Gray
                Write-Host "    https://$($app.url)" -ForegroundColor DarkGray
            }
        } else {
            Write-Host "  No web apps found." -ForegroundColor Gray
            Write-Host "`n💡 Create web app first:" -ForegroundColor Yellow
            Write-Host "   az webapp create --name $WebAppName --resource-group $ResourceGroup --plan <plan-name> --runtime 'PYTHON:3.11'`n" -ForegroundColor Gray
        }
    } catch {
        Write-Host "  Unable to list web apps." -ForegroundColor Gray
    }
    Write-Host ""
    exit 1
}

# Get publish profile
Write-Host "[5/6] Retrieving publish profile..." -NoNewline
try {
    $publishProfile = az webapp deployment list-publishing-profiles `
        --name $WebAppName `
        --resource-group $ResourceGroup `
        --xml 2>&1
    
    if ($LASTEXITCODE -ne 0) {
        throw "Failed to retrieve profile"
    }
    
    Write-Host " ✅" -ForegroundColor Green
    
    # Save to file if requested
    $fileName = $null
    if ($SaveToFile) {
        $fileName = "azure-publish-profile-$(Get-Date -Format 'yyyyMMdd-HHmmss').xml"
        $publishProfile | Out-File -FilePath $fileName -Encoding UTF8
        Write-Host "      Saved to: $fileName" -ForegroundColor Gray
    }
    
    # Try to copy to clipboard
    try {
        $publishProfile | Set-Clipboard
        Write-Host "      ✅ Copied to clipboard" -ForegroundColor Green
    } catch {
        Write-Host "      ⚠️  Could not copy to clipboard" -ForegroundColor Yellow
    }
    
} catch {
    Write-Host " ❌" -ForegroundColor Red
    Write-Host "`n❌ Failed to retrieve publish profile.`n" -ForegroundColor Red
    Write-Host "Error: $($_.Exception.Message)`n" -ForegroundColor Red
    exit 1
}

# Validate publish profile
Write-Host "[6/6] Validating publish profile..." -NoNewline
try {
    # Parse key information
    if ($publishProfile -match 'msdeploySite="([^"]+)"') {
        $msdeploySite = $matches[1]
    }
    if ($publishProfile -match 'publishUrl="([^"]+)"') {
        $publishUrl = $matches[1]
    }
    
    # Check if profile matches app name
    if ($msdeploySite -eq $WebAppName) {
        Write-Host " ✅" -ForegroundColor Green
        Write-Host "      MSDeploy Site: $msdeploySite ✅" -ForegroundColor Green
        Write-Host "      Publish URL: $publishUrl" -ForegroundColor Gray
    } else {
        Write-Host " ⚠️" -ForegroundColor Yellow
        Write-Host "      ⚠️  MSDeploy site mismatch!" -ForegroundColor Yellow
        Write-Host "         Expected: $WebAppName" -ForegroundColor Yellow
        Write-Host "         Got: $msdeploySite" -ForegroundColor Yellow
    }
    
    # Count profiles
    $profileCount = ([regex]::Matches($publishProfile, '<publishProfile')).Count
    Write-Host "      Deployment methods: $profileCount (Web Deploy, FTP, Zip)" -ForegroundColor Gray
    
} catch {
    Write-Host " ⚠️" -ForegroundColor Yellow
    Write-Host "      Could not validate profile structure" -ForegroundColor Yellow
}

# Display results
Write-Host "`n" -NoNewline
Write-Host "================================================" -ForegroundColor Green
Write-Host "✅ Publish Profile Retrieved Successfully!" -ForegroundColor Green
Write-Host "================================================`n" -ForegroundColor Green

Write-Host "📋 Profile Details:" -ForegroundColor Cyan
Write-Host "   Web App: $WebAppName" -ForegroundColor White
Write-Host "   Resource Group: $ResourceGroup" -ForegroundColor White
Write-Host "   MSDeploy Site: $msdeploySite" -ForegroundColor White
Write-Host "   Publish URL: $publishUrl" -ForegroundColor White

if ($fileName) {
    Write-Host "   File: $fileName" -ForegroundColor White
}
Write-Host ""

# Next steps
Write-Host "================================================" -ForegroundColor Cyan
Write-Host "📝 Next Steps - Add to GitHub Secrets" -ForegroundColor Cyan
Write-Host "================================================`n" -ForegroundColor Cyan

Write-Host "1️⃣  Go to GitHub Secrets:" -ForegroundColor White
Write-Host "   https://github.com/Naveenkumar-2007/Daibetes/settings/secrets/actions`n" -ForegroundColor Blue

Write-Host "2️⃣  Click 'New repository secret'`n" -ForegroundColor White

Write-Host "3️⃣  Add the secret:" -ForegroundColor White
Write-Host "   Name:  " -NoNewline
Write-Host "AZURE_WEBAPP_PUBLISH_PROFILE" -ForegroundColor Yellow
if ($fileName) {
    Write-Host "   Value: [Paste from $fileName or clipboard]" -ForegroundColor Gray
} else {
    Write-Host "   Value: [Paste from clipboard]" -ForegroundColor Gray
}
Write-Host ""

Write-Host "4️⃣  Click 'Add secret'`n" -ForegroundColor White

Write-Host "5️⃣  Verify and Deploy:" -ForegroundColor White
Write-Host "   git add ." -ForegroundColor Gray
Write-Host "   git commit -m 'Fix: Update Azure deployment configuration'" -ForegroundColor Gray
Write-Host "   git push origin main`n" -ForegroundColor Gray

Write-Host "================================================" -ForegroundColor Cyan
Write-Host "🔍 Troubleshooting" -ForegroundColor Cyan
Write-Host "================================================`n" -ForegroundColor Cyan

Write-Host "If deployment still fails:" -ForegroundColor Yellow
Write-Host "  • Verify secret name is exactly: AZURE_WEBAPP_PUBLISH_PROFILE" -ForegroundColor White
Write-Host "  • Ensure you copied the ENTIRE XML (including <?xml...>)" -ForegroundColor White
Write-Host "  • Check workflow file has: slot-name: 'production'" -ForegroundColor White
Write-Host "  • Verify app name matches in .github/workflows/azure-deploy.yml" -ForegroundColor White
Write-Host ""

Write-Host "Monitor deployment:" -ForegroundColor Yellow
Write-Host "  • GitHub Actions: https://github.com/Naveenkumar-2007/Daibetes/actions" -ForegroundColor White
Write-Host "  • Azure Portal: https://portal.azure.com" -ForegroundColor White
Write-Host ""

Write-Host "✅ Ready to deploy! Push to GitHub when ready.`n" -ForegroundColor Green
