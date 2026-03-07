#!/bin/bash
# run_docker_prod.sh
# Build and run Jogfol API in Docker for production (detached, host network)

set -e

IMAGE_NAME="jogfol-api"
CONTAINER_NAME="jogfol-api-prod"

# Load PORT from .env
PORT=$(grep -E '^PORT=' .env | cut -d '=' -f2)

if [ -z "$PORT" ]; then
    echo "Error: PORT is not defined in .env"
    exit 1
fi

echo "Building Docker image..."
docker build -t $IMAGE_NAME .

echo "Stopping existing container (if any)..."
docker rm -f $CONTAINER_NAME 2>/dev/null || true

echo "Running Docker container in detached mode with host network..."
docker run -d \
    --name $CONTAINER_NAME \
    --env-file .env \
    --network host \
    $IMAGE_NAME

echo "Container $CONTAINER_NAME is running on port $PORT (via host network)"
