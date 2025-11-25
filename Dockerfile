# syntax=docker/dockerfile:1
# Multi-stage build with Node.js for React frontend
FROM node:20-alpine AS frontend-builder

WORKDIR /app/frontend
COPY frontend/package*.json ./
RUN npm ci --silent
COPY frontend/ ./
RUN npm run build

# Python backend stage
FROM python:3.11-slim

# Environment variables
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PORT=8000 \
    FLASK_ENV=production

WORKDIR /app

# Install system dependencies
RUN apt-get update \
    && apt-get install -y --no-install-recommends \
       libfreetype6 \
       libjpeg62-turbo \
       libpng16-16 \
       curl \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements and install Python dependencies
COPY requirements.txt ./
RUN pip install --no-cache-dir --upgrade pip \
    && pip install --no-cache-dir -r requirements.txt \
    && pip install --no-cache-dir gunicorn

# Copy application code
COPY . .

# Copy React build from frontend-builder stage
COPY --from=frontend-builder /app/frontend/dist ./frontend/dist

# Create necessary directories with proper permissions
RUN mkdir -p /app/reports /app/logs /app/artifacts \
    && chmod -R 755 /app/reports /app/logs /app/artifacts

# Make entrypoint executable
RUN chmod +x /app/entrypoint.sh

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=60s --retries=3 \
    CMD curl -f http://localhost:8000/health || exit 1

# Expose port
EXPOSE 8000

# Use entrypoint script
CMD ["/app/entrypoint.sh"]
