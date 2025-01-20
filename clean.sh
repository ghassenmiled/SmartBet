#!/bin/bash

# Exit immediately if a command exits with a non-zero status
set -e

# Step 1: Stop all running containers
echo "Stopping all running containers..."
docker ps -q | xargs -r docker stop

# Step 2: Remove all Docker containers (stopped and running)
echo "Removing all Docker containers..."
docker ps -a -q | xargs -r docker rm

# Step 3: Get the latest 2 Docker images based on creation date
echo "Cleaning up Docker images"
# Keep only the latest 2 images
docker images --format "{{.Repository}}:{{.Tag}} {{.ID}} {{.CreatedAt}}" | xargs -r docker rmi
