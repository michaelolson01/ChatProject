#!/usr/bin/python3

import socket
import threading
import enum
import time

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
onlineList = []
listReceived = False
    
def printHelp():
    print("Enter PM for public message, DM for direct message, HP for help or EX to exit):")

def getFromServer():
    global listReceived
    global onlineList
    global currentState
    global iAmRunning

    
    while iAmRunning:
        try:
            message = client.recv(1024).decode('ascii')
            if (currentState == clientState.DM):
                # we sent a DM message, so get get back list of eligable recipients.
                if (message[0] == '['):
                    # remove the beginning and the end
                    string = message[2:-2]
                    # split the list into a user list.
                    onlineList = string.split("', '")
                    listReceived = True
                else:
                    print(message)
            elif message == 'USERNAME':
                client.send(username.encode('ascii'))
            elif message == 'PASSWORD':
                client.send(password.encode('ascii'))
            elif message == 'PM':
                currentState = clientState.PM
            elif message == 'DM':
                currentState = clientState.DM
            elif message == 'PM-CONF ':
                currentState = clientState.Waiting
            else:
                print(message)
        except:
            print("System error")
            client.close()
            break

def sendToServer():
    global listReceived
    global onlineList
    global currentState
    global iAmRunning

    count = 0
    
    printHelp()
    while iAmRunning:
        if (currentState == clientState.PM):
            message = input("Enter public message:")
            client.send(message.encode('ascii'))
            currentState = clientState.WaitingPMConf;
            count = 0
        elif (currentState == clientState.DM):
            while (listReceived == False):
                # we gotta wait for the list to be fully received
                time.sleep(0.005)
            for i in range(0, len(onlineList)):
                print(str(i) + ": " + onlineList[i])
            message = input("Choose recipient:")
            client.send(message.encode('ascii'))
            message = input("Enter direct message:")
            client.send(message.encode('ascii'))
            currentState = clientState.Waiting;
            listReceived = False
        elif (currentState == clientState.Waiting):
            message = input('')
            if (message == "PM" or message == "pm"):
                client.send("PM".encode('ascii'))
                currentState = clientState.PM
            elif (message == "HP" or message == "hp"):
                printHelp()
            elif (message == "DM" or message == "dm"):
                client.send("DM".encode('ascii'))
                currentState = clientState.DM
            elif (message =="EX" or message == "ex"):
                print("Exiting...")
                iAmRunning = False
                client.send("EX".encode('ascii'))
        elif (currentState == clientState.WaitingPMConf):
            count+=1;
            if (count > 100000):
                message = "REQ-CONF"
                client.send(message.encode('ascii'))
                count = 0
        else:
            # ignore it, state probably changed while we were doing something.
            count = 0


username = input("Enter Username: ")
password = input("Enter Password: ")

hostname = socket.gethostname()
host = socket.gethostbyname(hostname)
port = 56017

client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
client.connect((host, port))

receiving = threading.Thread(target=getFromServer)
receiving.start()

#writing = threading.Thread(target=sendToServer)
#writing.start()
sendToServer()

                
