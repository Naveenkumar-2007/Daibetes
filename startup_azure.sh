#!/bin/bash
# Azure App Service startup script
# This script runs BEFORE Gunicorn starts

echo "========================================="
echo "Azure App Service Startup"
echo "========================================="

# Install dependencies if requirements.txt changed
if [ -f "requirements.txt" ]; then
    echo "Installing Python dependencies..."
    python -m pip install --no-cache-dir -r requirements.txt --quiet
fi

echo "Starting Gunicorn..."
exec gunicorn --bind=0.0.0.0:8000 \
    --workers=1 \
    --threads=8 \
    --timeout=120 \
    --worker-class=gthread \
    --access-logfile=- \
    --error-logfile=- \
    flask_app:app
