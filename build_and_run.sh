#!/bin/bash
set -e

# Default to port 3000 if not specified
PORT=${1:-3000}

if [ "$PORT" != "3000" ] && [ "$PORT" != "4000" ]; then
    echo "Error: Port must be either 3000 or 4000."
    exit 1
fi

echo "🚀 Building Docker image aws-security-dashboard..."
docker build -t aws-security-dashboard:latest .

echo "🛑 Stopping existing container (if running)..."
docker stop security-dashboard 2>/dev/null || true
docker rm security-dashboard 2>/dev/null || true

echo "▶️  Starting container on port $PORT..."
docker run -d \
  --name security-dashboard \
  --network host \
  -v ~/.aws:/root/.aws:ro \
  -e AWS_PROFILE=${AWS_PROFILE:-default} \
  -e PORT=$PORT \
  aws-security-dashboard:latest

# Fetch private IP
PRIVATE_IP=$(hostname -I | awk '{print $1}')

echo "==========================================================="
echo "✅ Application deployed successfully!"
echo "🌐 Access the website at: http://${PRIVATE_IP}:${PORT}"
echo "==========================================================="
