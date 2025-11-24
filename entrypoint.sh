#!/bin/bash
set -e

echo "🚀 Starting Diabetes Predictor App"
echo "Python: $(python --version)"
echo "Working directory: $(pwd)"
echo "Environment: ${FLASK_ENV:-development}"

# Check if artifacts exist
if [ -d "/app/artifacts" ]; then
    echo "✅ ML artifacts found"
    ls -lh /app/artifacts/
else
    echo "⚠️  artifacts/ directory not found!"
fi

# Run startup test to verify imports
echo ""
echo "Running startup tests..."
python startup_test.py
if [ $? -ne 0 ]; then
    echo "❌ Startup test failed! Check logs above."
    exit 1
fi
echo "✅ Startup test passed!"
echo ""

# Azure sets WEBSITES_PORT, local/Docker uses PORT
PORT=${WEBSITES_PORT:-${PORT:-8000}}
echo "Starting Gunicorn on port $PORT..."

exec gunicorn \
  --bind 0.0.0.0:$PORT \
  --workers 2 \
  --threads 4 \
  --timeout 600 \
  --graceful-timeout 60 \
  --keep-alive 5 \
  --access-logfile - \
  --error-logfile - \
  --log-level info \
  flask_app:app
