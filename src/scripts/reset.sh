#!/bin/bash

# Exit immediately if a command exits with a non-zero status
set -e

# Function to check if a process is running by its name
check_process() {
    pgrep -f "$1" &>/dev/null
}

# Check if the virtual environment is active
if [[ -z "$VIRTUAL_ENV" ]]; then
    echo "No virtual environment is currently active."
else
    echo "Virtual environment is active: $VIRTUAL_ENV"
fi

# Check if 'my_project' directory exists
if [ ! -d "my_project" ]; then
    echo "'my_project' directory does not exist."
else
    echo "'my_project' directory exists."
fi

# Check if Flask app is running
if check_process "flask"; then
    FLASK_PID=$(pgrep -f "flask")
    echo "Flask app is running with PID: $FLASK_PID"
else
    echo "No Flask app is currently running."
    FLASK_PID=""
fi

# If no virtual environment, Flask app, or 'my_project' directory exists, exit
if [ -z "$FLASK_PID" ] && [ ! -d "venv" ] && [ ! -d "my_project" ]; then
    echo "No active environment or Flask app found. Nothing to clean."
    exit 0
fi

# Ask if the user wants to stop the Flask app
if [ ! -z "$FLASK_PID" ]; then
    read -p "Do you want to stop the Flask application? (y/n): " stop_app
    if [ "$stop_app" == "y" ]; then
        echo "Stopping Flask app..."
        pkill -f "flask" || echo "No Flask app found running."
    else
        echo "Flask app is not stopped."
    fi
fi

# Ask if the user wants to clean the environment inside the container
read -p "Do you want to clean the environment inside the container? (y/n): " cleanup_env
if [ "$cleanup_env" == "y" ]; then
    # Clean up virtual environment
    if [ -d "venv" ]; then
        echo "Removing virtual environment..."
        rm -rf venv || { echo "Failed to remove virtual environment"; exit 1; }
    else
        echo "No virtual environment found to remove."
    fi

    # Ask if the user wants to remove 'my_project' directory
    if [ -d "my_project" ]; then
        read -p "Do you want to remove the 'my_project' directory? (y/n): " remove_project
        if [ "$remove_project" == "y" ]; then
            echo "Removing 'my_project' directory..."
            rm -rf my_project || { echo "Failed to remove 'my_project' directory"; exit 1; }
        else
            echo "'my_project' directory is not removed."
        fi
    else
        echo "'my_project' directory not found, nothing to remove."
    fi
else
    echo "Skipping environment cleanup inside the container."
fi

echo "Environment cleanup inside the container complete."
exit 0
