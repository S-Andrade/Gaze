# Use a base image with Python and OpenCV
FROM python:3.8

# Install dependencies, including graphics libraries
RUN apt-get update && \
    apt-get install -y libgl1-mesa-glx && \
    pip install opencv-python && \
    pip install opencv-python-headless && \
    pip install mediapipe && \
    pip install joblib && \
    pip install numpy && \
    pip install scikit-learn

# Copy the Python script into the container
COPY gazeclient.py /app/gazeclient.py
COPY gaze_logger.py /app/gaze_logger.py
COPY poly.pkl /app/poly.pkl

# Set the working directory
WORKDIR /app

# Run the Python script
CMD ["python", "gazeclient.py", "2"]