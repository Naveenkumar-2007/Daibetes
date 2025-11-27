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

# Run startup test to verify imports
echo ""
echo "Running startup tests..."
python startup_test.py
if [ $? -ne 0 ]; then
    echo "❌ Startup test failed! Check logs above."
    exit 1
fi
echo ""

# Start gunicorn on the port Azure expects
PORT=${WEBSITES_PORT:-8080}

exec gunicorn \
  --bind 0.0.0.0:$PORT \
  --workers 1 \
  --threads 4 \
  --timeout 300 \
  --graceful-timeout 60 \
  --keep-alive 5 \
  --access-logfile - \
  --error-logfile - \
  --log-level info \
  flask_app:app
