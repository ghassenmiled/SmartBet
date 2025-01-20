#!/bin/bash

# Exit immediately if a command exits with a non-zero status
set -e

# Function to check if a command exists
command_exists() {
    command -v "$1" &>/dev/null
}

# Check if Node.js and npm are installed, and install if missing
echo "Checking for Node.js and npm..."
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

# Check if Python3 and pip are installed
echo "Checking for Python3 and pip..."
if ! command_exists python3; then
    echo "Error: Python3 is not installed. Please install Python3 before proceeding."
    exit 1
fi

if ! command_exists pip3; then
    echo "Error: Pip3 is not installed. Please install Pip3 before proceeding."
    exit 1
fi

# Create a virtual environment if it doesn't exist
if [ ! -d "venv" ]; then
    echo "Creating a Python virtual environment..."
    python3 -m venv venv || { echo "Failed to create virtual environment"; exit 1; }
    echo "Virtual environment created in $(pwd)/venv"
else
    echo "Virtual environment already exists."
fi

# Activate the virtual environment
echo "Activating the virtual environment..."
source venv/bin/activate || { echo "Failed to activate virtual environment"; exit 1; }

# Check if the virtual environment is activated
if [[ "$VIRTUAL_ENV" == "" ]]; then
    echo "Error: Virtual environment is not activated."
    exit 1
else
    echo "Virtual environment is activated."
fi

# Install Python dependencies from requirements.txt if available
if [ -f "requirements.txt" ]; then
    echo "Installing Python dependencies from requirements.txt..."
    pip install --upgrade pip || { echo "Failed to upgrade pip"; exit 1; }
    pip install -r requirements.txt || { echo "Failed to install Python dependencies"; exit 1; }
else
    echo "requirements.txt not found. Skipping Python dependency installation."
fi

# Force the installation of Flask 2.2.2, Werkzeug, and any missing dependencies (like scikit-learn, pandas)
echo "Installing or upgrading Flask 2.2.2, scikit-learn, pandas, numpy, and other dependencies..."
pip install --upgrade flask==2.2.2 werkzeug==2.2.2 scikit-learn pandas numpy || { echo "Failed to install/upgrade necessary dependencies"; exit 1; }

# Check if the necessary environment variables are set (e.g., API_KEY)
if [ -z "$API_KEY" ]; then
    echo "Warning: API_KEY environment variable is not set. Please set it before running the app."
else
    echo "API_KEY environment variable is set."
fi

# Verifying installations
echo "Verifying installations..."
echo "Python version: $(python3 --version)"
echo "Pip version: $(pip3 --version)"
echo "Installed Python packages:"
pip freeze

echo "Node.js version: $(nodejs --version)"
echo "npm version: $(npm --version)"

# Request API key
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

# Request API key
get_api_key

# Check if Docker and Podman are installed
check_container_tools() {
    if ! command_exists docker && ! command_exists podman; then
        echo "Error: Neither Docker nor Podman is installed. Please install one before proceeding."
        exit 1
    fi
}

# Request and check for Docker/Podman
check_container_tools

# Determine which container tool is available
if command_exists docker; then
    CONTAINER_TOOL="docker"
elif command_exists podman; then
    CONTAINER_TOOL="podman"
else
    echo "Error: Neither Docker nor Podman found."
    exit 1
fi

# Function to stop all running containers
stop_containers() {
    echo "Stopping all running containers..."
    if [ "$CONTAINER_TOOL" = "docker" ]; then
        docker ps -q | xargs -r docker stop
    elif [ "$CONTAINER_TOOL" = "podman" ]; then
        podman ps -q | xargs -r podman stop
    fi
}

# Function to remove all containers (force removal)
remove_containers() {
    echo "Removing all containers..."
    if [ "$CONTAINER_TOOL" = "docker" ]; then
        docker ps -a -q | xargs -r docker rm
    elif [ "$CONTAINER_TOOL" = "podman" ]; then
        podman ps -a -q | xargs -r podman rm -f
    fi
}

# Function to remove all Docker images except Ubuntu images
remove_docker_images() {
    echo "Removing all Docker images except Ubuntu images..."
    if [ "$CONTAINER_TOOL" = "docker" ]; then
        docker images --filter "dangling=false" --filter "reference!=ubuntu*" -q | xargs -r docker rmi -f || echo "No Docker images to remove"
    fi
}

# Function to remove all Podman images except Ubuntu images
remove_podman_images() {
    echo "Removing all Podman images except Ubuntu images..."
    if [ "$CONTAINER_TOOL" = "podman" ]; then
        podman images --filter "dangling=false" --filter "reference!=ubuntu*" -q | xargs -r podman rmi -f || echo "No Podman images to remove"
    fi
}

# Function to clean up unused Docker volumes
remove_docker_volumes() {
    echo "Cleaning up unused Docker volumes..."
    if [ "$CONTAINER_TOOL" = "docker" ]; then
        docker volume prune -f || echo "No unused Docker volumes to remove"
    fi
}

# Function to clean up unused Docker networks
remove_docker_networks() {
    echo "Cleaning up unused Docker networks..."
    if [ "$CONTAINER_TOOL" = "docker" ]; then
        docker network prune -f || echo "No unused Docker networks to remove"
    fi
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

    # Step 3: Build the container image
    echo "Building container image..."
    if [ "$CONTAINER_TOOL" = "docker" ]; then
        docker build --network=host -t my-bet-app . || { echo "Container image build failed"; exit 1; }
    elif [ "$CONTAINER_TOOL" = "podman" ]; then
        podman build --network=host -t my-bet-app . || { echo "Container image build failed"; exit 1; }
    fi

    # Step 4: Run the container with the API key
    echo "Running container with $CONTAINER_TOOL..."
    if [ "$CONTAINER_TOOL" = "docker" ]; then
        docker run --network=host -d -p 5000:5000 --name bet-app -e API_KEY="$API_KEY" my-bet-app || { echo "Failed to run container"; exit 1; }
    elif [ "$CONTAINER_TOOL" = "podman" ]; then
        podman run --network=host -d -p 5000:5000 --name bet-app -e API_KEY="$API_KEY" my-bet-app || { echo "Failed to run container"; exit 1; }
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
