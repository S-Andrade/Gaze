import cv2
import numpy as np
import mediapipe as mp

# Initialize MediaPipe Pose
mp_pose = mp.solutions.pose
pose = mp_pose.Pose()

# Initialize drawing utility
mp_drawing = mp.solutions.drawing_utils

# Start video capture
cap = cv2.VideoCapture(2)

while True:
    ret, frame = cap.read()
    if not ret:
        break
    # Show the frame
    cv2.imshow('Body Tracking', frame)
    
    # Break the loop with 'q'
    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

# Release the capture and close windows
cap.release()
cv2.destroyAllWindows()
