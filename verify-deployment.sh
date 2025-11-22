#!/bin/bash

# Azure Deployment Verification Script
# Run this after deployment to verify everything is working

set -e

# Configuration
WEBAPP_NAME="${AZURE_WEBAPP_NAME:-diabetes-predictor-ai}"
RESOURCE_GROUP="${RESOURCE_GROUP:-diabetes-predictor-rg}"
APP_URL="https://${WEBAPP_NAME}.azurewebsites.net"

echo "🔍 Azure Deployment Verification"
echo "=================================="
echo ""

# Check if logged in
echo "1. Checking Azure login status..."
if ! az account show &> /dev/null; then
    echo "❌ Not logged into Azure. Run: az login"
    exit 1
fi
echo "✅ Azure CLI authenticated"
echo ""

# Check Web App exists
echo "2. Checking Web App existence..."
if ! az webapp show --resource-group "$RESOURCE_GROUP" --name "$WEBAPP_NAME" &> /dev/null; then
    echo "❌ Web App not found: $WEBAPP_NAME"
    echo "   Create it first in Azure Portal or using Azure CLI"
    exit 1
fi
echo "✅ Web App found: $WEBAPP_NAME"
echo ""

# Check Web App status
echo "3. Checking Web App status..."
STATUS=$(az webapp show --resource-group "$RESOURCE_GROUP" --name "$WEBAPP_NAME" --query "state" -o tsv)
if [ "$STATUS" != "Running" ]; then
    echo "⚠️  Web App status: $STATUS (expected: Running)"
else
    echo "✅ Web App is running"
fi
echo ""

# Check environment variables
echo "4. Checking critical environment variables..."
REQUIRED_VARS=("GROQ_API_KEY" "FIREBASE_PROJECT_ID" "SECRET_KEY")
MISSING_VARS=()

for VAR in "${REQUIRED_VARS[@]}"; do
    if ! az webapp config appsettings list -g "$RESOURCE_GROUP" -n "$WEBAPP_NAME" --query "[?name=='$VAR'].value" -o tsv | grep -q .; then
        MISSING_VARS+=("$VAR")
        echo "❌ Missing: $VAR"
    else
        echo "✅ Set: $VAR"
    fi
done

if [ ${#MISSING_VARS[@]} -gt 0 ]; then
    echo ""
    echo "⚠️  Missing environment variables: ${MISSING_VARS[*]}"
    echo "   Set them in Azure Portal: Configuration > Application settings"
fi
echo ""

# Test HTTP endpoint
echo "5. Testing HTTP endpoint..."
HTTP_CODE=$(curl -s -o /dev/null -w "%{http_code}" "$APP_URL" || echo "000")
if [ "$HTTP_CODE" = "200" ] || [ "$HTTP_CODE" = "302" ]; then
    echo "✅ Application responding (HTTP $HTTP_CODE)"
else
    echo "⚠️  Application returned HTTP $HTTP_CODE"
    echo "   Check logs: az webapp log tail -g $RESOURCE_GROUP -n $WEBAPP_NAME"
fi
echo ""

# Check deployment history
echo "6. Checking recent deployments..."
LAST_DEPLOYMENT=$(az webapp deployment list --resource-group "$RESOURCE_GROUP" --name "$WEBAPP_NAME" --query "[0].{time:start_time,status:status}" -o table 2>/dev/null || echo "No deployments found")
echo "$LAST_DEPLOYMENT"
echo ""

# Check logs for errors
echo "7. Checking recent logs for errors..."
echo "   (Last 50 lines, filtered for errors)"
az webapp log download --resource-group "$RESOURCE_GROUP" --name "$WEBAPP_NAME" --log-file app_logs.zip &> /dev/null || true
if [ -f app_logs.zip ]; then
    unzip -q -o app_logs.zip 2>/dev/null || true
    if [ -f LogFiles/Application/*.log ]; then
        tail -n 50 LogFiles/Application/*.log 2>/dev/null | grep -i "error\|exception\|failed" || echo "✅ No errors found in recent logs"
    fi
    rm -rf LogFiles app_logs.zip 2>/dev/null
else
    echo "⚠️  Could not download logs"
fi
echo ""

# Summary
echo "=================================="
echo "📊 Verification Summary"
echo "=================================="
echo "App Name: $WEBAPP_NAME"
echo "Resource Group: $RESOURCE_GROUP"
echo "URL: $APP_URL"
echo "Status: $STATUS"
echo ""

if [ ${#MISSING_VARS[@]} -eq 0 ] && [ "$STATUS" = "Running" ] && ([ "$HTTP_CODE" = "200" ] || [ "$HTTP_CODE" = "302" ]); then
    echo "✅ Deployment looks healthy!"
else
    echo "⚠️  Some issues detected. Review the output above."
fi

echo ""
echo "🔗 Quick links:"
echo "   - Azure Portal: https://portal.azure.com"
echo "   - Application: $APP_URL"
echo "   - Logs: az webapp log tail -g $RESOURCE_GROUP -n $WEBAPP_NAME"
