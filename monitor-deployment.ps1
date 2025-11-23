# Azure Deployment Monitor
# Tracks deployment progress and shows logs

param(
    [string]$DeploymentId = "latest",
    [int]$MaxWaitMinutes = 15
)

Write-Host "🔍 Monitoring Azure Deployment..." -ForegroundColor Cyan
Write-Host "App: diabetes-predictor-ai" -ForegroundColor Yellow
Write-Host "Resource Group: diabetes-predictor-rg" -ForegroundColor Yellow
Write-Host ""

$startTime = Get-Date
$timeout = $startTime.AddMinutes($MaxWaitMinutes)

while ((Get-Date) -lt $timeout) {
    Write-Host "⏰ $(Get-Date -Format 'HH:mm:ss') - Checking deployment status..." -ForegroundColor Gray
    
    # Get deployment status
    try {
        $status = az webapp deployment list `
            --resource-group diabetes-predictor-rg `
            --name diabetes-predictor-ai `
            --query "[0].{id:id, status:status, message:message, active:active}" `
            --output json | ConvertFrom-Json
        
        if ($status) {
            Write-Host "📊 Status: $($status.status)" -ForegroundColor Yellow
            Write-Host "📝 Message: $($status.message)" -ForegroundColor White
            Write-Host "🔗 Deployment ID: $($status.id)" -ForegroundColor Gray
            
            if ($status.status -eq "Success" -or $status.active -eq $true) {
                Write-Host ""
                Write-Host "✅ DEPLOYMENT SUCCESSFUL!" -ForegroundColor Green
                Write-Host ""
                Write-Host "🌐 Your app is live at: https://diabetes-predictor-ai.azurewebsites.net" -ForegroundColor Cyan
                Write-Host ""
                Write-Host "📋 Next steps:" -ForegroundColor Yellow
                Write-Host "1. Configure Google OAuth credentials (see AZURE_DEPLOYMENT_COMPLETE.md)" -ForegroundColor White
                Write-Host "2. Set GROQ_API_KEY in App Settings" -ForegroundColor White
                Write-Host "3. Test the application" -ForegroundColor White
                break
            }
            
            if ($status.status -eq "Failed") {
                Write-Host ""
                Write-Host "❌ DEPLOYMENT FAILED!" -ForegroundColor Red
                Write-Host ""
                Write-Host "📋 View logs at:" -ForegroundColor Yellow
                Write-Host "https://diabetes-predictor-ai.scm.azurewebsites.net/api/deployments/$($status.id)/log" -ForegroundColor Cyan
                break
            }
        }
    }
    catch {
        Write-Host "⚠️  Error checking status: $_" -ForegroundColor Red
    }
    
    # Wait before next check
    Start-Sleep -Seconds 15
}

if ((Get-Date) -ge $timeout) {
    Write-Host ""
    Write-Host "⏰ Timeout reached. Deployment is taking longer than expected." -ForegroundColor Yellow
    Write-Host "Check GitHub Actions: https://github.com/Naveenkumar-2007/Daibetes/actions" -ForegroundColor Cyan
}

Write-Host ""
Write-Host "📊 To check app health:" -ForegroundColor Yellow
Write-Host "az webapp show --name diabetes-predictor-ai --resource-group diabetes-predictor-rg --query state" -ForegroundColor White
Write-Host ""
Write-Host "📋 To view live logs:" -ForegroundColor Yellow
Write-Host "az webapp log tail --name diabetes-predictor-ai --resource-group diabetes-predictor-rg" -ForegroundColor White
