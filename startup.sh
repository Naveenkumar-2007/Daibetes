#!/bin/bash

# Azure App Service startup script for Flask application
# This script runs when the container starts

set -e  # Exit on error

echo "🚀 Starting Diabetes Health Predictor..."
echo "📅 Timestamp: $(date)"
echo "🖥️  Hostname: $(hostname)"

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

# Install dependencies if not already installed
if [ ! -d "/home/site/wwwroot/antenv" ]; then
    echo "📦 Installing dependencies (first run)..."
    python3.11 -m pip install --upgrade pip --user
    python3.11 -m pip install -r requirements.txt --user --no-cache-dir
    echo "✅ Dependencies installed"
else
    echo "📦 Dependencies already installed"
fi

# Verify critical files exist
echo "🔍 Verifying application files..."
if [ ! -f "flask_app.py" ]; then
    echo "❌ ERROR: flask_app.py not found!"
    exit 1
fi

if [ ! -f "requirements.txt" ]; then
    echo "⚠️  WARNING: requirements.txt not found!"
fi

echo "✅ Application files verified"

# Determine the port (Azure sets PORT environment variable)
PORT="${PORT:-8000}"

echo "🌐 Starting Gunicorn on port $PORT..."
echo "⚙️  Configuration:"
echo "   - Workers: 2 (reduced for faster startup)"
echo "   - Threads: 4"
echo "   - Timeout: 300s"
echo "   - Graceful timeout: 120s"

# Start Gunicorn with optimized settings for Azure (faster startup)
exec gunicorn --bind=0.0.0.0:$PORT \
         --workers=2 \
         --threads=4 \
         --timeout=300 \
         --graceful-timeout=120 \
         --keep-alive=5 \
         --max-requests=1000 \
         --max-requests-jitter=50 \
         --access-logfile=- \
         --error-logfile=- \
         --log-level=info \
         --worker-class=gthread \
         flask_app:app

