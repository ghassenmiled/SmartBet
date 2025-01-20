#!/bin/bash

# Exit immediately if a command exits with a non-zero status
set -e

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

# Function to remove all Docker images
remove_docker_images() {
    echo "Removing all Docker images..."
    # Remove Docker images if they exist
    docker images -q | xargs -r docker rmi -f || echo "No Docker images to remove"
}

# Function to remove all Podman images
remove_podman_images() {
    echo "Removing all Podman images..."
    # Remove Podman images if they exist
    podman images -q | xargs -r podman rmi -f || echo "No Podman images to remove"
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

# Main script execution
stop_containers
remove_containers
remove_docker_images
remove_podman_images
remove_docker_volumes
remove_docker_networks

echo "Clean up complete!"
