#!/bin/bash

# Azure App Service startup script for Flask application
# This script runs when the container starts

echo "🚀 Starting Diabetes Health Predictor..."

# Create necessary directories
echo "📁 Creating directories..."
mkdir -p logs/predictions logs/drift_reports logs/performance_reports
mkdir -p static/reports static/app
mkdir -p artifacts data/raw data/processed reports

# Set environment variables
export PYTHONUNBUFFERED=1
export PYTHONDONTWRITEBYTECODE=1
export MPLCONFIGDIR=/tmp/matplotlib

# Create matplotlib cache directory
mkdir -p /tmp/matplotlib

echo "✅ Environment configured"

# Determine the port (Azure sets PORT environment variable)
PORT="${PORT:-8000}"

echo "🌐 Starting Gunicorn on port $PORT..."

# Start Gunicorn with optimized settings for Azure
gunicorn --bind=0.0.0.0:$PORT \
         --workers=4 \
         --threads=2 \
         --timeout=600 \
         --keep-alive=5 \
         --max-requests=1000 \
         --max-requests-jitter=50 \
         --access-logfile=- \
         --error-logfile=- \
         --log-level=info \
         --worker-class=sync \
         flask_app:app

echo "❌ Gunicorn stopped unexpectedly"
