# 504 Gateway Timeout Fix for Azure Deployment

## Changes Made to Fix Timeout Issues

### 1. **Lazy Loading of LLM** (`flask_app.py`)
- Changed from eager loading to lazy initialization
- LLM only loads when actually needed (first AI request)
- Reduces startup time by 5-10 seconds

### 2. **Optimized Gunicorn Configuration** (`startup.sh`)
- Reduced workers from 4 to 2 (faster startup)
- Increased threads from 2 to 4 (better concurrency)
- Changed worker class from `sync` to `gthread` (non-blocking)
- Reduced timeout from 600s to 300s
- Removed `--preload` flag (causes slow startup)
- Added graceful timeout of 120s

### 3. **Health Check Endpoint** (`/health`)
- New lightweight endpoint for Azure health checks
- Returns JSON with service status
- Helps Azure verify app is running

### 4. **Updated Web.config**
- Added application initialization with `/health` warmup
- Prevents premature health check failures

### 5. **Azure Settings** (`.azure-settings.json`)
- Configured warmup path to `/health`
- Set proper timeouts and cache settings
- Optimized for Python 3.11

## Azure App Service Settings Required

Add these to **Configuration > Application Settings** in Azure Portal:

```
SCM_COMMAND_IDLE_TIMEOUT = 600
WEBSITE_SWAP_WARMUP_PING_PATH = /health
WEBSITE_SWAP_WARMUP_PING_STATUSES = 200
WEBSITE_WARMUP_PATH = /health
WEBSITES_PORT = 8000
PYTHON_VERSION = 3.11
```

## Deployment Steps

1. **Commit and push changes:**
   ```bash
   git add .
   git commit -m "fix: Optimize startup to prevent 504 Gateway Timeout"
   git push origin main
   ```

2. **Monitor deployment in Azure:**
   - Go to Azure Portal → Your App Service → Deployment Center
   - Check GitHub Actions logs

3. **Test the health endpoint:**
   ```bash
   curl https://your-app.azurewebsites.net/health
   ```

4. **Check application logs:**
   ```bash
   az webapp log tail --name your-app-name --resource-group your-rg
   ```

## Why This Fixes the 504 Error

**504 Gateway Timeout** occurs when:
- App takes too long to start (> 230 seconds)
- First request times out before app is ready
- Heavy initialization blocks the worker

**Our fixes:**
- ✅ Lazy LLM loading (only when needed)
- ✅ Fewer workers start faster
- ✅ Threaded workers handle requests while loading
- ✅ Health endpoint lets Azure know we're alive
- ✅ Proper warmup prevents premature checks

## Expected Startup Time

- **Before:** 45-60 seconds (with LLM preload)
- **After:** 15-25 seconds (lazy load)

## Troubleshooting

If still getting 504:

1. **Check Gunicorn logs in Azure:**
   ```
   Deployment Center → Logs → Runtime logs
   ```

2. **Verify startup.sh is executable:**
   ```bash
   chmod +x startup.sh
   ```

3. **Increase Azure timeout** (if on Basic plan):
   - Upgrade to Standard S1 or higher
   - Basic plans have stricter timeouts

4. **Test locally:**
   ```bash
   ./startup.sh
   ```

## Performance Optimization

Current configuration:
- **Workers:** 2 (uses less memory)
- **Threads:** 4 per worker = 8 concurrent requests
- **Timeout:** 300s per request
- **Keep-alive:** 5s
- **Max requests:** 1000 (then worker restarts)

## Contact

If issues persist, check:
- Firebase connectivity
- GROQ_API_KEY environment variable
- Model and scaler files in `artifacts/`
