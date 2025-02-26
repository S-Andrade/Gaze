import cv2
import dlib
from deepgaze.head_pose_estimation import CnnHeadPoseEstimator

detector = dlib.get_frontal_face_detector()
predictor_path = "shape_predictor_68_face_landmarks.dat"
predictor = dlib.shape_predictor(predictor_path)

cap = cv2.VideoCapture(0)
estimator = CnnHeadPoseEstimator("model_path")

while True:
    ret, frame = cap.read()
    gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
    faces = detector(gray)
    
    for face in faces:
        landmarks = predictor(gray, face)
        pitch, yaw, roll = estimator.return_head_pose(landmarks)
        print(f"Pitch: {pitch}, Yaw: {yaw}, Roll: {roll}")

    cv2.imshow("Frame", frame)
    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

cap.release()
cv2.destroyAllWindows()