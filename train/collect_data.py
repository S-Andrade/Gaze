
import time
import csv
from playsound import playsound
import sys
import random
import numpy as np
import cv2
import mediapipe as mp
import warnings
warnings.filterwarnings('ignore')
     
def main(participant,filename):
    mp_pose = mp.solutions.pose
    pose_mp = mp_pose.Pose()
    cap = cv2.VideoCapture(0)
        

    getlabel = {"Left":0, "Right":0, "Down":0, "Front":0}
    data = {"Left":[], "Right":[], "Down":[], "Front":[]}

    
    if participant == "2":
        gettarget = {"Left":{"SHREK":0}, "Right":{"ROBOT":0}, "Down":{"PINK CUBE":0, "BLUE CUBE":0,"YELLOW CUBE":0,"PURPLE CUBE":0, "previous": ""}, "Front":{"RED CUBE":0, "GREEN CUBE":0,"ORANGE CUBE":0,"WHITE CUBE":0, "previous": ""}}

    
    if participant == "3":
        gettarget = {"Left":{"ROBOT":0}, "Right":{"SHREK":0}, "Down":{"PINK CUBE":0, "BLUE CUBE":0,"YELLOW CUBE":0,"PURPLE CUBE":0, "previous": ""}, "Front":{"RED CUBE":0, "GREEN CUBE":0,"ORANGE CUBE":0,"WHITE CUBE":0, "previous": ""}}

    end = True
    previous_target = ""
    i = 0
    while end:
        poses = [label for label, value in getlabel.items() if value < 8 and label != previous_target]
        pose = random.choice(poses)
        getlabel[pose] += 1
        if pose == "Left" or pose == "Right":
            targets = dict(gettarget[pose])
            targets = list(targets.keys())
            target = targets[0]
            previous_target = pose
            gettarget[pose][target] += 1
            
        
        if pose == "Front" or pose == "Down":
            targets = [target for target,value in gettarget[pose].items() if target != "previous" and target != gettarget[pose]["previous"] and value < 2]
            if len(targets) == 0:
                targets = [target for target,value in gettarget[pose].items() if target != "previous" and value < 2]
            target = random.choice(targets)
            gettarget[pose][target] += 1
            gettarget[pose]["previous"] = target

        print(pose + " > " + target)
        print(gettarget)
        print(getlabel)
        i+=1      

        file = target.replace(" ", "") + ".mp3"

        playsound(file)
        
        data_pose = []
        j = 0
        while j < 100:
            ret, frame = cap.read()
            if not ret:
                break
            
            # Convert the frame to RGB for MediaPipe processing
            rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            
            # Process the frame with MediaPipe Pose
            results = pose_mp.process(rgb_frame)
            
            if results.pose_landmarks:
                
                # Get shoulder landmarks
                landmarks = results.pose_landmarks.landmark
                landmarks = landmarks[:13]

                temp = []
                for l in landmarks:
                    temp += [l.x, l.y, l.z]

                data_pose.append(temp)
                print(j)
                j += 1

        data[pose] += data_pose
        i+=1
        
        if sum(getlabel.values()) == 32:
             end = False

    p = [(p, len(v)) for p,v in data.items()]
    print(p)

    playsound("bip.mp3")
        
            
    filename = "data/" + participant + "/" + filename + ".tsv"
    with open(filename, 'w', encoding='utf8', newline='') as tsv_file:
                tsv_writer = csv.writer(tsv_file, delimiter='\t', lineterminator='\n')
                for pose in data.keys():
                      tsv_writer.writerow([pose])
                      for line in data[pose]:
                            tsv_writer.writerow(line)


if __name__ == '__main__':
    main(sys.argv[1],sys.argv[2])
