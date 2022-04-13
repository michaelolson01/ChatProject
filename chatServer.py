#!/usr/bin/python3

import socket
import threading
import requests
import enum
import sys
import time

class clientState(enum.Enum):
    Waiting = 0 # online
    PM = 1 # Working on a PM
    DM = 2 # Working on a DM
    EX = 3 # offline

# clientList of  clientData ['socket client info' 'username' 'client state' 'password']
clientList = []
password = []
userfile = None
receiveThread = None

def isInClientList(username):
    for n in range(0,  len(clientList)):
        if (clientList[n][1] == username):
            return True
    return False

def isOnline(username):
    for n in range(0,  len(clientList)):
        if (clientList[n][1] == username):
            if clientList[n][2] == clientState.EX:
                return False
    return True

def setUserState(username, state):
    for n in range(0,  len(clientList)):
        if (clientList[n][1] == username):
            clientList[n][2] = state
    
def getClientData(client):
    for i in range(0,  len(clientList)):
        if (clientList[i][0] == client):
            return clientList[i]
    return None

def updateUser(username, data):
    for i in range(0,  len(clientList)):
        if (clientList[i][1] == username):
            clientList[i][0] = data

def setClientState(client, state):
    for i in range(0, len(clientList)):
        if (clientList[i] == client):
            clientList[i][2] = state
            return True
    return False

def getClientState(client):
    clientData = getClientData(client)
    if (clientData != None):
        return clientData[2]
        
def getClientUsername(client):
    clientData = getClientData(client)
    if (clientData != None):
        return clientData[1]
    else:
        return "Server"

def getClientByUsername(username):
    for i in range(0, len(clientList)):
        if (clientList[i][1] == username):
            return clientList[i][0]
    return None

def getOnlineList():
    online = []
    for i in range(0,  len(clientList)):
        if (clientList[i][2] != clientState.EX):
            online.append(clientList[i][1])
    return online
    
def readUserFile():
    global clientList
    try:
        print('Reading in user data...')
        userfile = open('users.dat', 'r')
        currec = userfile.readline()
        while currec != '':
            record = []
            record.append("")
            record.append(currec.split('%')[0])
            record.append(clientState.EX)
            clientList.append(record)
            currec = userfile.readline()
        userfile.close()
        print(clientList)
    except:
        print('Unable to import user data')

def readUserPassword(user):
    try:
        print('Reading in user data...')
        userfile = open('users.dat', 'r+')
        currec = userfile.readline()
        while currec != '':
            record = currec.split("%")
            if record[0] == user:
                print(record[0] + " found")
                return record[1]
            print(currec)
            currec = userfile.readline()
        userfile.close()
    except:
        print('Unable to import user data')
        
def saveUserData(user, password):
    try:
        print('Writing user data')
        userfile = open('users.dat', 'a+')
        print('File open')
        stringToWrite = user + "%" + password + "%\n"
        print('String Created')
        userfile.write(stringToWrite)
    except:
        print('Error writing file')
        
def handle(client, username):
    if (isInClientList(username)):
        if (isOnline(username)):
            client.sendall("CLOSENOW".encode('ascii'))
            return
        else:
            passAttempts = 0
            successful = False
            updateUser(username, client)
            directMessage("Welcome back! Please enter your password\n", client, server)
            readPassword = readUserPassword(username)
            while (passAttempts < 3 and not successful):
                time.sleep(0.05)
                client.sendall('PASSWORD'.encode('ascii'))
                password = client.recv(1024).decode('ascii')
                print(str(readPassword) + " vs. " + str(password))
                if readPassword != password:
                    client.sendall(("Incorrect Password, try again. Attempts left : " + str(2-passAttempts)).encode('ascii'))
                    time.sleep(0.05)
                    passAttempts += 1
                else:
                    successful = True
            if (successful):
                client.sendall("SUCCESS!".encode('ascii'))
                setUserState(username, clientState.Waiting)
            else:
                client.sendall("CLOSENOW".encode('ascii'))
                return
                        
    else:
        clientData = []
        clientData.append(client)
        clientData.append(username)
        clientData.append(clientState.Waiting)
        clientList.append(clientData)
        directMessage('Welcome to the server!\n', client, server)
        directMessage('Please enter a new password', client, server)
        time.sleep(0.05)
        client.sendall('PASSWORD'.encode('ascii'))
        password = client.recv(1024).decode('ascii')
        time.sleep(0.05)
        client.sendall('SUCCESS!'.encode('ascii'))
        saveUserData(username, password)
            
        publicMessage('{} joined!'.format(username).encode('ascii'), host)


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
                    cState = clientState.PM
                    setUserState(cUsername, clientState.PM)
                    client.sendall("PM".encode('ascii'))
                elif (message.decode('ascii') == "DM"):
                    onlineList = getOnlineList()
                    reply = str(onlineList)
                    if (reply == 'None'):
                        client.sendall("['EmptyList']".encode('ascii'))
                    else:
                        client.sendall(reply.encode('ascii'))
                        cState = clientState.DM
                        setClientState(client, clientState.DM)
                elif (message.decode('ascii') == "EX"):
                    publicMessage((cUsername + " has left the server.").encode('ascii'), host)
                    clientDisconnect(client)
                    break;
                elif (message.decode('ascii') == "REQ-CONF"):
                    # Never got confirmation, so resend it.
                    client.sendall("PM-CONF".encode('ascii'))
                else:
                    print("Unexpected Message: '" + message + "'. Breaking connection before getting spammed.")
                    clientDisconnect(client)
                    break
            elif (cState == clientState.PM):
                # We received the public message, now distribute it.
                publicMessage(message, client)
                # Send a confirmation, and set us back to waiting....
                client.sendall("PM-CONF ".encode('ascii'))
                cState = clientState.Waiting
                setUserState(cUsername, clientState.Waiting)
            elif (cState == clientState.DM):
                # We should get 2 messages, the user, and the message.
                recipient = getClientByUsername(message.decode('ascii'))
                if (recipient != None):
                    message = client.recv(1024)
                    if (isOnline(getClientUsername(recipient))):
                        directMessage(message.decode('ascii'), recipient, client)
                setClientState(client, clientState.Waiting)
                cState = clientState.Waiting
            else:
                print("System Error.... Unknown state.")
       except:
            print("Handle Error...")
            clientDisconnect(client)
            break

def publicMessage(message, sender):
    if (sender == host):
        messageUser = 'Server'
    else:
        curClient = getClientData(sender)
        messageUser = curClient[1]

    messageout = messageUser + ": " + message.decode('ascii')
    for client in clientList:
        if (client[2] != clientState.EX):
            client[0].sendall(messageout.encode('ascii'))

def directMessage(message, receiver, sender):
    # print(getClientUsername(sender) + "Sent a direct message to " + getClientUsername(receiver))
    outgoing = "DM (" + getClientUsername(sender) + "): " +  message;
    receiver.sendall(outgoing.encode('ascii'))

def clientDisconnect(client):
    if (getClientState(client) != clientState.EX):
        setUserState(getClientUsername(client), clientState.EX)
        client.close()

def receiveMessage():
    global receiveThread
    
    while True:
        client, address = server.accept()

        client.sendall('USERNAME'.encode('ascii'))
        username = client.recv(1024).decode('ascii')

        receiveThread = threading.Thread(target=handle, args=(client,username, ))
        receiveThread.start()

try:
    port = int(sys.argv[1])
except:
    port = 56017

readUserFile()
    
hostname = socket.gethostname()
host = socket.gethostbyname(hostname)
print("IP Address is " + host + ":" + str(port))

server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
server.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
server.bind((host,port))
server.listen()
print("Server is listening...")

receiveMessage()
receiveThread.join()
userlist.close()
