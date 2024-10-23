#sudo docker build -t gaze .
sudo docker run --rm -it --device=/dev/video2:/dev/video2  -e DISPLAY=$DISPLAY -v /tmp/.X11-unix:/tmp/.X11-unix gaze