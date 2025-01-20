# Use the official Ubuntu base image
FROM ubuntu:latest

# Set the working directory inside the container
WORKDIR /app

# Copy the necessary files into the container
COPY code/requirements.txt /app/
COPY code/source /app/source/
COPY code/prerequisites.sh /app/prerequisites.sh
COPY code/reset.sh /app/reset.sh

# Install system dependencies and Python
RUN apt-get update && apt-get install -y \
    python3 \
    python3-venv \
    python3-pip \
    bash \
    && rm -rf /var/lib/apt/lists/*

# Install the dependencies from requirements.txt
RUN python3 -m venv /app/venv \
    && /app/venv/bin/pip install --upgrade pip \
    && /app/venv/bin/pip install -r /app/requirements.txt

# Set the environment variable to point to the virtual environment
ENV PATH="/app/venv/bin:$PATH"

# Expose the application port
EXPOSE 5000

# Run the app.py file when the container starts
CMD ["python", "source/app.py"]
