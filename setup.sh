#!/bin/bash

# Exit immediately if a command exits with a non-zero status
set -e

# Function to prompt for the API key and export it
get_api_key() {
    echo "Please enter your Sports API key:"
    read -r API_KEY
    export API_KEY
    echo "API key set successfully."
}

# Request API key
get_api_key

# Function to stop all running containers
stop_containers() {
    echo "Stopping all running containers..."
    # Stop Docker containers
    docker ps -q | xargs -r docker stop
    # Stop Podman containers
    podman ps -q | xargs -r podman stop
}

# Function to remove all containers (force removal)
remove_containers() {
    echo "Removing all containers..."
    # Remove Docker containers
    docker ps -a -q | xargs -r docker rm
    # Remove Podman containers
    podman ps -a -q | xargs -r podman rm -f
}

# Function to remove all Docker images except Ubuntu images
remove_docker_images() {
    echo "Removing all Docker images except Ubuntu images..."
    # Remove Docker images except those starting with 'ubuntu'
    docker images --filter "dangling=false" --filter "reference!=ubuntu*" -q | xargs -r docker rmi -f || echo "No Docker images to remove"
}

# Function to remove all Podman images except Ubuntu images
remove_podman_images() {
    echo "Removing all Podman images except Ubuntu images..."
    # Remove Podman images except those starting with 'ubuntu'
    podman images --filter "dangling=false" --filter "reference!=ubuntu*" -q | xargs -r podman rmi -f || echo "No Podman images to remove"
}

# Function to clean up unused Docker volumes
remove_docker_volumes() {
    echo "Cleaning up unused Docker volumes..."
    docker volume prune -f || echo "No unused Docker volumes to remove"
}

# Function to clean up unused Docker networks
remove_docker_networks() {
    echo "Cleaning up unused Docker networks..."
    docker network prune -f || echo "No unused Docker networks to remove"
}

# Function to build and run the app container
build_and_run_app() {
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

    # Step 4: Run the container using docker with the API key as an environment variable
    echo "Running container with docker..."
    docker run --network=host -d -p 5000:5000 --name bet-app -e API_KEY="$API_KEY" my-bet-app || { echo "Failed to run container"; exit 1; }
}

# Main script execution
echo "Starting setup process..."

# Clean up Docker and Podman containers, images, volumes, and networks
stop_containers
remove_containers
remove_docker_images
remove_podman_images
remove_docker_volumes
remove_docker_networks

# Build and launch the app
build_and_run_app

echo "Setup complete!"
