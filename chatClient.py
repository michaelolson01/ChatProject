#!/usr/bin/python3

import socket
import threading
import enum
import time
import sys

class clientState(enum.Enum):
    Waiting = 0
    PM = 1
    DM = 2
    EX = 3
    WaitingPMConf = 4
    WaitingPassword = 5
    WaitingForCommand = 6

username = ''
iAmRunning = True
currentState = clientState.Waiting
onlineList = []
listReceived = False
    
def printHelp():
    print("Enter PM for public message, DM for direct message, HP for help or EX to exit):")

def closeClient():
    global currentState
    global iAmRunning
    
    currentState = clientState.EX
    iAmRunning = False
    client.close()
    
def getFromServer():
    global listReceived
    global onlineList
    global currentState
    global iAmRunning

    
    while iAmRunning:
        try:
            message = client.recv(1024).decode('ascii')
            if (currentState == clientState.WaitingPassword):
                commandPart = message[0:8]
                if commandPart == 'USERNAME':
                    print(message[8:])
                    client.send(username.encode('ascii'))
                elif commandPart == 'PASSWORD':
                    acceptable = False
                    while not acceptable:
                        password = input("Please enter password: ")
                        if (password == ""):
                            print("Please try again")
                            continue
                        else:
                            acceptable = True
                    client.send(password.encode('ascii'))
                elif commandPart == 'SUCCESS!':
                    print(message[8:])
                    print('Log in successful')
                    currentState = clientState.Waiting
                elif commandPart == 'CLOSENOW':
                    print(message[8:])
                    print('Log in unsuccessful')
                    closeClient()
                else:
                    print(message)
                
            elif (currentState == clientState.DM):
                # we sent a DM message, so get get back list of eligable recipients.
                if (message[0] == '['):
                    # remove the beginning and the end
                    string = message[2:-2]
                    # split the list into a user list.
                    onlineList = string.split("', '")
                    listReceived = True
                else:
                    print(message)
            elif message == 'CLOSENOW':
                print("User is already online... quiting")
                closeClient()
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
            closeClient()
            exit(0)
            break

def sendToServer():
    global listReceived
    global onlineList
    global currentState
    global iAmRunning

    count = 0
    
    printHelp()
    while iAmRunning:
        if (currentState == clientState.EX):
          closeClient()
          break
        elif (currentState == clientState.PM):
            message = input("Enter public message:")
            client.send(message.encode('ascii'))
            currentState = clientState.WaitingPMConf;
            count = 0
        elif (currentState == clientState.DM):
            successful = False
            cancel = False
            while (listReceived == False):
                # we gotta wait for the list to be fully received
                time.sleep(0.005)
            for i in range(0, len(onlineList)):
                print(str(i) + ": " + onlineList[i])
            while (not successful and not cancel):
                userNum = input("Enter number of recipient(-1 to cancel): ")
                try:
                    number = int(userNum)
                    if (number == -1):
                        cancel = True
                        client.send("CANCEL".encode('ascii'))
                    elif number in range(0, len(onlineList)):
                        successful = True
                        client.send(onlineList[int(userNum)].encode('ascii'))
                except:
                    successful = False
            if (successful):
                message = input("Enter direct message:")
                client.send(message.encode('ascii'))
            currentState = clientState.Waiting;
            listReceived = False
        elif (currentState == clientState.Waiting):
            printHelp()
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
            else:
                printHelp()
                continue
        elif (currentState == clientState.WaitingPMConf):
            count+=1;
            if (count > 100000):
                message = "REQ-CONF"
                client.send(message.encode('ascii'))
                count = 0
        else:
            # ignore it, state probably changed while we were doing something.
            count = 0

try:
    if (len(sys.argv) == 4):
        hostname = sys.argv[1]
        port = int(sys.argv[2])
        username = sys.argv[3]
    else:
        hostname = socket.gethostname()
        port = 56017
        username = input("Enter Username: ")
except:
    print("Usage:")
    print("$ ./chatclient.py Server_Name Port Username")  
    print("For example ")                                 
    print("$ ./chatclient.py 127.0.1.11 56017 Your_Name") 
    exit(0)                                               

# This needs to be handled by the server.

currentState = clientState.WaitingPassword
host = socket.gethostbyname(hostname)

client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
client.connect((host, port))

receiving = threading.Thread(target=getFromServer)
receiving.start()

sendToServer()

receiving.join()                

