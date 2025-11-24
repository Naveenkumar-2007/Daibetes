#!/bin/bash
set -e

echo "🚀 Starting Diabetes Predictor App"
echo "Python: $(python --version)"
echo "Working directory: $(pwd)"

# Check if artifacts exist
if [ -d "/app/artifacts" ]; then
    echo "✅ ML artifacts found"
else
    echo "⚠️  artifacts/ directory not found!"
fi

# Start gunicorn
exec gunicorn \
  --bind 0.0.0.0:${PORT:-8080} \
  --workers 1 \
  --threads 4 \
  --timeout 300 \
  --access-logfile - \
  --error-logfile - \
  --log-level info \
  --preload \
  flask_app:app
