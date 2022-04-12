#!/usr/bin/python3

import socket
import threading
import enum


class clientState(enum.Enum):
    Waiting = 0
    PM = 1
    DM = 2
    EX = 3
    WaitingPMConf = 4
    WaitingDMConf = 5

username = ''
password = ''
iAmRunning = True
currentState = clientState.Waiting

    
def getFromServer():
    global currentState
    global iAmRunning
    while iAmRunning:
        try:
            message = client.recv(1024).decode('ascii')
            if message == 'USERNAME':
                client.send(username.encode('ascii'))
            elif message == 'PASSWORD':
                client.send(password.encode('ascii'))
            elif message == 'PM':
                currentState = clientState.PM
            elif message == 'DM':
                currentState = clientState.DM
            elif message == 'PM-CONF':
                currentState = clientState.Waiting
            else:
                print(message)
        except:
            print("System error")
            client.close()
            break

def sendToServer():
    global currentState
    global iAmRunning

    count = 0
    
    while iAmRunning:
        if (currentState == clientState.PM):
            message = input("Enter public message:")
            client.send(message.encode('ascii'))
            currentState = clientState.WaitingPMConf;
            count = 0
        elif (currentState == clientState.DM):
            message = input("Enter direct message:")
            client.send(message.encode('ascii'))
            currentState = clientState.Waiting;
        elif (currentState == clientState.Waiting):
            message = input("Enter command (PM/DM/EX):")
            if (message == "PM"):
                client.send(message.encode('ascii'))
                currentState = clientState.PM
            elif (message == "DM"):
                client.send(message.encode('ascii'))
            elif (message =="EX"):
                print("Exiting...")
                iAmRunning = False
                client.send(message.encode('ascii'))
        elif (currentState == clientState.WaitingPMConf):
            count+=1;
        else:
            print("Bad input.")


username = input("Enter Username: ")
password = input("Enter Password: ")

hostname = socket.gethostname()
host = socket.gethostbyname(hostname)
port = 56017

client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
client.connect((host, port))

receiving = threading.Thread(target=getFromServer)
receiving.start()

writing = threading.Thread(target=sendToServer)
writing.start()

                
