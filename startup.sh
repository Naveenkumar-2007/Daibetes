#!/bin/bash

# Azure App Service startup script for Flask application

# Install dependencies if needed
pip install -r requirements.txt

# Create necessary directories
mkdir -p logs/predictions logs/drift_reports logs/performance_reports
mkdir -p static/reports
mkdir -p artifacts

# Set Python unbuffered mode
export PYTHONUNBUFFERED=1

# Start Gunicorn with proper configuration
gunicorn --bind=0.0.0.0:8000 \
         --workers=4 \
         --threads=2 \
         --timeout=120 \
         --access-logfile=- \
         --error-logfile=- \
         --log-level=info \
         flask_app:app
