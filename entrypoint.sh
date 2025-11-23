#!/bin/bash
set -e

echo "========================================="
echo "🚀 Starting Diabetes Predictor App"
echo "========================================="
echo "Python version: $(python --version)"
echo "Working directory: $(pwd)"
echo "Files in /app:"
ls -la /app/ | head -20
echo ""
echo "Files in /app/artifacts:"
ls -la /app/artifacts/ || echo "⚠️  artifacts/ directory not found!"
echo ""
echo "Environment variables:"
echo "PORT=${PORT:-8080}"
echo "GROQ_API_KEY=${GROQ_API_KEY:0:20}..."
echo "========================================="
echo "Starting gunicorn..."
echo "========================================="

exec gunicorn \
  --bind 0.0.0.0:${PORT:-8080} \
  --workers 2 \
  --threads 2 \
  --timeout 120 \
  --access-logfile - \
  --error-logfile - \
  --log-level debug \
  --capture-output \
  flask_app:app
