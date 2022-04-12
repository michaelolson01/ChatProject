#!/usr/bin/python3

import socket
import threading
import requests

clients = []
usernames = []
password = []
userfile = None

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

def getUsername(client):
    returnval = ''
    
    try:
        index = clients.index(client)
        returnval =  usernames[index]
    except:
        returnval = "Server"
        
    return returnval

def handle(client):
    while True:
        try:
            message = client.recv(1024)
            if (message.decode('ascii') == "PM"):
                print("Public Message from " + getUsername(client))
            elif (message.decode('ascii') == "DM"):
                print("Direct Message from " + getUsername(client))
            elif (message.decode('ascii') == "EX"):
                print(getUsername(client) + " is leaving...")
                clientDisconnect(client)
                break;
            else:
                publicMessage(message, client)
                
        except:
            print("Handle Error...")
            if (client in clients):
                clientDisconnect(client)
            break;

def publicMessage(message, sender):
    if (sender == host):
        messageUser = 'Server'
    else:
        index = clients.index(sender)
        messageUser = usernames[index]

    messageout = getUsername(sender) + ":" + message.decode('ascii')
    for client in clients:
        client.send(messageout.encode('ascii'))

def directMessage(message, receiver, sender):
    index = clients.index(receiver)
    messageUser = usernames[index]
    print("Send a direct message to " + messageUser)
    
    receiver.send(message.encode('ascii'))

def clientDisconnect(client):
    print("Client is disconnecting: " + str(client))
    index = clients.index(client)
    clients.remove(client)
    client.close()
    username = usernames[index]
    publicMessage('{} left!'.format(username).encode('ascii'), host)
    usernames.remove(username)

def receiveMessage():
    while True:
        client, address = server.accept()
        print("Connected with {}".format(str(address)))

        client.send('USERNAME'.encode('ascii'))
        username = client.recv(1024).decode('ascii')
        client.send('PASSWORD'.encode('ascii'))
        password = client.recv(1024).decode('ascii')
        try:
            # See if the client is already in the list.
            index = clients.index(client)
            directMessage("Welcome back!", client, server)
        except:
            usernames.append(username)
            clients.append(client)
            directMessage("Welcome to the server!", client, server)

        print('Username is {}'.format(username))
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
