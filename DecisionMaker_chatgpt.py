#!/usr/bin/python                                                                                                                                                                      

import socket
import multiprocessing
import json
import threading
import os
from openai import OpenAI
from datetime import datetime
from csv import writer
import re
from decision_maker_logger import init_logger
from ElmoV2API import ElmoV2API
import subprocess
from enum import Enum

class State(Enum):
    TALKING = 1
    THINKING = 2
    LISTENING = 3
    WAITING = 4

class Target(Enum):
    P2 = 2
    P3 = 3

class Participant():
    def __init__(self, id):
        self.id = id
        self.gazeTarget = ""
        self.isLookingAtRobot = False
        self.isTalkingToRobot = False
        self.isTalking = False
        self.currentTranscript= ""       
        self.currentCluster = -1
        self.currentDuration = 0
        self.transcripts= []      
        self.clusters = []
        self.durations = []
        self.listKeywords = []
        self.textToSay = ""
        self.history = []

robot_ip = "192.168.0.101"
robot = ElmoV2API(robot_ip, debug=False)
robot.enable_behavior(name="look_around", control = False)
robot.set_pan(0)
robot.set_tilt(-10)
robot.set_pan_torque(True)
robot.set_tilt_torque(True)
robot.update_leds_icon("nothing.png")
robot.set_screen("simple-blink.gif")

def load_api_key(secrets_file="..\\secrectsChatGPT.json"):
    with open(secrets_file) as f:
        secrets = json.load(f)
    return secrets["OPENAI_API_KEY"]

logger = init_logger("Reactive", "Reactive_decision_maker.log")

try:
    logger.log_info("Creating OpenAI client...")
    client = OpenAI(
        # defaults to os.environ.get("OPENAI_API_KEY")
        api_key=load_api_key(),
    )
    os.environ["OPENAI_API_KEY"] =load_api_key()
    logger.log_info("OpenAI client created.")
except Exception as e:
    logger.log_exception("An unexpected error occurred while creating OpenAI client", e)
    raise


def chatGPT(messages, model="gpt-4o-mini"):
    response = client.chat.completions.create(
        model=model,
        messages=messages,
        temperature=0, # this is the degree of randomness of the model's output
    )
    return response.choices[0].message.content.strip()


def getPromptAnswer(query, history):
    return [{"role": "system", "content": f"""
        És um agente útil que responde a perguntas sobre conhecimento geral. A tua tarefa é:
        Responder à consulta atual do utilizador ({query}) com um máximo de 10 palavras.
        Considerar o histórico de consultas e respostas ({history}) para garantir consistência na conversa.
        A tua resposta deve ser simpática e com um toque engraçado.
        Nota: Usa português europeu.
        Se deres uma boa resposta eu dou-te 10 dolares.
    """}] 


def getAnwser(message, history):
    
    messages =  getPromptAnswer(message, history)

    response = chatGPT(messages)
        
    return response

global tagFinished
tagFinished = None
def say(text):
    global tagFinished
    tagFinished = False
    logger.log_info(f"start say")
    #print(text)
    subprocess.call(f"""C:\\Windows\\System32\\WindowsPowerShell\\v1.0\\powershell.exe Add-Type -AssemblyName 'System.Speech'; $speaker = new-object System.Speech.Synthesis.SpeechSynthesizer; $speaker.SelectVoice('Vocalizer Expressive Felipe Harpo 22kHz'); $speaker.Speak('{text}');""", shell=True)
    logger.log_info(f"end say")
    tagFinished = True

def decisionMaker(shared_data, shared_data_lock):
    global tagFinished
    #print("hello")
    logger.log_info(f"Decision Maker started")
    while True:
        #print(str(shared_data["2"].gazeTarget) + "  " + str(shared_data["3"].gazeTarget))
        logger.log_info("DecisionMaker: " + str(shared_data["state"]) + " - " + str(shared_data["target"]))

        if shared_data["state"] == State.WAITING:
            #print(str(shared_data["2"].isLookingAtRobot) + "  " + str(shared_data["3"].isLookingAtRobot))
            if shared_data["2"].isLookingAtRobot == False and shared_data["3"].isLookingAtRobot == False:
                robot.set_pan(0)
                logger.log_info(f"Both participants are not looking at the robot: Robot look front")
                #print("Front")

            elif shared_data["2"].isLookingAtRobot == True and shared_data["3"].isLookingAtRobot == True:

                totaltime2 = sum(shared_data["2"].durations)
                totaltime3 = sum(shared_data["3"].durations)

                if totaltime2 > totaltime3:
                    robot.set_pan(-40)
                    logger.log_info(f"Both participants are looking at the robot: Robot look right")
                    #print("Right")
                
                if totaltime3 > totaltime2:
                    robot.set_pan(40)
                    logger.log_info(f"Both participants are looking at the robot: Robot look left")
                    #print("Left")

            elif shared_data["2"].isLookingAtRobot == True:
                robot.set_pan(40)
                logger.log_info(f"Robot look left")
                #print("Left")

            elif shared_data["3"].isLookingAtRobot == True:
                robot.set_pan(-40)
                logger.log_info(f"Robot look right")
                #print("Right")

        elif shared_data["state"] == State.LISTENING:
            #print(str(shared_data["state"]) + " - " + str(shared_data["target"]))
            if shared_data["target"] == Target.P2:
                robot.set_pan(40)
                #print("Left")
                logger.log_info(f"Robot look left")
                #backchanel
                logger.log_info(f"Robot backchanneling")
                #print("Left backchanneling")

            if shared_data["target"] == Target.P3:
                robot.set_pan(-40)
                #print("Right")
                logger.log_info(f"Robot look right")
                #backchanel
                logger.log_info(f"Robot backchanneling")
                #print("Right backchanneling")
        
        elif shared_data["state"] == State.THINKING:
            #print(str(shared_data["state"]) + " - " + str(shared_data["target"]))
            id = ""
            if shared_data["target"] == Target.P2:
                robot.set_pan(40)
                #print("Left")
                logger.log_info(f"Robot look left")
                robot.set_screen("simple-think.gif")
                logger.log_info(f"Robot thinking eyes")
                id = "2"
                #print("Left thinking")

            if shared_data["target"] == Target.P3:
                robot.set_pan(-40)
                #print("Right")
                logger.log_info(f"Robot look right")
                robot.set_screen("simple-think.gif")
                logger.log_info(f"Robot thinking eyes")
                id = "3"
                #print("Right thinking")
            
            p = shared_data[id]

            logger.log_info(f"Question to participant {id}: {p.currentTranscript}")
            #threading.Thread(target = say, args=("Deixa-me pensar...", )).start()
            logger.log_info(f"Answer to participant {id}")
            print(">" + p.currentTranscript)
            response = getAnwser(p.currentTranscript, p.history)
            logger.log_info(f"Answer to participant {id}: {response}")
            print(">" + response)
            #print("end response")
            p.history += [[p.currentTranscript, response]]
            if len(p.history) > 5:
                p.history = p.history[-5:]
        
            p.currentTranscript = ""
            p.textToSay = response
            p.isTalkingToRobot = False
            with shared_data_lock:
                shared_data[id] = p
                logger.log_info(f"Participant 2 info updated")
                shared_data["state"] = State.TALKING
            tagFinished = None
            robot.set_screen(image="simple-blink.gif")
            logger.log_info(f"Robot blink eyes")          

        elif shared_data["state"] == State.TALKING:
                #print(str(shared_data["state"]) + " - " + str(shared_data["target"]))
                id = ""
                if shared_data["target"] == Target.P2:
                    robot.set_pan(40)
                    #print("Left")
                    logger.log_info(f"Robot look left")
                    id = "2"
                    #print("say left")

                if shared_data["target"] == Target.P3:
                    robot.set_pan(-40)
                    #print("Right")
                    logger.log_info(f"Robot look right")
                    id = "3"
                    #print("say right")

                
                if tagFinished == None:
                    logger.log_info(f"Start say")
                    #print("start say")
                    threading.Thread(target = say, args=(p.textToSay, )).start()
                    with shared_data_lock:
                        p = shared_data[id]
                        p.textToSay = ""
                        shared_data[id] = p
                    
                if tagFinished == True:
                    logger.log_info(f"End say")
                    with shared_data_lock:
                        shared_data["state"] = State.WAITING
                        shared_data["target"] = None
                        shared_data["lock"] = False
                    #print("end say")
                               
with open("keywords.json", encoding='utf-8') as json_data:
        keywords_list = json.load(json_data)
        keywords_list = set(map(str.lower,keywords_list))

def getKeywords(text):
    bad_chars = [';', ':', '!', ",", "?", ".", "-"]
    text = ''.join(i for i in text if not i in bad_chars)
    list_words = text.split()
    list_words = set(map(str.lower,list_words))

    if (list_words & keywords_list):
        return list(list_words & keywords_list)
    else:
        return []

def on_new_client_text(conn, addr, id, shared_data, shared_data_lock):
    print(f'Connected by {addr}')
    logger.log_info(f"Connected to participant {id} stt")
    say(f"Connectei com o STT do participante {id}")
    target = None
    for t in (Target):
        if t.value == int(id):
            target = t

    with conn:
        while True:
            msg = conn.recv(1024)
            if not msg:
                break
            msg = msg.decode()
            logger.log_info(f"Recived stt message from client {id}: {msg}")
            
            print(id+" - "+msg)
            #print(shared_data["state"])
            p = shared_data[id]
            print(p.currentTranscript)
            print(p.isTalking)

            msg = re.split(r'\[|\]| \[|\] ', msg)
            msg = list(filter(None, msg))

            if shared_data["state"] != State.LISTENING or (shared_data["state"] == State.LISTENING and shared_data["target"] != target):
                if p.isLookingAtRobot == True and shared_data["lock"] == False:
                    with shared_data_lock:
                        shared_data["state"] = State.LISTENING
                        shared_data["target"] = target
                        shared_data["lock"] = True
                        logger.log_info(f"Participant {id} is talking and looking at the robot")
                else:
                    if msg[0] == "End Talking":
                        p.isTalking = False
                        p.currentDuration = float(msg[1])
                        p.currentCluster = -1
                        p.durations += [float(msg[1])]
                        p.transcripts += [[]]       
                        p.clusters += [[]]
                        logger.log_info(f"Participant {id} ended talking")
                        #print("end")
                    else:
                        if p.isTalking == False:
                            p.isTalking = True
                            p.currentTranscript = ""
                            p.currentCluster = -1
                            p.currentDuration = 0
                            p.transcripts += [[]]       
                            p.clusters += [[]]
                        p.currentTranscript += " " + msg[0]     
                        p.currentCluster = int(msg[2])
                        p.currentDuration += float(msg[1])
                        p.transcripts[-1] += [msg[0]]      
                        p.clusters[-1] += [int(msg[2])]
                        logger.log_info(f"Participant {id} is talking")

            if shared_data["state"] == State.LISTENING and shared_data["target"] == target:
                    if msg[0] == "End Talking":
                        p.isTalking = False
                        p.currentDuration = float(msg[1])
                        p.currentCluster = -1
                        p.durations += [float(msg[1])]
                        p.transcripts += [[]]       
                        p.clusters += [[]]
                        logger.log_info(f"Participant {id} ended talking")
                        #print("end")
                        #print(p.currentTranscript)
                        if not re.search("^\s*$", p.currentTranscript):
                            #print("entrei")
                            with shared_data_lock:
                                shared_data["state"] = State.THINKING
                        else:
                            with shared_data_lock:
                                shared_data["state"] = State.WAITING
                                shared_data["lock"] = False
                                shared_data["target"] = None
                        #print(shared_data["state"])
                    else:
                        if p.isTalking == False:
                            p.isTalking = True
                            p.currentTranscript = ""
                            p.currentCluster = -1
                            p.currentDuration = 0
                            p.transcripts += [[]]       
                            p.clusters += [[]]
                        logger.log_info(f"Participant {id} is talking and looking at the robot")
                        print("~" + p.currentTranscript)
                        p.currentTranscript += " " + msg[0]     
                        print("*" + p.currentTranscript) 
                        p.currentCluster = int(msg[2])
                        p.currentDuration += float(msg[1])
                        p.transcripts[-1] += [msg[0]]      
                        p.clusters[-1] += [int(msg[2])]

                              
            with shared_data_lock:    
                shared_data[id] = p
                logger.log_info(f"Participant {id} info updated")

def on_new_client_gaze(conn, addr, id, shared_data, shared_data_lock):
    print(f'Connected by {addr}')
    logger.log_info(f"Connected to participant {id} gaze")
    threading.Thread(target = say, args=(f"Conectei com o gaze do participante {id}", )).start()
    #sent_startTime, sent_endTime
    with conn:
        while True:
            msg = conn.recv(1024)
            if not msg:
                break
            msg = msg.decode()
            logger.log_info(f"Recived gaze message from client {id}: {msg}")
            #g = list(msg.split(" "))
            #print(shared_data[id].gazeTarget)
            p = shared_data[id]
            if "Right" in msg:
                p.gazeTarget = "Right"
                if id == "2":
                    p.isLookingAtRobot = True
                    logger.log_info(f"Participant {id} is looking at the robot")
                else:
                    p.isLookingAtRobot = False
                    logger.log_info(f"Participant {id} is not looking at the robot")
            elif "Left" in msg:
                p.gazeTarget = "Left"
                if id == "3": 
                    p.isLookingAtRobot = True
                    logger.log_info(f"Participant {id} is looking at the robot")
                else:
                    p.isLookingAtRobot = False
                    logger.log_info(f"Participant {id} is not looking at the robot")
            else:
                p.gazeTarget = "Center"
                p.isLookingAtRobot = False
            #print(p.gazeTarget)
            with shared_data_lock:
                shared_data[id] = p
                logger.log_info(f"Participant {id} info updated")
      
def main():
    HOST = '192.168.0.104'
    PORT = 50009
    with multiprocessing.Manager() as manager:
        shared_data = manager.dict({"2": Participant("2"), "3": Participant("3"), "state":State.WAITING, "target":None, "lock": False})
        shared_data_lock = manager.Lock()
        try:
            logger.log_info("Starting decisionMaker")
            process = multiprocessing.Process(target=decisionMaker, args=(shared_data, shared_data_lock))
            process.start()
            logger.log_info("decisionMaker started.")
        except Exception as e:
            logger.log_exception("An unexpected error occurred while starting decisionMaker", e)
            raise

        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as server_socket:
            try:
                logger.log_info("Creating server socket")
                server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
                server_socket.bind((HOST, PORT))
                server_socket.listen()
                print(f'Server listening on {HOST}:{PORT}')
                threading.Thread(target = say, args=("Estou pronto para conectar", )).start()
                logger.log_info("Server socket created.")
            except Exception as e:
                logger.log_exception("An unexpected error occurred while creating server socket", e)
                raise

            i = 0
            while True:
                try:
                    logger.log_info("Connecting to client")
                    conn, addr = server_socket.accept()
                    first = conn.recv(1024)
                    first = first.decode()
                    #print(first)
                    id = ''.join(x for x in first if x.isdigit())
                    #print(id)
                    logger.log_info(f"Connected to {first}")
                except ConnectionRefusedError:
                    logger.log_error("Connection to client.")
                except Exception as e:
                    logger.log_exception("An unexpected error occurred while connecting to client", e)
                    raise 


                if "Text" in first:
                    try:
                        logger.log_info(f"Starting on_new_client_text({id})")
                        process = multiprocessing.Process(target=on_new_client_text, args=(conn, addr,id ,shared_data, shared_data_lock))
                        process.start()
                        logger.log_info(f"on_new_client_text({id}) started.")
                    except Exception as e:
                        logger.log_exception(f"An unexpected error occurred while starting on_new_client_text({id})", e)
                        raise

                if "gaze" in first:
                    try:
                        logger.log_info(f"Starting on_new_client_gaze({id})")
                        process = multiprocessing.Process(target=on_new_client_gaze, args=(conn, addr, id, shared_data, shared_data_lock))
                        process.start()
                        logger.log_info(f"on_new_client_gaze({id}) started.")
                    except Exception as e:
                        logger.log_exception(f"An unexpected error occurred while starting on_new_client_gaze({id})", e)
                        raise
                conn.close()

if __name__ == '__main__':
    multiprocessing.set_start_method('spawn')
    main()



