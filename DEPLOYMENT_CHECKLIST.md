# 🚀 Azure Deployment Checklist

Use this checklist to ensure a successful deployment to Azure.

## Pre-Deployment

### 1. Prerequisites
- [ ] Azure account created ([Sign up](https://azure.microsoft.com/free/))
- [ ] GitHub account with repository access
- [ ] All API keys and credentials ready
  - [ ] GROQ API key
  - [ ] Firebase credentials
  - [ ] SMTP credentials (if using email)
  - [ ] Google OAuth credentials (if using)

### 2. Local Testing
- [ ] Application runs locally without errors
- [ ] All dependencies in `requirements.txt` are up to date
- [ ] Frontend builds successfully (`cd frontend && npm run build`)
- [ ] Environment variables documented
- [ ] No hardcoded secrets in code

### 3. Code Preparation
- [ ] All changes committed to Git
- [ ] Code pushed to GitHub main branch
- [ ] `.github/workflows/azure-deploy.yml` exists
- [ ] `startup.sh` has correct permissions (`chmod +x startup.sh`)
- [ ] `requirements.txt` includes all Python packages

## Azure Setup

### 4. Create Azure Resources
- [ ] Created Azure Web App (B1 or higher recommended)
  - [ ] App Name: `diabetes-predictor-ai` (or your custom name)
  - [ ] Runtime: Python 3.11
  - [ ] Region: Nearest to users
  - [ ] Pricing tier selected
- [ ] Resource group created: `diabetes-predictor-rg`

### 5. Configure Azure Web App
- [ ] Set all environment variables in Configuration > Application settings:
  - [ ] `GROQ_API_KEY`
  - [ ] `FIREBASE_API_KEY`
  - [ ] `FIREBASE_PROJECT_ID`
  - [ ] `FIREBASE_CLIENT_EMAIL`
  - [ ] `FIREBASE_STORAGE_BUCKET`
  - [ ] `FIREBASE_DATABASE_URL`
  - [ ] `FIREBASE_SERVICE_ACCOUNT_JSON`
  - [ ] `SECRET_KEY`
  - [ ] `SMTP_HOST` (if using email)
  - [ ] `SMTP_USERNAME`
  - [ ] `SMTP_PASSWORD`
  - [ ] `SMTP_PORT`
  - [ ] `SMTP_FROM_EMAIL`
  - [ ] Other custom variables
- [ ] Saved configuration
- [ ] Web App restarted

### 6. Configure Deployment
- [ ] Downloaded publish profile from Azure Portal
- [ ] Added `AZURE_WEBAPP_PUBLISH_PROFILE` to GitHub Secrets
- [ ] Updated `AZURE_WEBAPP_NAME` in `.github/workflows/azure-deploy.yml`
- [ ] GitHub Actions has necessary permissions

## Deployment

### 7. First Deployment
- [ ] Pushed code to GitHub main branch
- [ ] Verified GitHub Actions workflow started
- [ ] Monitored workflow in Actions tab
- [ ] Build stage completed successfully
- [ ] Deploy stage completed successfully
- [ ] No errors in workflow logs

### 8. Verify Deployment
- [ ] Application URL accessible (`https://your-app.azurewebsites.net`)
- [ ] Homepage loads without errors
- [ ] Login/registration works
- [ ] Prediction functionality works
- [ ] Report generation works
- [ ] Static files (CSS/JS) loading correctly
- [ ] No 404 errors in browser console

### 9. Monitor & Test
- [ ] Checked Azure logs for errors
  - Run: `az webapp log tail -g diabetes-predictor-rg -n diabetes-predictor-ai`
- [ ] Tested all major features:
  - [ ] User registration
  - [ ] User login
  - [ ] Password reset
  - [ ] Make prediction
  - [ ] View history
  - [ ] Generate report
  - [ ] Admin panel (if applicable)
- [ ] Verified database connections
- [ ] Checked API integrations

## Post-Deployment

### 10. Monitoring Setup
- [ ] Enabled Application Insights (recommended)
- [ ] Set up log streaming
- [ ] Configured alerts for errors/downtime
- [ ] Bookmarked Azure Portal dashboard

### 11. Performance
- [ ] Application responds within acceptable time
- [ ] No cold start issues (if using B1+)
- [ ] Static files cached properly
- [ ] Database queries optimized

### 12. Security
- [ ] HTTPS-only enabled
- [ ] No secrets exposed in logs
- [ ] CORS configured correctly
- [ ] Firebase security rules reviewed
- [ ] Authentication working properly

### 13. Documentation
- [ ] Updated README with deployment info
- [ ] Documented environment variables
- [ ] Created runbook for common issues
- [ ] Shared credentials securely with team

## Optional Enhancements

### 14. Production Improvements
- [ ] Custom domain configured
- [ ] SSL certificate installed
- [ ] Azure CDN setup for static files
- [ ] Azure Key Vault for secrets
- [ ] Backup and disaster recovery configured
- [ ] Scaling rules configured
- [ ] Cost alerts set up

### 15. CI/CD Enhancements
- [ ] Added automated tests to pipeline
- [ ] Configured staging environment
- [ ] Set up deployment slots (blue-green deployment)
- [ ] Added manual approval gates

## Troubleshooting

If deployment fails, check:

1. **Build Errors**
   - [ ] Review GitHub Actions logs
   - [ ] Check `requirements.txt` for missing packages
   - [ ] Verify Python version compatibility
   - [ ] Check frontend build errors

2. **Deployment Errors**
   - [ ] Verify publish profile is correct
   - [ ] Check Azure Web App status in Portal
   - [ ] Review deployment logs in Azure
   - [ ] Verify app name matches in workflow

3. **Runtime Errors**
   - [ ] Check application logs in Azure
   - [ ] Verify all environment variables set
   - [ ] Test database/API connections
   - [ ] Check startup command configuration

4. **Application Not Responding**
   - [ ] Wait 5-10 minutes for first deployment
   - [ ] Restart Web App in Azure Portal
   - [ ] Check if port 8000 is configured
   - [ ] Review Gunicorn logs

## Success Criteria

✅ **Deployment is successful when:**
- Application URL is accessible
- All features work as expected
- No errors in logs
- Performance is acceptable
- Monitoring is active
- Team has access to logs and portal

---

## Quick Commands

```bash
# View logs
az webapp log tail -g diabetes-predictor-rg -n diabetes-predictor-ai

# Restart app
az webapp restart -g diabetes-predictor-rg -n diabetes-predictor-ai

# Check status
az webapp show -g diabetes-predictor-rg -n diabetes-predictor-ai --query "state"

# Run verification script
bash verify-deployment.sh
```

---

**Date Completed:** _______________

**Deployed By:** _______________

**App URL:** https://_______________

**Notes:**
