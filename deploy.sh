#!/bin/bash

# Azure deployment script with timeout optimization
set -e

echo "🚀 Starting Azure deployment..."
echo "⏱️  Optimized for quick startup"

# Install dependencies if not cached
if [ ! -d "antenv" ]; then
    echo "📦 Installing Python dependencies..."
    python -m pip install --upgrade pip
    pip install -r requirements.txt --no-cache-dir
else
    echo "✅ Using cached dependencies"
fi

echo "✅ Deployment complete!"
