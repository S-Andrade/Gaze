sudo docker build -t gaze .
sudo docker run --rm -it --device=/dev/video0:/dev/video0 gaze