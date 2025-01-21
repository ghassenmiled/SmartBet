#!/bin/bash

# Exit immediately if a command exits with a non-zero status
set -e

# Colors for output
RESET='\033[0m'
GREEN='\033[0;32m'
YELLOW='\033[0;33m'
RED='\033[0;31m'
BLUE='\033[0;34m'
CYAN='\033[0;36m'

# Function to check if a command exists
command_exists() {
    command -v "$1" &>/dev/null
}

# Function to prompt for the API key if not set
get_api_key() {
    echo -e "${CYAN}Please enter your Sports API key:${RESET}"
    read -r API_KEY
    if [ -z "$API_KEY" ]; then
        echo -e "${RED}API key cannot be empty. Please try again.${RESET}"
        get_api_key
    else
        export API_KEY
        echo -e "${GREEN}API key set successfully.${RESET}"
    fi
}

# Function to display a progress bar
progress_bar() {
    local step=$1
    local duration=$2
    echo -n "$step"
    while [ $duration -gt 0 ]; do
        echo -n "."
        sleep 1
        ((duration--))
    done
    echo ""
}

# Step 1: Check if Node.js and npm are installed, and install if missing
echo -e "${BLUE}Step 1: Checking for Node.js and npm...${RESET}"
progress_bar "Checking Node.js and npm" 3
if ! command_exists nodejs || ! command_exists npm; then
    echo -e "${YELLOW}Node.js or npm not found. Installing Node.js and npm...${RESET}"
    sudo apt install -y nodejs npm || { echo -e "${RED}Failed to install Node.js and npm${RESET}"; exit 1; }
else
    echo -e "${GREEN}Node.js and npm are already installed.${RESET}"
    NODE_VERSION=$(node -v | cut -d '.' -f 1 | sed 's/[^0-9]*//g')
    if [ "$NODE_VERSION" -lt 16 ]; then
        echo -e "${YELLOW}Warning: Node.js version is lower than 16. Some features may not work.${RESET}"
    else
        echo -e "${GREEN}Node.js version is sufficient.${RESET}"
    fi
fi

# Step 2: Check if Python3 and pip3 are installed
echo -e "${BLUE}Step 2: Checking for Python3 and pip3...${RESET}"
progress_bar "Checking Python3 and pip3" 3
if ! command_exists python3; then
    echo -e "${RED}Error: Python3 is not installed.${RESET}"
    exit 1
fi
if ! command_exists pip3; then
    echo -e "${RED}Error: Pip3 is not installed.${RESET}"
    exit 1
fi

# Step 3: Create a virtual environment if it doesn't exist
echo -e "${BLUE}Step 3: Checking and creating virtual environment...${RESET}"
progress_bar "Creating virtual environment" 3
if [ ! -d "venv" ]; then
    python3 -m venv venv || { echo -e "${RED}Failed to create virtual environment${RESET}"; exit 1; }
    echo -e "${GREEN}Virtual environment created.${RESET}"
else
    echo -e "${GREEN}Virtual environment already exists.${RESET}"
fi

# Step 4: Activate the virtual environment
echo -e "${BLUE}Step 4: Activating the virtual environment...${RESET}"
progress_bar "Activating virtual environment" 3
source venv/bin/activate || { echo -e "${RED}Failed to activate virtual environment${RESET}"; exit 1; }
echo -e "${GREEN}Virtual environment activated.${RESET}"

# Step 5: Install Python dependencies from requirements.txt if available
echo -e "${BLUE}Step 5: Installing Python dependencies...${RESET}"
progress_bar "Installing Python dependencies" 3
if [ -f "requirements.txt" ]; then
    pip install --upgrade pip || { echo -e "${RED}Failed to upgrade pip${RESET}"; exit 1; }
    pip install -r requirements.txt || { echo -e "${RED}Failed to install Python dependencies${RESET}"; exit 1; }
else
    echo -e "${YELLOW}No requirements.txt found. Skipping dependency installation.${RESET}"
fi

# Step 6: Install or upgrade necessary dependencies like Flask, scikit-learn, pandas
echo -e "${BLUE}Step 6: Installing/upgrading necessary dependencies...${RESET}"
progress_bar "Installing dependencies" 3
pip install --upgrade flask==2.2.2 werkzeug==2.2.2 scikit-learn pandas numpy || { echo -e "${RED}Failed to install/upgrade necessary dependencies${RESET}"; exit 1; }

# Step 7: Check if the necessary environment variable (API_KEY) is set
echo -e "${BLUE}Step 7: Checking if the API_KEY environment variable is set...${RESET}"
progress_bar "Checking API_KEY" 2
if [ -z "$API_KEY" ]; then
    echo -e "${YELLOW}Warning: API_KEY environment variable is not set.${RESET}"
else
    echo -e "${GREEN}API_KEY environment variable is set.${RESET}"
fi

# Request and set the API key if not set
get_api_key

# Step 8: Check if Docker or Podman is installed
echo -e "${BLUE}Step 8: Checking for Docker/Podman...${RESET}"
progress_bar "Checking Docker/Podman" 3
check_container_tools() {
    if ! command_exists docker && ! command_exists podman; then
        echo -e "${RED}Error: Neither Docker nor Podman is installed.${RESET}"
        exit 1
    fi
}

check_container_tools

# Step 9: Determine which container tool is available
echo -e "${BLUE}Step 9: Determining available container tool...${RESET}"
progress_bar "Determining container tool" 3
if command_exists docker; then
    CONTAINER_TOOL="docker"
elif command_exists podman; then
    CONTAINER_TOOL="podman"
else
    echo -e "${RED}Error: Neither Docker nor Podman found.${RESET}"
    exit 1
fi

# Step 10-15: Clean up Docker/Podman containers, images, volumes, and networks
echo -e "${BLUE}Step 10: Cleaning up containers, images, and volumes...${RESET}"
stop_containers
remove_containers
remove_docker_images
remove_podman_images
remove_docker_volumes
remove_docker_networks

# Step 16: Build and run the app container
echo -e "${BLUE}Step 16: Building and running the app container...${RESET}"
progress_bar "Building and running app container" 3
build_and_run_app

echo -e "${GREEN}Setup complete!${RESET}"
