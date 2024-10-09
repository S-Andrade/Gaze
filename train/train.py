from sklearn import svm, datasets
import sklearn.model_selection as model_selection
from sklearn.metrics import accuracy_score
from sklearn.metrics import f1_score
import csv
import numpy as np
import time
import glob, os
import joblib
from sklearn import model_selection
from sklearn import svm
from sklearn.preprocessing import StandardScaler
from sklearn.metrics import accuracy_score, f1_score, precision_score, recall_score
import numpy as np
import cv2
import mediapipe as mp
import warnings
warnings.filterwarnings('ignore')

def getData():
    pose = ""
    X = []
    y = []
    l = ["./data/2"]
    #l = [".\\data\\train"]
    for ls in l:
        os.chdir(ls)    
        for file in glob.glob("*.tsv"):    
            with open(file, encoding="utf-8") as file:       
                tsv_file = csv.reader(file, delimiter="\t")
                for line in tsv_file:
                    if len(line) == 1:
                        pose = line[0]
                    else:
                        X.append(line)
                        y.append(pose)
        os.chdir("../..")
    return np.array(X), np.array(y)

def training(X,y):
    X_train, X_test, y_train, y_test = model_selection.train_test_split(X, y, train_size=0.80, test_size=0.20, random_state=101)
    rbf = svm.SVC(kernel='rbf', gamma=0.5, C=0.1).fit(X_train, y_train)
    poly = svm.SVC(kernel='poly', degree=3, C=1).fit(X_train, y_train)

    poly_pred = poly.predict(X_test)
    rbf_pred = rbf.predict(X_test)

    poly_accuracy = accuracy_score(y_test, poly_pred)
    poly_f1 = f1_score(y_test, poly_pred, average='weighted')
    print('Accuracy (Polynomial Kernel): ', "%.2f" % (poly_accuracy*100))
    print('F1 (Polynomial Kernel): ', "%.2f" % (poly_f1*100))

    rbf_accuracy = accuracy_score(y_test, rbf_pred)
    rbf_f1 = f1_score(y_test, rbf_pred, average='weighted')
    print('Accuracy (RBF Kernel): ', "%.2f" % (rbf_accuracy*100))
    print('F1 (RBF Kernel): ', "%.2f" % (rbf_f1*100))

    return poly, rbf

def trainingAll(X,y):
    
    rbf = svm.SVC(kernel='rbf', gamma=0.5, C=0.1).fit(X, y)
    poly = svm.SVC(kernel='poly', degree=3, C=1).fit(X, y)

    return poly, rbf

def run(poly,rbf):
    # Initialize MediaPipe Pose
    mp_pose = mp.solutions.pose
    pose = mp_pose.Pose()

    # Initialize drawing utility
    mp_drawing = mp.solutions.drawing_utils

    # Start video capture
    cap = cv2.VideoCapture(0)

    while True:
        ret, frame = cap.read()
        if not ret:
            break
        
        # Convert the frame to RGB for MediaPipe processing
        rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        
        # Process the frame with MediaPipe Pose
        results = pose.process(rgb_frame)
        
        if results.pose_landmarks:
            # Draw the pose landmarks on the frame
            mp_drawing.draw_landmarks(frame, results.pose_landmarks, mp_pose.POSE_CONNECTIONS)

            
            
            # Get shoulder landmarks
            landmarks = results.pose_landmarks.landmark
            landmarks = landmarks[:13]

            i =0

            temp = []
            for l in landmarks:
                temp += [l.x, l.y, l.z]
                
            
            poly_pred = poly.predict([temp])
            rbf_pred = rbf.predict([temp])
            #print(poly_pred[0]+" "+ rbf_pred[0])
            cv2.putText(frame, "poly: {}".format(poly_pred[0]), (10, 60),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 255, 255), 2)
            cv2.putText(frame, "rbf: {}".format(rbf_pred[0]), (10, 90),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 255, 255), 2)
            
        # Show the frame
        cv2.imshow('Body Tracking', frame)
        
        # Break the loop with 'q'
        if cv2.waitKey(1) & 0xFF == ord('q'):
            break

    # Release the capture and close windows
    cap.release()
    cv2.destroyAllWindows()
                            



X, y = getData()
poly, rbf = training(X,y)
joblib.dump(poly, 'poly.pkl')
joblib.dump(rbf, 'rbf.pkl')
#os.chdir(".\\data")
#poly = joblib.load('poly.pkl')
#rbf = joblib.load('rbf.pkl')
run(poly,rbf)