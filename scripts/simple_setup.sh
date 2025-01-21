#!/bin/bash

# Exit immediately if a command exits with a non-zero status
set -e

# Function to check if a command exists
command_exists() {
    command -v "$1" &>/dev/null
}

# Step 1: Check if Python3 and pip3 are installed
echo "Step 1: Checking for Python3 and pip3..."
if ! command_exists python3; then
    echo "Error: Python3 is not installed. Please install Python3 before proceeding."
    exit 1
fi

if ! command_exists pip3; then
    echo "Error: Pip3 is not installed. Please install Pip3 before proceeding."
    exit 1
fi

# Step 2: Check if Docker or Podman is installed
echo "Step 2: Checking if Docker or Podman is installed..."
if ! command_exists docker && ! command_exists podman; then
    echo "Error: Neither Docker nor Podman is installed. Please install one before proceeding."
    exit 1
fi

# Step 3: Check if the necessary environment variable (API_KEY) is set
echo "Step 3: Checking if the API_KEY environment variable is set..."
if [ -z "$API_KEY" ]; then
    echo "Warning: API_KEY environment variable is not set. Please set it before running the app."
else
    echo "API_KEY environment variable is set."
fi

# Step 4: Build and run the app container
echo "Step 4: Building and running the app container..."

# Check which container tool is available
if command_exists docker; then
    CONTAINER_TOOL="docker"
elif command_exists podman; then
    CONTAINER_TOOL="podman"
else
    echo "Error: Neither Docker nor Podman found."
    exit 1
fi

# Function to stop and remove the existing container
stop_and_remove_container() {
    echo "Step 5: Stopping and removing existing container..."

    if [ "$CONTAINER_TOOL" = "docker" ]; then
        if docker ps -a --format '{{.Names}}' | grep -q "bet-app"; then
            docker stop bet-app
            docker rm bet-app
        fi
    elif [ "$CONTAINER_TOOL" = "podman" ]; then
        if podman ps -a --format '{{.Names}}' | grep -q "bet-app"; then
            podman stop bet-app
            podman rm bet-app
        fi
    fi
}

stop_and_remove_container

# Build and run the container with API_KEY
echo "Building and running the app..."

if [ "$CONTAINER_TOOL" = "docker" ]; then
    docker build --network=host -t my-bet-app . || { echo "Failed to build Docker image"; exit 1; }
    docker run --network=host -d -p 5000:5000 --name bet-app -e API_KEY="$API_KEY" my-bet-app || { echo "Failed to run Docker container"; exit 1; }
elif [ "$CONTAINER_TOOL" = "podman" ]; then
    podman build --network=host -t my-bet-app . || { echo "Failed to build Podman image"; exit 1; }
    podman run --network=host -d -p 5000:5000 --name bet-app -e API_KEY="$API_KEY" my-bet-app || { echo "Failed to run Podman container"; exit 1; }
fi

echo "App setup and run complete!"

