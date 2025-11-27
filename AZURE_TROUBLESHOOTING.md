# Azure Deployment Troubleshooting Guide

## Common Issues and Solutions

### 1. HTTP 403 Forbidden Error

**Symptoms:**
- App returns 403 status code
- Cannot access the website
- "Access Denied" message

**Causes & Solutions:**

#### A. Authentication/CORS Issues
```bash
# Check if CORS is properly configured
# In flask_app.py, ensure:
CORS(app, supports_credentials=True, origins=allowed_origins)
```

#### B. App Service Authentication Enabled
```bash
# Check authentication settings
az webapp auth show --name diabetes-predictor-ai --resource-group diabetes-predictor-rg

# Disable if not needed
az webapp auth update --name diabetes-predictor-ai \
  --resource-group diabetes-predictor-rg \
  --enabled false
```

#### C. IP Restrictions
```bash
# Check access restrictions
az webapp config access-restriction show \
  --name diabetes-predictor-ai \
  --resource-group diabetes-predictor-rg

# Remove all restrictions (use cautiously in production)
az webapp config access-restriction remove \
  --name diabetes-predictor-ai \
  --resource-group diabetes-predictor-rg \
  --rule-name AllowAll
```

### 2. Slow Startup / Gateway Timeout

**Symptoms:**
- App takes >2 minutes to start
- 504 Gateway Timeout errors
- Health check fails

**Solutions:**

#### A. Optimize Gunicorn Configuration
```bash
# Current optimized settings in startup.sh:
--workers=1              # Single worker for fast startup
--threads=8              # More threads for concurrency
--timeout=120            # Reduced from 300
--worker-tmp-dir=/dev/shm  # Use shared memory for faster I/O
```

#### B. Enable Always On
```bash
# Prevent cold starts
az webapp config set \
  --name diabetes-predictor-ai \
  --resource-group diabetes-predictor-rg \
  --always-on true
```

#### C. Scale Up App Service Plan
```bash
# Check current plan
az appservice plan show \
  --name diabetes-predictor-plan \
  --resource-group diabetes-predictor-rg

# Upgrade to B2 or higher for better performance
az appservice plan update \
  --name diabetes-predictor-plan \
  --resource-group diabetes-predictor-rg \
  --sku B2
```

### 3. Firebase Authentication Errors

**Symptoms:**
- "Firebase 401 Unauthorized"
- Data not saving/loading
- Using local JSON fallback

**Solutions:**

#### A. Update Firebase Realtime Database Rules
1. Go to Firebase Console: https://console.firebase.google.com
2. Select project: diabetes-prediction-22082
3. Navigate to: Realtime Database > Rules
4. Update rules to:
```json
{
  "rules": {
    ".read": true,
    ".write": true
  }
}
```
⚠️ **Note:** This is for development. In production, implement proper security rules.

#### B. Configure Service Account (Alternative)
```bash
# Set Firebase service account in Azure
az webapp config appsettings set \
  --name diabetes-predictor-ai \
  --resource-group diabetes-predictor-rg \
  --settings FIREBASE_SERVICE_ACCOUNT_JSON='<your-service-account-json>'
```

### 4. Missing Environment Variables

**Check if all required variables are set:**

```bash
# List all app settings
az webapp config appsettings list \
  --name diabetes-predictor-ai \
  --resource-group diabetes-predictor-rg \
  --output table

# Required variables:
# - GROQ_API_KEY
# - PINECONE_API_KEY
# - FIREBASE_API_KEY
# - FIREBASE_PROJECT_ID
# - FIREBASE_DATABASE_URL
# - All other Firebase variables from GitHub secrets
```

**Set missing variables:**
```bash
az webapp config appsettings set \
  --name diabetes-predictor-ai \
  --resource-group diabetes-predictor-rg \
  --settings \
    GROQ_API_KEY="your-key-here" \
    PINECONE_API_KEY="your-key-here"
```

### 5. Deployment Verification

**Check deployment logs:**
```bash
# View real-time logs
az webapp log tail \
  --name diabetes-predictor-ai \
  --resource-group diabetes-predictor-rg

# Download logs
az webapp log download \
  --name diabetes-predictor-ai \
  --resource-group diabetes-predictor-rg \
  --log-file logs.zip
```

**Test endpoints:**
```bash
# Health check
curl https://diabetes-predictor-ai.azurewebsites.net/health

# Expected response:
# {
#   "status": "healthy",
#   "timestamp": "...",
#   "firebase": true,
#   "model_loaded": true,
#   "scaler_loaded": true
# }
```

### 6. React Frontend Not Loading

**Symptoms:**
- Blank page
- 404 on routes
- Static files not found

**Solutions:**

#### A. Verify Frontend Build
```bash
# Check if frontend was built in workflow
# Look for: "Build React Frontend" step in Actions

# Manually rebuild if needed:
cd frontend
npm install
npm run build

# Copy to static folder
mkdir -p ../static/app
cp -r dist/* ../static/app/
```

#### B. Check Static File Configuration
```bash
# Ensure web.config has static file mappings
# Or use Azure static files configuration
az webapp config set \
  --name diabetes-predictor-ai \
  --resource-group diabetes-predictor-rg \
  --use-32bit-worker-process false
```

## Quick Diagnostic Commands

```bash
# 1. Check app status
az webapp show \
  --name diabetes-predictor-ai \
  --resource-group diabetes-predictor-rg \
  --query state

# 2. Check current plan/SKU
az appservice plan show \
  --name diabetes-predictor-plan \
  --resource-group diabetes-predictor-rg \
  --query "{name:name, sku:sku.name, tier:sku.tier}"

# 3. Restart the app
az webapp restart \
  --name diabetes-predictor-ai \
  --resource-group diabetes-predictor-rg

# 4. View deployment history
az webapp deployment list \
  --name diabetes-predictor-ai \
  --resource-group diabetes-predictor-rg \
  --output table

# 5. SSH into container (if Linux App Service)
az webapp ssh \
  --name diabetes-predictor-ai \
  --resource-group diabetes-predictor-rg
```

## Performance Optimization

### 1. Enable Application Insights
```bash
az monitor app-insights component create \
  --app diabetes-predictor-insights \
  --location eastus \
  --resource-group diabetes-predictor-rg

# Link to web app
INSTRUMENTATION_KEY=$(az monitor app-insights component show \
  --app diabetes-predictor-insights \
  --resource-group diabetes-predictor-rg \
  --query instrumentationKey -o tsv)

az webapp config appsettings set \
  --name diabetes-predictor-ai \
  --resource-group diabetes-predictor-rg \
  --settings APPINSIGHTS_INSTRUMENTATIONKEY=$INSTRUMENTATION_KEY
```

### 2. Enable CDN for Static Assets (Optional)
```bash
# Create CDN profile
az cdn profile create \
  --name diabetes-predictor-cdn \
  --resource-group diabetes-predictor-rg \
  --sku Standard_Microsoft

# Add CDN endpoint
az cdn endpoint create \
  --name diabetes-predictor-endpoint \
  --profile-name diabetes-predictor-cdn \
  --resource-group diabetes-predictor-rg \
  --origin diabetes-predictor-ai.azurewebsites.net
```

## Contact & Support

For urgent issues:
1. Check GitHub Actions logs: https://github.com/Naveenkumar-2007/Daibetes/actions
2. View Azure Portal: https://portal.azure.com
3. Monitor Firebase Console: https://console.firebase.google.com

## Common Error Codes

| Code | Meaning | Common Fix |
|------|---------|------------|
| 403 | Forbidden | Check authentication/CORS |
| 404 | Not Found | Verify deployment & routing |
| 500 | Server Error | Check logs for Python errors |
| 502 | Bad Gateway | App crashed - check startup.sh |
| 503 | Unavailable | App starting or overloaded |
| 504 | Gateway Timeout | Increase timeout, optimize startup |

## Success Checklist

✅ Health endpoint returns 200  
✅ Homepage loads (200 or 302)  
✅ Firebase connected or local storage working  
✅ ML model loaded successfully  
✅ React frontend displays  
✅ Can create user account  
✅ Can make predictions  
✅ Can view dashboard  

---

**Last Updated:** November 28, 2025  
**Deployment:** Azure Web App (Linux, Python 3.11)
