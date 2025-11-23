# Quick Status Check
Write-Host "🔍 Checking Deployment Status..." -ForegroundColor Cyan
Write-Host ""

# GitHub Actions
Write-Host "📊 GitHub Actions:" -ForegroundColor Yellow
Write-Host "   https://github.com/Naveenkumar-2007/Daibetes/actions" -ForegroundColor White
Write-Host ""

# App State
Write-Host "🌐 App State:" -ForegroundColor Yellow
$state = az webapp show --name diabetes-predictor-ai --resource-group diabetes-predictor-rg --query "state" --output tsv 2>$null
if ($state) {
    Write-Host "   State: $state" -ForegroundColor $(if ($state -eq "Running") {"Green"} else {"Red"})
} else {
    Write-Host "   Error checking state" -ForegroundColor Red
}

# Runtime
$runtime = az webapp config show --name diabetes-predictor-ai --resource-group diabetes-predictor-rg --query "linuxFxVersion" --output tsv 2>$null
Write-Host "   Runtime: $runtime" -ForegroundColor White

# Startup Command
$startup = az webapp config show --name diabetes-predictor-ai --resource-group diabetes-predictor-rg --query "appCommandLine" --output tsv 2>$null
Write-Host "   Startup: $startup" -ForegroundColor Gray
Write-Host ""

# Quick HTTP Test
Write-Host "🌍 Testing Endpoint:" -ForegroundColor Yellow
try {
    $response = Invoke-WebRequest -Uri "https://diabetes-predictor-ai.azurewebsites.net" -Method Head -TimeoutSec 5 -ErrorAction Stop
    Write-Host "   ✅ HTTP $($response.StatusCode) - App is responding!" -ForegroundColor Green
} catch {
    Write-Host "   ❌ Error: $($_.Exception.Response.StatusCode.value__) - $($_.Exception.Message)" -ForegroundColor Red
}
Write-Host ""

Write-Host "📋 Commands:" -ForegroundColor Yellow
Write-Host "   View logs:    az webapp log tail --name diabetes-predictor-ai --resource-group diabetes-predictor-rg" -ForegroundColor Gray
Write-Host "   Monitor:      .\monitor-deployment.ps1" -ForegroundColor Gray
Write-Host "   Verify:       .\verify-deployment.ps1" -ForegroundColor Gray
