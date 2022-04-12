#!/usr/bin/python3

import socket
import threading
import requests
import enum

class clientState(enum.Enum):
    Waiting = 0 # online
    PM = 1 # Working on a PM
    DM = 2 # Working on a DM
    EX = 3 # offline

# clientList of  clientData ['socket client info' 'username' 'client state']
clientList = []
password = []
userfile = None

def isInClientList(client):
    for n in range(0,  len(clientList)):
        if (clientList[n][0] == client):
            return True
    return False

def getClientData(client):
    for i in range(0,  len(clientList)):
        if (clientList[i][0] == client):
            return clientList[i]
    return None

def setClientState(client, state):
    for i in range(0, len(clientList)):
        if (clientList[i][0] == client):
            clientList[i][2] = state
            return True
    return False

def getClientState(client):
    clientData = getClientData(client)
    if (clientData != None ):
        return clientData[2]
        
def getClientUsername(client):
    clientData = getClientData(client)
    if (clientData != None):
        return clientData[1]

def readuserfile():
    try:
        print('Reading in user data...')
        userfile = open('users.dat', 'r+')
        while currec != '':
            currec = userfile.readlin()
            print(currec)
    except:
        print('User data does not exist, Creating...')
        userfile = open('users.dat', 'w+')

def handle(client):
    cState = clientState.Waiting
    cUsername = getClientUsername(client)
    while True:
        try:
            # wait for a message
            message = client.recv(1024)
            if (cState == clientState.Waiting):
                # What do we do when we get a message from a waiting client?????
                # This is where we get the initial commands of the client....
                # We got a PM Message - 
                if (message.decode('ascii') == "PM"):
                    print("Public Message from " + cUsername)
                    cState = clientState.PM
                    setClientState(client, clientState.PM)
                    print("State set")
                    client.send("PM".encode('ascii'))
                    print("PM response sent")
                elif (message.decode('ascii') == "DM"):
                    print("Direct Message from " + cUsername)
                elif (message.decode('ascii') == "EX"):
                    print(cUsername + " is leaving...")
                    clientDisconnect(client)
                    break;
                else:
                    print("Unexpected Message.")
            elif (cState == clientState.PM):
                # We received the public message, now distribute it.
                publicMessage(message, client)
                # Send a confirmation, and set us back to waiting....
                client.send("PM-CONF".encode('ascii'))
                cState = clientState.Waiting
                setClientState(client, clientState.Waiting)
            elif (cState == clientState.DM):
                # We are in middle of doing a direct message
                print("Direct message")
            else:
                print("System Error.... Unknown state.")
        except:
            print("Handle Error...")
            if (isInClientList(client)):
                clientDisconnect(client)
            break;

def publicMessage(message, sender):
    if (sender == host):
        messageUser = 'Server'
    else:
        curClient = getClientData(sender)
        messageUser = curClient[1]

    messageout = messageUser + ":" + message.decode('ascii')
    for client in clientList:
        if (client[2] != clientState.EX):
            print(client[1] + " " + str(client[2]))
            client[0].send(messageout.encode('ascii'))

def directMessage(message, receiver, sender):
    print("Send a direct message to " + getClientUsername(receiver))
    
    receiver.send(message.encode('ascii'))

def clientDisconnect(client):
    print("Client is disconnecting: " + getClientUsername(client))
    setClientState(client, clientState.EX)
    client.close()

def receiveMessage():
    while True:
        client, address = server.accept()
        print("Connected with {}".format(str(address)))

        client.send('USERNAME'.encode('ascii'))
        username = client.recv(1024).decode('ascii')
        client.send('PASSWORD'.encode('ascii'))
        password = client.recv(1024).decode('ascii')
        if (isInClientList(client)):
            directMessage("Welcome back!", client, server)
            setClientState(client, clientState.Waiting)
        else:
            clientData = []
            clientData.append(client)
            clientData.append(username)
            clientData.append(clientState.Waiting)
            clientList.append(clientData)
            directMessage("Welcome to the server!", client, server)

        publicMessage('{} joined!'.format(username).encode('ascii'), host)
        
        thread = threading.Thread(target=handle, args=(client,))
        thread.start()

hostname = socket.gethostname()
host = socket.gethostbyname(hostname)
port = 56017
print("IP Address is " + host + ":" + str(port))

server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
server.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
server.bind((host,port))
server.listen()
print("Server is listening...")
receiveMessage()

userlist.close()
