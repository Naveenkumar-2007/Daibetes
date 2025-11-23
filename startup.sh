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

# Set Python path to include pre-installed packages
if [ -d ".python_packages/lib/site-packages" ]; then
    echo "📦 Using pre-installed dependencies from .python_packages..."
    export PYTHONPATH="${PYTHONPATH}:$(pwd)/.python_packages/lib/site-packages"
else
    echo "⚠️  Pre-installed packages not found, will use system packages"
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
echo "   - Workers: 4"
echo "   - Threads: 2"
echo "   - Timeout: 600s"

# Start Gunicorn with optimized settings for Azure
exec gunicorn --bind=0.0.0.0:$PORT \
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
         --preload \
         flask_app:app

