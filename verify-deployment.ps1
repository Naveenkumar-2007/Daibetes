# Quick Deployment Verification Script
# Run this after deployment completes

Write-Host "🔍 Azure Web App Deployment Verification" -ForegroundColor Cyan
Write-Host "=========================================" -ForegroundColor Cyan
Write-Host ""

# 1. Check app state
Write-Host "1️⃣ Checking app state..." -ForegroundColor Yellow
$state = az webapp show --name diabetes-predictor-ai --resource-group diabetes-predictor-rg --query "state" --output tsv
if ($state -eq "Running") {
    Write-Host "   ✅ App is RUNNING" -ForegroundColor Green
} else {
    Write-Host "   ❌ App state: $state" -ForegroundColor Red
}
Write-Host ""

# 2. Check latest deployment
Write-Host "2️⃣ Checking latest deployment..." -ForegroundColor Yellow
$deployment = az webapp deployment list --name diabetes-predictor-ai --resource-group diabetes-predictor-rg --query "[0].{status:status, message:message, id:id}" --output json | ConvertFrom-Json
Write-Host "   Status: $($deployment.status)" -ForegroundColor $(if ($deployment.status -eq "Success") { "Green" } else { "Red" })
Write-Host "   Message: $($deployment.message)" -ForegroundColor White
Write-Host ""

# 3. Test HTTP endpoint
Write-Host "3️⃣ Testing HTTP endpoint..." -ForegroundColor Yellow
try {
    $response = Invoke-WebRequest -Uri "https://diabetes-predictor-ai.azurewebsites.net" -Method Head -TimeoutSec 10 -ErrorAction Stop
    Write-Host "   ✅ HTTP Status: $($response.StatusCode)" -ForegroundColor Green
} catch {
    Write-Host "   ⚠️ HTTP Error: $($_.Exception.Message)" -ForegroundColor Yellow
}
Write-Host ""

# 4. Check for common issues
Write-Host "4️⃣ Checking app settings..." -ForegroundColor Yellow
$settings = az webapp config appsettings list --name diabetes-predictor-ai --resource-group diabetes-predictor-rg --query "[?name=='SCM_DO_BUILD_DURING_DEPLOYMENT' || name=='GOOGLE_CLIENT_ID' || name=='GROQ_API_KEY'].{Name:name, Value:value}" --output json | ConvertFrom-Json

foreach ($setting in $settings) {
    if ($setting.Name -eq "SCM_DO_BUILD_DURING_DEPLOYMENT") {
        if ($setting.Value -eq "false") {
            Write-Host "   ✅ Build disabled (good)" -ForegroundColor Green
        } else {
            Write-Host "   ⚠️ Build is enabled (may cause timeout)" -ForegroundColor Yellow
        }
    }
    if ($setting.Name -eq "GOOGLE_CLIENT_ID") {
        if ($setting.Value) {
            Write-Host "   ✅ Google OAuth configured" -ForegroundColor Green
        } else {
            Write-Host "   ⚠️ Google OAuth NOT configured" -ForegroundColor Yellow
        }
    }
    if ($setting.Name -eq "GROQ_API_KEY") {
        if ($setting.Value) {
            Write-Host "   ✅ GROQ API key configured" -ForegroundColor Green
        } else {
            Write-Host "   ⚠️ GROQ API key NOT configured" -ForegroundColor Yellow
        }
    }
}
Write-Host ""

# 5. Summary
Write-Host "📋 Summary" -ForegroundColor Cyan
Write-Host "=========================================" -ForegroundColor Cyan
Write-Host "App URL: https://diabetes-predictor-ai.azurewebsites.net" -ForegroundColor White
Write-Host "GitHub Actions: https://github.com/Naveenkumar-2007/Daibetes/actions" -ForegroundColor White
Write-Host ""

# 6. Next steps
Write-Host "📝 Next Steps:" -ForegroundColor Yellow
if (-not $settings.GOOGLE_CLIENT_ID) {
    Write-Host "• Configure Google OAuth credentials" -ForegroundColor White
}
if (-not $settings.GROQ_API_KEY) {
    Write-Host "• Set GROQ_API_KEY in App Settings" -ForegroundColor White
}
Write-Host "• Test the application thoroughly" -ForegroundColor White
Write-Host ""

Write-Host "💡 To view live logs:" -ForegroundColor Yellow
Write-Host "   az webapp log tail --name diabetes-predictor-ai --resource-group diabetes-predictor-rg" -ForegroundColor Gray
