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
mkdir -p artifacts data/raw data/processed reports /tmp/matplotlib

# Set environment variables
export PYTHONUNBUFFERED=1
export PYTHONDONTWRITEBYTECODE=1
export MPLCONFIGDIR=/tmp/matplotlib

echo "✅ Environment configured"

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

# Run startup test
if [ -f "startup_test.py" ]; then
    echo "🧪 Running startup tests..."
    python startup_test.py
    if [ $? -ne 0 ]; then
        echo "⚠️ Startup test failed, but continuing..."
    fi
fi

# Determine the port (Azure sets PORT or WEBSITES_PORT environment variable)
PORT="${WEBSITES_PORT:-${PORT:-8000}}"

echo "🌐 Starting Gunicorn on port $PORT..."
echo "⚙️  Configuration:"
echo "   - Workers: 1 (optimized for fast startup)"
echo "   - Threads: 8"
echo "   - Timeout: 120s (reduced)"
echo "   - Preload: disabled"

# Start Gunicorn with optimized settings for Azure
# Single worker for faster startup, more threads to handle concurrent requests
exec gunicorn --bind=0.0.0.0:$PORT \
         --workers=1 \
         --threads=8 \
         --timeout=120 \
         --graceful-timeout=30 \
         --keep-alive=5 \
         --max-requests=500 \
         --max-requests-jitter=50 \
         --access-logfile=- \
         --error-logfile=- \
         --log-level=info \
         --worker-class=gthread \
         --worker-tmp-dir=/dev/shm \
         flask_app:app

