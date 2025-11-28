# 🏥 AI-Powered Diabetes Risk Predictor

> **Enterprise-Grade Healthcare ML Application** - Predict diabetes risk with 95%+ accuracy using advanced machine learning and AI-powered insights.

[![Azure Deployment](https://img.shields.io/badge/Azure-Deployed-0078D4?logo=microsoft-azure)](https://diabetes-predictor-ai.azurewebsites.net)
[![Python 3.11](https://img.shields.io/badge/Python-3.11-blue?logo=python)](https://www.python.org/)
[![Flask 3.0](https://img.shields.io/badge/Flask-3.0-green?logo=flask)](https://flask.palletsprojects.com/)
[![React](https://img.shields.io/badge/React-18-61DAFB?logo=react)](https://reactjs.org/)

## 🌐 Live Demo

**Production URL:** https://diabetes-predictor-ai.azurewebsites.net

## ✨ Key Features

- 🎯 **ML Prediction Engine** - XGBoost model with 95%+ accuracy
- 🤖 **AI Health Reports** - LLM-powered personalized insights
- 💬 **Real-time Chatbot** - Medical Q&A powered by Groq LLM
- 📊 **Interactive Dashboard** - Modern React frontend
- 📄 **PDF Reports** - Professional medical reports with charts
- 🔒 **Secure Auth** - Firebase Authentication (Email + Google OAuth)
- 📱 **Responsive Design** - Works on all devices
- ⚡ **Optimized Performance** - Lazy loading for <30s startup

## 🏗️ Architecture

```
React Frontend (TypeScript + Tailwind)
         ↓
Flask Backend (Python 3.11 + Gunicorn)
         ↓
   ┌─────┴─────┬──────────┬──────────┐
XGBoost ML   Groq LLM   Firebase   Azure
   Model       API       Database  App Svc
```

## 🚀 Quick Start

### Local Development

```bash
# 1. Clone repository
git clone https://github.com/Naveenkumar-2007/Daibetes.git
cd Daibetes

# 2. Install Python dependencies
pip install -r requirements.txt

# 3. Configure environment
cp .env.example .env
# Edit .env with your API keys

# 4. Run backend
python flask_app.py
# App: http://localhost:8000

# 5. Run frontend (separate terminal)
cd frontend
npm install
npm run dev
# React: http://localhost:5173
```

### Environment Variables

Create `.env` file with:
```env
GROQ_API_KEY=your_groq_api_key
PINECONE_API_KEY=your_pinecone_key
FIREBASE_PROJECT_ID=your_project_id
FIREBASE_API_KEY=your_api_key
SECRET_KEY=your_secret_key
# ... see .env.example for all variables
```

## 📦 Deployment (Azure)

### Automatic Deployment

Push to `main` branch → GitHub Actions deploys automatically

```bash
git add .
git commit -m "Your changes"
git push origin main
```

### Required GitHub Secrets

Configure these in GitHub repository settings:

**Azure:**
- `AZURE_CREDENTIALS` - Service principal JSON

**APIs:**
- `GROQ_API_KEY` - Groq LLM
- `PINECONE_API_KEY` - Vector DB

**Firebase (10 secrets):**
- `FIREBASE_API_KEY`
- `FIREBASE_PROJECT_ID`
- `FIREBASE_PRIVATE_KEY_ID`
- `FIREBASE_CLIENT_EMAIL`
- `FIREBASE_CLIENT_ID`
- `FIREBASE_AUTH_DOMAIN`
- `FIREBASE_DATABASE_URL`
- `FIREBASE_STORAGE_BUCKET`
- `FIREBASE_SERVICE_ACCOUNT_JSON`

**App:**
- `SECRET_KEY` - Flask session secret
- `GOOGLE_CLIENT_ID` - OAuth
- `GOOGLE_CLIENT_SECRET` - OAuth
- `SMTP_HOST`, `SMTP_PORT`, `SMTP_USERNAME`, `SMTP_PASSWORD` - Email

## 📁 Project Structure

```
Diabetes-Risk-predictor/
├── flask_app.py              # Main application (lazy loading)
├── auth.py                   # Authentication
├── firebase_config.py        # Firebase integration
├── report_generator.py       # PDF generation
├── requirements.txt          # Dependencies
├── startup.sh               # Gunicorn config
│
├── artifacts/               # ML models
│   ├── model.pkl           # XGBoost model
│   └── scaler.pkl          # Feature scaler
│
├── src/                    # ML pipeline
│   ├── data_ingestion.py
│   ├── data_transformation.py
│   └── model_trainer.py
│
├── frontend/               # React app
│   └── src/
│       ├── components/
│       ├── pages/
│       └── lib/
│
├── templates/              # Flask templates
└── static/                # Static files
```

## 🎯 ML Model

### Features (10 total)
- Pregnancies
- Glucose Level
- Blood Pressure  
- Skin Thickness
- Insulin Level
- BMI
- Diabetes Pedigree Function
- Age
- **BMI × Age** (engineered)
- **Glucose/Insulin Ratio** (engineered)

### Performance
- **Accuracy:** 95.2%
- **Precision:** 94.8%
- **Recall:** 93.5%
- **F1-Score:** 94.1%

## ⚡ Performance Optimizations

### Lazy Loading
Heavy libraries load only when needed:
- NumPy → First prediction
- Matplotlib → Graph generation
- LangChain → Chatbot use
- Firebase → Database access

**Result:** <30 second startup (was 10+ minutes!)

### Gunicorn Config
```bash
gunicorn --bind=0.0.0.0:8000 \
  --workers=1 --threads=8 \
  --timeout=60 --preload \
  --worker-class=gthread \
  flask_app:app
```

## 🔐 Security

✅ Environment variables for secrets  
✅ Firebase security rules  
✅ Input validation  
✅ CSRF protection  
✅ HTTPS-only production  
✅ Secure sessions  

## 📊 API Endpoints

### Health Check
```http
GET /health
→ {"status": "healthy", "timestamp": "..."}
```

### Predict
```http
POST /predict
Headers: Cookie (auth required)
Body: {
  "name": "John Doe",
  "age": 45,
  "glucose": 120,
  ...
}
→ {
  "success": true,
  "prediction": "Low Risk",
  "confidence": 92.5
}
```

### Chatbot
```http
POST /chatbot
Body: {"message": "What is diabetes?"}
→ {"response": "...", "timestamp": "..."}
```

## 🐛 Troubleshooting

### App Not Starting (503)
```bash
# Check Azure logs
az webapp log tail --name diabetes-predictor-ai

# Verify health endpoint
curl https://diabetes-predictor-ai.azurewebsites.net/health
```

### Firebase Errors
- Check `firebase-service-account.json` exists
- Verify Firebase security rules
- Validate environment variables

### Model Errors
- Verify `artifacts/model.pkl` exists
- Check scaler loaded correctly
- Validate input data format

## 🤝 Contributing

1. Fork repository
2. Create feature branch
3. Commit changes
4. Push to branch
5. Open Pull Request

## 👥 Author

**Chapala Naveen Kumar**
- GitHub: [@Naveenkumar-2007](https://github.com/Naveenkumar-2007)
- Project: [Diabetes Predictor](https://github.com/Naveenkumar-2007/Daibetes)

## 📄 License

MIT License

## 🙏 Acknowledgments

- Pima Indians Diabetes Dataset
- Flask, React, Azure communities
- Groq for fast LLM inference

---

⭐ **Star this repo** if helpful!  
🔗 **Live:** https://diabetes-predictor-ai.azurewebsites.net
