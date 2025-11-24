# Firebase Database Setup Guide

## ✅ Current Status
Your Firebase Realtime Database is partially configured:
- **Database URL**: `https://diabetes-prediction-22082-default-rtdb.firebaseio.com`
- **Project ID**: `diabetes-prediction-22082`
- **Mode**: REST API (fallback mode - works but limited)

## 🎯 Goal
Set up Firebase Admin SDK for full database functionality including user authentication.

---

## Option 1: Use Firebase Service Account (RECOMMENDED)

### Step 1: Get Firebase Service Account JSON

1. **Go to Firebase Console**:
   - Visit: https://console.firebase.google.com/
   - Select project: `diabetes-prediction-22082`

2. **Navigate to Project Settings**:
   - Click the gear icon ⚙️ (top left)
   - Click **Project Settings**

3. **Go to Service Accounts Tab**:
   - Click **Service accounts** tab
   - Click **Generate new private key**
   - Click **Generate key** (downloads JSON file)

4. **You'll get a JSON file like this**:
   ```json
   {
     "type": "service_account",
     "project_id": "diabetes-prediction-22082",
     "private_key_id": "abc123...",
     "private_key": "-----BEGIN PRIVATE KEY-----\nXXXX...\n-----END PRIVATE KEY-----\n",
     "client_email": "firebase-adminsdk-xxxxx@diabetes-prediction-22082.iam.gserviceaccount.com",
     "client_id": "123456789",
     "auth_uri": "https://accounts.google.com/o/oauth2/auth",
     "token_uri": "https://oauth2.googleapis.com/token",
     "auth_provider_x509_cert_url": "https://www.googleapis.com/oauth2/v1/certs",
     "client_x509_cert_url": "https://www.googleapis.com/robot/v1/metadata/x509/firebase-adminsdk-xxxxx%40diabetes-prediction-22082.iam.gserviceaccount.com"
   }
   ```

### Step 2: Add to Azure App Settings

**Method A: Using PowerShell (EASIER)**

```powershell
# Read the JSON file content
$firebaseJson = Get-Content -Path "path\to\your\firebase-service-account.json" -Raw

# Escape quotes for Azure
$firebaseJsonEscaped = $firebaseJson -replace '"', '\"'

# Set as environment variable in Azure
az webapp config appsettings set `
  --name diabetes-predictor-ai `
  --resource-group diabetes-predictor-rg `
  --settings FIREBASE_SERVICE_ACCOUNT_JSON="$firebaseJsonEscaped"
```

**Method B: Using Azure Portal (IF PowerShell fails)**

1. Go to Azure Portal: https://portal.azure.com
2. Navigate to: **diabetes-predictor-ai** App Service
3. Click **Configuration** (left menu)
4. Click **+ New application setting**
5. Name: `FIREBASE_SERVICE_ACCOUNT_JSON`
6. Value: Paste the ENTIRE contents of the JSON file (as-is)
7. Click **OK** then **Save**

### Step 3: Restart Azure Web App

```powershell
az webapp restart --name diabetes-predictor-ai --resource-group diabetes-predictor-rg
```

### Step 4: Verify Connection

```powershell
curl.exe https://diabetes-predictor-ai.azurewebsites.net/health
```

You should see:
```json
{
  "status": "healthy",
  "model_loaded": true,
  "llm_available": false,
  "database_connected": true,
  "firebase_mode": "Admin_SDK"
}
```

---

## Option 2: Use Firebase REST API (CURRENT - LIMITED)

This is what's running now. It works but:
- ❌ No server-side authentication
- ❌ Requires open database rules
- ✅ Simple, no credentials needed
- ⚠️ Less secure

### Current Configuration
The REST API mode is active and uses:
- Database URL: `https://diabetes-prediction-22082-default-rtdb.firebaseio.com`
- No authentication
- Direct HTTP requests to Firebase

### Make it Work Better
Ensure your Firebase Realtime Database rules allow access:

1. Go to Firebase Console → Realtime Database
2. Click **Rules** tab
3. Use these rules (TEMPORARY - for testing):
   ```json
   {
     "rules": {
       ".read": true,
       ".write": true
     }
   }
   ```
   ⚠️ **WARNING**: This allows anyone to read/write. Use only for testing!

4. Better rules (after testing):
   ```json
   {
     "rules": {
       "users": {
         ".read": true,
         ".write": true
       },
       "predictions": {
         ".read": true,
         ".write": true
       },
       "patient_data": {
         ".read": true,
         ".write": true
       }
     }
   }
   ```

---

## Option 3: Switch to Firestore (ALTERNATIVE)

If Realtime Database doesn't work, you can use Firestore instead.

### Enable Firestore
1. Go to Firebase Console
2. Click **Firestore Database** (left menu)
3. Click **Create database**
4. Choose **Production mode**
5. Select region: `us-central1` or closest to you

### Update Firestore Rules
```
rules_version = '2';
service cloud.firestore {
  match /databases/{database}/documents {
    match /users/{userId} {
      allow read, write: if true;
    }
    match /predictions/{predictionId} {
      allow read, write: if true;
    }
  }
}
```

### Update Code
The code already supports Firestore via `db.collection()` syntax!

---

## 🔍 Troubleshooting

### Issue: "Database connection not available"
**Cause**: Firebase not initialized

**Solution**:
1. Check Azure logs: `az webapp log tail --name diabetes-predictor-ai --resource-group diabetes-predictor-rg`
2. Look for:
   - ✅ "✅ Firebase Admin SDK connected!"
   - ✅ "🔥 Using Firebase REST API"
   - ❌ "⚠️ Admin SDK error"
3. If errors, verify service account JSON is valid

---

### Issue: 401 Unauthorized on login
**Causes**:
1. Database not connected
2. User doesn't exist in Firebase
3. Session not working

**Solutions**:
1. **Check health endpoint**:
   ```powershell
   curl.exe https://diabetes-predictor-ai.azurewebsites.net/health
   ```
   - `database_connected` should be `true`

2. **Test with admin credentials** (hardcoded):
   - Username: `admin`
   - Password: `admin123`

3. **Create test user via Firebase Console**:
   - Go to Realtime Database
   - Create path: `/users/test_user_123`
   - Add data:
     ```json
     {
       "username": "testuser",
       "email": "test@example.com",
       "password_hash": "5e884898da28047151d0e56f8dc6292773603d0d6aabbdd62a11ef721d1542d8",
       "full_name": "Test User",
       "role": "user",
       "is_active": true,
       "created_at": "2025-11-24T12:00:00"
     }
     ```
     (Password: `password` - SHA-256 hash)

---

### Issue: Google OAuth not working
**See**: `GOOGLE_OAUTH_FIX.md` for complete instructions

**Quick Fix**:
1. Go to Google Cloud Console
2. Add to Authorized JavaScript origins:
   - `https://diabetes-predictor-ai.azurewebsites.net`
3. Add to Authorized redirect URIs:
   - `https://diabetes-predictor-ai.azurewebsites.net/api/login/google`

---

## 📊 Database Structure

Your Firebase Realtime Database should have this structure:

```
diabetes-prediction-22082/
├── users/
│   ├── user_id_123/
│   │   ├── username: "john_doe"
│   │   ├── email: "john@example.com"
│   │   ├── password_hash: "sha256_hash"
│   │   ├── full_name: "John Doe"
│   │   ├── role: "user"
│   │   ├── is_active: true
│   │   ├── created_at: "2025-11-24T..."
│   │   └── predictions: ["pred_001", "pred_002"]
│   └── user_id_456/
│       └── ...
├── predictions/
│   ├── pred_001/
│   │   ├── user_id: "user_id_123"
│   │   ├── patient_name: "John Doe"
│   │   ├── age: 45
│   │   ├── glucose: 120
│   │   ├── prediction: "Low Risk"
│   │   ├── diabetes_risk: 15.5
│   │   └── timestamp: "2025-11-24T..."
│   └── pred_002/
│       └── ...
└── reports/
    ├── report_001/
    │   ├── prediction_id: "pred_001"
    │   ├── pdf_path: "/static/reports/..."
    │   └── generated_at: "2025-11-24T..."
    └── ...
```

---

## ✅ Success Criteria

After setup, you should have:

1. **Health Check Shows**:
   ```json
   {
     "status": "healthy",
     "model_loaded": true,
     "llm_available": true/false,
     "database_connected": true,
     "firebase_mode": "Admin_SDK" or "REST_API"
   }
   ```

2. **Login Works**:
   - Admin login: admin / admin123
   - Regular user login with Firebase credentials
   - Google OAuth login (after Google Console config)

3. **Predictions Save**:
   - Make a prediction
   - Check Firebase Console → Realtime Database
   - Should see new entry under `/predictions/`

4. **Dashboard Loads**:
   - No "Network Error"
   - Shows user stats and recent predictions

---

## 🚀 Quick Start Commands

```powershell
# 1. Set up Firebase service account
az webapp config appsettings set `
  --name diabetes-predictor-ai `
  --resource-group diabetes-predictor-rg `
  --settings FIREBASE_SERVICE_ACCOUNT_JSON="$(Get-Content firebase-service-account.json -Raw)"

# 2. Restart app
az webapp restart --name diabetes-predictor-ai --resource-group diabetes-predictor-rg

# 3. Wait 30 seconds, then test
Start-Sleep -Seconds 30
curl.exe https://diabetes-predictor-ai.azurewebsites.net/health

# 4. Test login (should work with admin credentials)
curl.exe -X POST https://diabetes-predictor-ai.azurewebsites.net/api/login `
  -H "Content-Type: application/json" `
  -d '{\"username\":\"admin\",\"password\":\"admin123\"}'
```

---

## 📞 Need Help?

1. **Check logs**:
   ```powershell
   az webapp log tail --name diabetes-predictor-ai --resource-group diabetes-predictor-rg
   ```

2. **Check health**:
   ```powershell
   curl.exe https://diabetes-predictor-ai.azurewebsites.net/health
   ```

3. **Verify Firebase Console**:
   - https://console.firebase.google.com/
   - Check Realtime Database → Data tab

4. **Read other guides**:
   - `DEPLOYMENT_STATUS.md` - Overall deployment status
   - `GOOGLE_OAUTH_FIX.md` - Google OAuth setup

---

## 🎯 Recommended Next Steps

1. ✅ Set up Firebase service account (Option 1 above)
2. ✅ Restart Azure app
3. ✅ Test health endpoint
4. ✅ Test admin login
5. ⏳ Configure Google OAuth (see GOOGLE_OAUTH_FIX.md)
6. ⏳ Create test user in Firebase
7. ⏳ Test predictions end-to-end
8. ⏳ Fix GROQ LLM (check API key)

Your website is deployed and running! The database connection is the last piece to get authentication working.
