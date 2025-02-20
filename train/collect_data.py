
import time
import csv
from playsound import playsound
import sys
import random
import numpy as np
import cv2
import mediapipe as mp
import threading
import serial
import warnings
warnings.filterwarnings('ignore')


#robot_ip = "192.168.0.103"
#robot = ElmoV2API(robot_ip, debug=False)
#robot.enable_behavior(name="look_around", control = False)
#robot.set_pan(0)
#robot.set_tilt(-10)
#robot.set_pan_torque(True)
#robot.set_tilt_torque(True)
#robot.update_leds_icon("nothing.png")
#robot.set_screen("simple-blink-green.gif")

#arduino = serial.Serial(port='COM3', baudrate=9600, timeout=.1)

global tag
tag = False    

def human():
    global tag
    time.sleep(10)
    tag = True

def robot(sound_file):
    global tag
   
    time.sleep(5)
   
    if sound_file == "ask_robot1.mp3":
        playsound("elmo.mp3")
    if sound_file == "ask_robot2.mp3":
        playsound("sun.mp3")
    tag = True

def card():
    global tag
    time.sleep(10)
    tag = True


def main(participant,filename):
    global tag
    mp_pose = mp.solutions.pose
    pose_mp = mp_pose.Pose()
    cap = cv2.VideoCapture(0)
        

    getlabel = {"Left":0, "Right":0, "Center":0}
    data = {"Left":[], "Right":[], "Center":[]}

    gettarget = {}
    angle = 90
    
    if participant == "2":
        gettarget = {"Left":"HUMAN", "Right":"ROBOT", "Center":"CARD"}
        angle = 0
    
    if participant == "3":
        gettarget = {"Left":"ROBOT", "Right":"HUMAN", "Center":"CARD"}
        angle = 90

    ask_human = ["ask_human1.mp3", "ask_human2.mp3"]
    ask_robot = ["ask_robot1.mp3", "ask_robot2.mp3"]

    while True:
        poses = [label for label, value in getlabel.items() if value < 2]
        if len(poses) == 0:
            break

        pose = random.choice(poses)
        getlabel[pose] += 1

        target = gettarget[pose]
        tag = False
        if target == "HUMAN":
            sound_file = random.choice(ask_human)
            ask_human.remove(sound_file)
            playsound(sound_file)
            threading.Thread(target = human).start()
        if target == "ROBOT":
            sound_file = random.choice(ask_robot)
            ask_robot.remove(sound_file)
            playsound(sound_file)
            threading.Thread(target = robot, args=(sound_file,)).start()
        if target == "CARD":
            playsound("read_text.mp3")
            threading.Thread(target = card).start()
        
        start = time.time()
        data_pose = []
        j = 0
        while j < 125:
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
        print(time.time() - start)
        
        if tag:
            playsound("bip.mp3")
            
    playsound("bip.mp3")     
    p = [(p, len(v)) for p,v in data.items()]
    print(p)
            
    filename = "data/" + participant + "/" + filename + ".tsv"
    with open(filename, 'w', encoding='utf8', newline='') as tsv_file:
                tsv_writer = csv.writer(tsv_file, delimiter='\t', lineterminator='\n')
                for pose in data.keys():
                      tsv_writer.writerow([pose])
                      for line in data[pose]:
                            tsv_writer.writerow(line)

if __name__ == '__main__':
    main(sys.argv[1],sys.argv[2])
