#!/bin/bash

# Exit immediately if a command exits with a non-zero status
set -e

# Get the current directory
APP_DIR=$(pwd)

# Step 1: Change to the app directory
echo "Changing to app directory: $APP_DIR"
cd "$APP_DIR" || { echo "Failed to navigate to the app directory"; exit 1; }

# Step 2: Stop and remove the existing container if it exists
echo "Checking for existing container..."
if docker ps -a --format '{{.Names}}' | grep -q "bet-app"; then
  echo "Stopping existing container..."
  docker stop bet-app || { echo "Failed to stop existing container"; exit 1; }
  echo "Removing existing container..."
  docker rm bet-app || { echo "Failed to remove existing container"; exit 1; }
else
  echo "No existing container found. Proceeding..."
fi

# Step 3: Build the container image using docker
echo "Building container image..."
docker build --network=host -t my-bet-app . || { echo "Container image build failed"; exit 1; }

# Step 4: Run the container using docker
echo "Running container with docker..."
docker run --network=host -d -p 5000:5000 --name bet-app my-bet-app || { echo "Failed to run container"; exit 1; }
