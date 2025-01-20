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

echo "Prerequisites setup completed successfully!"
