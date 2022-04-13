#!/usr/bin/python3
###############################
# Michael Olson jz6081ak      #
# Choua Vang                  #
# ICS 460-51                  #
# Server for the chat program #
###############################
import socket
import threading
import requests
import enum
import sys
import time

# Enumeration for the clients states
class clientState(enum.Enum):
    Waiting = 0 # online
    PM = 1 # Working on a PM
    DM = 2 # Working on a DM
    EX = 3 # offline

# clientList of  clientData ['socket client info' 'username' 'client state']
# Note - passwords are not stored on the server itself, they are on a file
clientList = []
# To make it so we can close the thread later.
receiveThread = None

# Checks to see if the user is in the list
def isInClientList(username):
    for n in range(0,  len(clientList)):
        if (clientList[n][1] == username):
            return True
    return False

# checks to see if the user is online
def isOnline(username):
    for n in range(0,  len(clientList)):
        if (clientList[n][1] == username):
            if clientList[n][2] == clientState.EX:
                return False
    return True

# sets the state of the user
def setUserState(username, state):
    for n in range(0,  len(clientList)):
        if (clientList[n][1] == username):
            clientList[n][2] = state

# gets the client data
def getClientData(client):
    for i in range(0,  len(clientList)):
        if (clientList[i][0] == client):
            return clientList[i]
    return None

# updates the socket info for the user
def updateUser(username, data):
    for i in range(0,  len(clientList)):
        if (clientList[i][1] == username):
            clientList[i][0] = data

# gets the state of the client
def getClientState(client):
    clientData = getClientData(client)
    if (clientData != None):
        return clientData[2]

# Gets the username of the client
def getClientUsername(client):
    clientData = getClientData(client)
    if (clientData != None):
        return clientData[1]
    else:
        return "Server"

# Gets a client by the username
def getClientByUsername(username):
    for i in range(0, len(clientList)):
        if (clientList[i][1] == username):
            return clientList[i][0]
    return None

# Gets a list of all members that are online
def getOnlineList():
    online = []
    for i in range(0,  len(clientList)):
        if (clientList[i][2] != clientState.EX):
            online.append(clientList[i][1])
    return online

# Reads in the list of users from file
def readUserFile():
    global clientList
    try:
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
    except:
        print('No user file found.')

# Reads the users password from the file
def readUserPassword(user):
    try:
        userfile = open('users.dat', 'r+')
        currec = userfile.readline()
        while currec != '':
            record = currec.split("%")
            if record[0] == user:
                return record[1]
            print(currec)
            currec = userfile.readline()
        userfile.close()
    except:
        print('Error reading file')

# Saves a new user's data to the user file.
def saveUserData(user, password):
    try:
        userfile = open('users.dat', 'a+')
        stringToWrite = user + "%" + password + "%\n"
        userfile.write(stringToWrite)
    except:
        print('Error writing file')

# handles a single client.
def handle(client, username):
    if (isInClientList(username)):
        if (isOnline(username)):
            client.sendall("CLOSENOW".encode('ascii'))
            return
        else:
            passAttempts = 0
            successful = False
            updateUser(username, client)
            directMessage("Welcome back!", client, server)
            readPassword = readUserPassword(username)
            while (passAttempts < 3 and not successful):
                time.sleep(0.05)
                client.sendall('PASSWORD'.encode('ascii'))
                password = client.recv(1024).decode('ascii')
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
                        setUserState(cUsername, clientState.DM)
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
                # The transaction was cancelled.
                if (message.decode('ascii') == "CANCEL"):
                    cState = clientState.Waiting
                # We should get 2 messages, the user, and the message.
                recipient = getClientByUsername(message.decode('ascii'))
                if (recipient != None):
                    message = client.recv(1024)
                    if (isOnline(getClientUsername(recipient))):
                        directMessage(message.decode('ascii'), recipient, client)
                setUserState(cUsername, clientState.Waiting)
                cState = clientState.Waiting
            else:
                print("System Error.... Unknown state.")
       except:
            print("Handle Error...")
            clientDisconnect(client)
            break

# broadcasts a public message
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

# broadcasts a direct message
def directMessage(message, receiver, sender):
    # print(getClientUsername(sender) + "Sent a direct message to " + getClientUsername(receiver))
    outgoing = "DM (" + getClientUsername(sender) + "): " +  message;
    receiver.sendall(outgoing.encode('ascii'))

# sets a client's status to disconnected and attempts to close it.
def clientDisconnect(client):
    if (getClientState(client) != clientState.EX):
        setUserState(getClientUsername(client), clientState.EX)
        client.close()

# Receives new messages from new clients.
def receiveMessage():
    global receiveThread

    try:
        while True:
            client, address = server.accept()
            
            client.sendall('USERNAME'.encode('ascii'))
            username = client.recv(1024).decode('ascii')
            
            receiveThread = threading.Thread(target=handle, args=(client,username, ))
            receiveThread.start()
    except:
        print("Server Error")

# main entry point of program
# Checks to see if we put a port at the command line.
try:
    port = int(sys.argv[1])
except:
    # a port was not entered, print out usage, and quit
    print("Invalid port")
    print("Usage: ")
    print("$ " + sys.argv[0] + " <PORT>")
    exit(1)

# read in the user file.
readUserFile()

# attempt to setup the server.
try:
    hostname = socket.gethostname()
    host = socket.gethostbyname(hostname)
    server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    server.bind((host,port))
except:
    print("Error creating server")
    exit(1)

# Have the server listen
server.listen()
print("Server is listening...")

# receive a message from a new client.
receiveMessage()

# we are quitting, wait for the thread to quit.
if (receiveThread != None):
    receiveThread.join()

