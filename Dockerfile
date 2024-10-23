# Use Ubuntu as the base image
FROM ubuntu:20.04

# Set the working directory
WORKDIR /app

# Set environment variables to avoid prompts during installation
ENV DEBIAN_FRONTEND=noninteractive

# Install Python 3.8, pip, and other necessary system packages
RUN apt-get update && apt-get install -y \
    python3 \
    python3-pip \
    python3-opencv \
    libgl1-mesa-glx \
    && rm -rf /var/lib/apt/lists/*

# Copy your Python scripts and model file into the container
COPY gazeclient.py gaze_logger.py poly.pkl ./

# Install Python dependencies
RUN pip3 install --no-cache-dir \
    "joblib" \
    "numpy>=1.20" \
    "scikit-learn" \
    "mediapipe" \
    "matplotlib"

# Default command to run your Python script
# CMD ["python3", "gazeclient.py", "2"]