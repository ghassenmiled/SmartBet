#!/bin/bash

# Measure the start time
start_time=$(date +%s)

# Exit immediately if a command exits with a non-zero status
set -e

# Function to check if a command exists
command_exists() {
    command -v "$1" &>/dev/null
}

# Step 1: Check if Python3, pip3, and Node.js are installed
echo "Step 1: Checking dependencies..."
if ! command_exists python3; then
    echo "Error: Python3 is not installed. Please install Python3."
    exit 1
fi

if ! command_exists pip3; then
    echo "Error: Pip3 is not installed. Please install Pip3."
    exit 1
fi

if ! command_exists nodejs || ! command_exists npm; then
    echo "Node.js or npm not found. Installing..."
    sudo apt install -y nodejs npm
fi

# Step 2: Create and activate the virtual environment
if [ ! -d "venv" ]; then
    echo "Step 2: Creating Python virtual environment..."
    python3 -m venv venv
fi

echo "Activating the virtual environment..."
source venv/bin/activate

# Step 3: Install Python dependencies
if [ -f "requirements.txt" ]; then
    echo "Step 3: Installing Python dependencies..."
    pip install --upgrade pip
    pip install -r requirements.txt
fi

# Step 4: Build and run the app container
APP_DIR=$(pwd)
CONTAINER_NAME="bet-app"
IMAGE_NAME="my-bet-app"

echo "Step 4: Building and running the app container..."
if docker ps -a --format '{{.Names}}' | grep -q "$CONTAINER_NAME"; then
    echo "Stopping and removing existing container..."
    docker stop "$CONTAINER_NAME"
    docker rm "$CONTAINER_NAME"
fi

echo "Building Docker image..."
docker build --network=host -t "$IMAGE_NAME" .

echo "Running container..."
docker run --network=host -d -p 5000:5000 --name "$CONTAINER_NAME" "$IMAGE_NAME"

# Measure the end time
end_time=$(date +%s)

# Calculate and display the total execution time
execution_time=$((end_time - start_time))
echo "Setup complete in $execution_time seconds!"
