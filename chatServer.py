#!/usr/bin/python3

import socket
import threading
import requests

clients = []
usernames = []

def handle(client):
    while True:
        try:
            message = client.recv(1024)
            publicMessage(message, client)
        except:
            clientDisconnect(client)
            break;

def publicMessage(message, client):
    if (client == host):
        messageUser = 'Server'
    else:
        index = clients.index(client)
        messageUser = usernames[index]
    
    for client in clients:
        client.send(message)

def directMessage(user, client):
    print("Send a direct message to " + user)

def clientDisconnect(client):
    print("Client is disconnecting: " + str(client))
    index = clients.index(client)
    clients.remove(client)
    client.close()
    username = username[index]
    publicMessage('{} left!'.format(username).encode('ascii'), host)
    username.remove(username)

def receiveMessage():
    while True:
        client, address = server.accept()
        print("Connected with {}".format(str(address)))

        client.send('USERNAME'.encode('ascii'))
        username = client.recv(1024).decode('ascii')
        usernames.append(username)
        clients.append(client)

        print('Username is {}'.format(username))
        publicMessage('{} joined!'.format(username).encode('ascii'), host)
        client.send('Connected to server!'.encode('ascii'))
        
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

