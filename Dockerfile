# Use the official Ubuntu base image
FROM ubuntu:latest

# Set the working directory inside the container
WORKDIR /app

# Copy the necessary files into the container
COPY requirements.txt /app/
COPY scripts/setup.sh /app/scripts/setup.sh
COPY scripts/reset.sh /app/scripts/reset.sh
COPY ../../src /app/src/
COPY ../../data /app/data/

# Install system dependencies and Python
RUN apt-get update && apt-get install -y \
    python3 \
    python3-venv \
    python3-pip \
    bash \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Set up the virtual environment and install the dependencies from requirements.txt
RUN python3 -m venv /app/venv \
    && /app/venv/bin/pip install --upgrade pip \
    && /app/venv/bin/pip install -r /app/requirements.txt

# Set the environment variable to point to the virtual environment
ENV PATH="/app/venv/bin:$PATH"

# Expose the application port (default Flask port)
EXPOSE 5000

# Run the app.py file when the container starts
CMD ["python", "src/app.py"]
