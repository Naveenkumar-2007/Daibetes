# 🏥 Diabetes Health Predictor – AI Doctor Portal

[![Deploy to Azure](https://github.com/Naveenkumar-2007/Daibetes/actions/workflows/azure-deploy.yml/badge.svg)](https://github.com/Naveenkumar-2007/Daibetes/actions/workflows/azure-deploy.yml)
[![Azure Status](https://img.shields.io/badge/Azure-Live-success?logo=microsoft-azure)](https://diabetes-predictor-ai.azurewebsites.net)
[![Python](https://img.shields.io/badge/Python-3.11-blue?logo=python)](https://www.python.org/)
[![React](https://img.shields.io/badge/React-20-61dafb?logo=react)](https://reactjs.org/)

A modern, production-ready healthcare application for diabetes risk prediction with ML models and AI-powered medical reports. Built with Flask, React, TypeScript, and Firebase.

**🌐 Live Demo:** [https://diabetes-predictor-ai.azurewebsites.net](https://diabetes-predictor-ai.azurewebsites.net)

## ✨ Features

- **🔐 User Authentication** - Secure login/register with Firebase + password reset
- **📊 Smart Dashboard** - Patient history, trends, and health metrics visualization
- **🤖 ML Prediction** - XGBoost model for accurate diabetes risk assessment
- **📈 Interactive Charts** - Recharts-powered graphs for health data analysis
- **🧠 AI Medical Reports** - Comprehensive 2000+ word reports via Groq LLM (Llama 3.3)
- **📱 Responsive Design** - Modern UI with Tailwind CSS, works on all devices
- **☁️ Azure Deployment** - CI/CD pipeline with GitHub Actions
- **💾 Firebase Database** - Real-time data sync and persistent storage
- **📄 PDF Reports** - Professional medical reports with clinical charts

## 🚀 Quick Start

### Prerequisites

- Python 3.10 or higher
- pip (Python package manager)
- Groq API key ([Get one here](https://console.groq.com/))

### Installation

1. **Clone or navigate to the project directory**
   ```bash
   cd "c:\Users\navee\Cisco Packet Tracer 8.2.2\saves\certificates\Diabetics-Agent"
   ```

2. **(Optional) Create a virtual environment**
   ```bash
   python -m venv .venv
   .venv\Scripts\activate
   ```

3. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

4. **Configure environment variables**
   - Copy `.env.example` to `.env`
   - Add your Groq API key (and any Firebase overrides if needed):
   ```env
   GROQ_API_KEY=your_actual_api_key_here
   ```

5. **Run the Flask application locally**
   ```bash
   python flask_app.py
   ```

6. **Open your browser**
   ```
   http://localhost:5000
   ```

## 📁 Project Structure

```
Diabetics-Agent/
│
├── Dockerfile                # Container definition for Cloud Run
├── .dockerignore             # Build context exclusions
├── flask_app.py              # Main Flask application
├── auth.py                   # Authentication helpers
├── firebase_config.py        # Firebase integration layer
├── requirements.txt          # Production Python dependencies
├── .env.example              # Template for environment variables
├── README.md                 # Project documentation
│
├── templates/               # Jinja templates (landing, dashboard, reports, etc.)
│
├── static/                  # CSS and JavaScript assets
│
├── artifacts/               # ML model artifacts
│   ├── model.pkl
│   ├── scaler.pkl
│   └── proprocessor.pkl
│
├── reports/                 # Generated AI reports (auto-created)
│
├── src/                     # Source code modules
│   ├── data_ingestion.py
│   ├── data_transformation.py
│   ├── model_trainer.py
│   └── utils.py
│
├── data/
│   └── raw/
│       └── diabetes.csv     # Training dataset snapshot
│
├── firebase-service-account.template.json  # Sample service account layout
├── retrain_model.py         # Offline model training script
└── artifacts/model_info.txt # Model metadata

```

## 🐳 Run with Docker

Build the production image and run it locally:

```powershell
docker build -t diabetes-health-predictor .
docker run -p 8080:8080 --env GROQ_API_KEY=your_actual_api_key diabetes-health-predictor
```

The container listens on port `8080` by default (Cloud Run requirement). Override additional environment variables with `--env` flags as needed.

## ☁️ Deploy to Google Cloud Run

1. **Authenticate and choose your project**
   ```powershell
   gcloud auth login
   gcloud config set project YOUR_GCP_PROJECT_ID
   ```
2. **Build and push the container image with Cloud Build**
   ```powershell
   gcloud builds submit --tag gcr.io/YOUR_GCP_PROJECT_ID/diabetes-health-predictor
   ```
3. **Deploy to Cloud Run (fully managed)**
   ```powershell
   gcloud run deploy diabetes-health-predictor \ 
     --image gcr.io/YOUR_GCP_PROJECT_ID/diabetes-health-predictor \ 
     --platform managed \ 
     --region YOUR_REGION \ 
     --allow-unauthenticated \ 
     --set-env-vars GROQ_API_KEY=your_actual_api_key
   ```
4. **Optional: manage secrets securely**
   - Store `GROQ_API_KEY` (and any Firebase credentials) in **Secret Manager**.
   - Replace `--set-env-vars` with `--set-secrets GROQ_API_KEY=projects/.../secrets/...:latest` for runtime secret injection.
   - If you need Firebase Admin SDK, upload `firebase-service-account.json` to Secret Manager and mount it via Cloud Run volume.
5. **Verify deployment** – Cloud Run outputs a service URL; visit it and log in with your test account.

> ℹ️ Cloud Run automatically handles scaling, HTTPS certificates, and log aggregation. Remember to restrict access and rotate API keys in production.

## 🎯 How to Use

1. **Register Patient**
   - Fill in patient details (Name, Age, Sex, Contact, Address)

2. **Enter Medical Test Results**
   - Input all required medical parameters:
     - Glucose Level (mg/dL)
     - Blood Pressure (mmHg)
     - BMI
     - Diabetes Pedigree Function
     - And other optional parameters

3. **Get Prediction**
   - Click "Predict Risk" button
   - View instant results with confidence score

4. **Generate AI Report**
   - Click "Generate Doctor Report"
   - AI creates a comprehensive medical diagnosis
   - Download the report for records

## 🔧 API Endpoints

- `GET /` - Home page with forms
- `POST /predict` - ML prediction endpoint
- `POST /report` - AI report generation
- `GET /download_report/<filename>` - Download report file
- `GET /health` - Health check endpoint

## 🎨 Features Highlight

### Medical Test Parameters
- **Pregnancies** - Number of pregnancies
- **Glucose** - Plasma glucose concentration
- **Blood Pressure** - Diastolic blood pressure (mm Hg)
- **Skin Thickness** - Triceps skin fold thickness (mm)
- **Insulin** - 2-Hour serum insulin (mu U/ml)
- **BMI** - Body mass index (weight in kg/(height in m)²)
- **Diabetes Pedigree Function** - Diabetes genetic predisposition
- **Age** - Patient age in years

### Design Philosophy
- 🎨 Modern medical theme with soft blue and teal colors
- 📱 Fully responsive for mobile and desktop
- ⚡ Smooth animations and transitions
- 🔒 Form validation and error handling
- ♿ Accessible and user-friendly interface

## 🛠️ Technology Stack

- **Backend**: Flask (Python)
- **Frontend**: HTML5, CSS3, JavaScript (Vanilla)
- **ML**: scikit-learn, NumPy, Pandas
- **AI**: Groq LLM (via LangChain)
- **Fonts**: Google Fonts (Poppins)
- **Icons**: Font Awesome 6

## 📊 Model Information

The ML model is trained on the Pima Indians Diabetes Database and predicts diabetes risk based on diagnostic measurements.

## 🔐 Security Notes

- Never commit your `.env` file to version control
- Keep your Groq API key secure
- Use environment variables for sensitive data
- Implement rate limiting for production deployment

## 🚀 Azure Deployment (CI/CD)

This project includes automated CI/CD deployment to Azure Web App Services.

### Quick Deploy to Azure

1. **Create Azure Web App** (Python 3.11, Linux)
2. **Configure Environment Variables** in Azure Portal
3. **Get Publish Profile** and add to GitHub Secrets as `AZURE_WEBAPP_PUBLISH_PROFILE`
4. **Push to main branch** - automatic deployment starts!

```bash
git add .
git commit -m "Deploy to Azure"
git push origin main
```

### Detailed Deployment Guide

📚 **Complete Guide:** [AZURE_DEPLOYMENT.md](./AZURE_DEPLOYMENT.md)
✅ **Checklist:** [DEPLOYMENT_CHECKLIST.md](./DEPLOYMENT_CHECKLIST.md)

### Verify Deployment

Run the verification script after deployment:

```bash
bash verify-deployment.sh
```

### CI/CD Pipeline Features

- ✅ Automated Python backend build
- ✅ Automated React frontend build  
- ✅ Combined deployment to Azure
- ✅ Health checks after deployment
- ✅ Detailed deployment logs
- ✅ Rollback support

**Workflow File:** `.github/workflows/azure-deploy.yml`

### Monitor Your Deployment

```bash
# View live logs
az webapp log tail -g diabetes-predictor-rg -n diabetes-predictor-ai

# Restart application
az webapp restart -g diabetes-predictor-rg -n diabetes-predictor-ai
```

### Production Best Practices

- ✅ Use B1 or higher tier (no cold starts)
- ✅ Enable Application Insights for monitoring
- ✅ Configure custom domain with SSL
- ✅ Set up Azure Key Vault for secrets
- ✅ Enable automated backups
- ✅ Configure alerts for errors/downtime

## 🤝 Contributing

This is a medical diagnostic tool. Ensure all contributions maintain:
- Medical accuracy
- Patient privacy
- Professional standards
- Code quality

## ⚠️ Disclaimer

This application is for educational and screening purposes only. It should not be used as a substitute for professional medical advice, diagnosis, or treatment. Always consult with qualified healthcare professionals for medical concerns.

## 📝 License

© 2025 Diabetes Health Predictor - AI Doctor Portal

## 👨‍⚕️ About

**Dr. Ramesh Kumar Hospital**  
AI-Powered Medical Diagnostic System

---

**Built with ❤️ for better healthcare**
