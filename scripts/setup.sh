#!/bin/bash

# Exit immediately if a command exits with a non-zero status
set -e

# Function to check if a command exists
command_exists() {
    command -v "$1" &>/dev/null
}

# Check if Node.js and npm are installed, and install if missing
echo "Step 1: Checking for Node.js and npm..."
if ! command_exists nodejs || ! command_exists npm; then
    echo "Node.js or npm not found. Installing Node.js and npm..."
    sudo apt install -y nodejs npm || { echo "Failed to install Node.js and npm"; exit 1; }
else
    echo "Node.js and npm are already installed."
    # Check for Node.js version (example: requiring version 16 or higher)
    NODE_VERSION=$(node -v | cut -d '.' -f 1 | sed 's/[^0-9]*//g')
    if [ "$NODE_VERSION" -lt 16 ]; then
        echo "Warning: Node.js version is lower than 16. Some features may not work. Consider upgrading Node.js."
    else
        echo "Node.js version is sufficient."
    fi
fi

# Step 2: Check if Python3 and pip3 are installed
echo "Step 2: Checking for Python3 and pip3..."
if ! command_exists python3; then
    echo "Error: Python3 is not installed. Please install Python3 before proceeding."
    exit 1
fi

if ! command_exists pip3; then
    echo "Error: Pip3 is not installed. Please install Pip3 before proceeding."
    exit 1
fi

# Step 3: Create a virtual environment if it doesn't exist
if [ ! -d "venv" ]; then
    echo "Step 3: Creating a Python virtual environment..."
    python3 -m venv venv || { echo "Failed to create virtual environment"; exit 1; }
    echo "Virtual environment created in $(pwd)/venv"
else
    echo "Virtual environment already exists."
fi

# Step 4: Activate the virtual environment
echo "Step 4: Activating the virtual environment..."
source venv/bin/activate || { echo "Failed to activate virtual environment"; exit 1; }

# Check if the virtual environment is activated
if [[ "$VIRTUAL_ENV" == "" ]]; then
    echo "Error: Virtual environment is not activated."
    exit 1
else
    echo "Virtual environment is activated."
fi

# Step 5: Install Python dependencies from requirements.txt if available
if [ -f "requirements.txt" ]; then
    echo "Step 5: Installing Python dependencies from requirements.txt..."
    pip install --upgrade pip || { echo "Failed to upgrade pip"; exit 1; }
    pip install -r requirements.txt || { echo "Failed to install Python dependencies"; exit 1; }
else
    echo "No requirements.txt found. Skipping Python dependency installation."
fi

# Step 6: Install or upgrade necessary dependencies like Flask, scikit-learn, pandas
echo "Step 6: Installing or upgrading necessary dependencies..."
pip install --upgrade flask==2.2.2 werkzeug==2.2.2 scikit-learn pandas numpy || { echo "Failed to install/upgrade necessary dependencies"; exit 1; }

# Step 7: Check if the necessary environment variable (API_KEY) is set
echo "Step 7: Checking if the API_KEY environment variable is set..."
if [ -z "$API_KEY" ]; then
    echo "Warning: API_KEY environment variable is not set. Please set it before running the app."
else
    echo "API_KEY environment variable is set."
fi

# Step 8: Request and set the API key if not set
get_api_key() {
    echo "Please enter your Sports API key:"
    read -r API_KEY
    if [ -z "$API_KEY" ]; then
        echo "API key cannot be empty. Please try again."
        get_api_key
    else
        export API_KEY
        echo "API key set successfully."
    fi
}

get_api_key

# Step 9: Check if Docker or Podman is installed
check_container_tools() {
    echo "Step 9: Checking if Docker or Podman is installed..."
    if ! command_exists docker && ! command_exists podman; then
        echo "Error: Neither Docker nor Podman is installed. Please install one before proceeding."
        exit 1
    fi
}

check_container_tools

# Step 10: Determine which container tool is available
if command_exists docker; then
    CONTAINER_TOOL="docker"
elif command_exists podman; then
    CONTAINER_TOOL="podman"
else
    echo "Error: Neither Docker nor Podman found."
    exit 1
fi

# Functions to manage containers and images
stop_containers() {
    echo "Step 11: Stopping all running containers..."
    if [ "$CONTAINER_TOOL" = "docker" ]; then
        docker ps -q | xargs -r docker stop
    elif [ "$CONTAINER_TOOL" = "podman" ]; then
        podman ps -q | xargs -r podman stop
    fi
}

remove_containers() {
    echo "Step 12: Removing all containers..."
    if [ "$CONTAINER_TOOL" = "docker" ]; then
        docker ps -a -q | xargs -r docker rm
    elif [ "$CONTAINER_TOOL" = "podman" ]; then
        podman ps -a -q | xargs -r podman rm -f
    fi
}

remove_docker_images() {
    echo "Step 13: Removing all Docker images except Ubuntu images..."
    if [ "$CONTAINER_TOOL" = "docker" ]; then
        docker images --filter "dangling=false" --filter "reference!=ubuntu*" -q | xargs -r docker rmi -f || echo "No Docker images to remove"
    fi
}

remove_podman_images() {
    echo "Step 14: Removing all Podman images except Ubuntu images..."
    if [ "$CONTAINER_TOOL" = "podman" ]; then
        podman images --filter "dangling=false" --filter "reference!=ubuntu*" -q | xargs -r podman rmi -f || echo "No Podman images to remove"
    fi
}

remove_docker_volumes() {
    echo "Step 15: Cleaning up unused Docker volumes..."
    if [ "$CONTAINER_TOOL" = "docker" ]; then
        docker volume prune -f || echo "No unused Docker volumes to remove"
    fi
}

remove_docker_networks() {
    echo "Step 16: Cleaning up unused Docker networks..."
    if [ "$CONTAINER_TOOL" = "docker" ]; then
        docker network prune -f || echo "No unused Docker networks to remove"
    fi
}

# Step 17: Build and run the app container
build_and_run_app() {
    echo "Step 17: Building and running the app container..."

    APP_DIR=$(pwd)

    echo "Navigating to app directory: $APP_DIR"
    cd "$APP_DIR" || { echo "Failed to navigate to the app directory"; exit 1; }

    echo "Checking for existing container..."
    if [ "$CONTAINER_TOOL" = "docker" ]; then
        if docker ps -a --format '{{.Names}}' | grep -q "bet-app"; then
            echo "Stopping existing container..."
            docker stop bet-app || { echo "Failed to stop existing container"; exit 1; }
            echo "Removing existing container..."
            docker rm bet-app || { echo "Failed to remove existing container"; exit 1; }
        fi
    elif [ "$CONTAINER_TOOL" = "podman" ]; then
        if podman ps -a --format '{{.Names}}' | grep -q "bet-app"; then
            echo "Stopping existing container..."
            podman stop bet-app || { echo "Failed to stop existing container"; exit 1; }
            echo "Removing existing container..."
            podman rm bet-app || { echo "Failed to remove existing container"; exit 1; }
        fi
    fi

    echo "Building container image..."
    if [ "$CONTAINER_TOOL" = "docker" ]; then
        docker build --network=host -t my-bet-app . || { echo "Failed to build Docker image"; exit 1; }
    elif [ "$CONTAINER_TOOL" = "podman" ]; then
        podman build --network=host -t my-bet-app . || { echo "Failed to build Podman image"; exit 1; }
    fi

    echo "Running container with API_KEY..."
    if [ "$CONTAINER_TOOL" = "docker" ]; then
        docker run --network=host -d -p 5000:5000 --name bet-app -e API_KEY="$API_KEY" my-bet-app || { echo "Failed to run Docker container"; exit 1; }
    elif [ "$CONTAINER_TOOL" = "podman" ]; then
        podman run --network=host -d -p 5000:5000 --name bet-app -e API_KEY="$API_KEY" my-bet-app || { echo "Failed to run Podman container"; exit 1; }
    fi
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
