#!/usr/bin/python3

import socket
import threading

username = ''
password = ''
iAmRunning = True

def getFromServer():
    global iAmRunning
    while iAmRunning:
        try:
            message = client.recv(1024).decode('ascii')
            if message == 'USERNAME':
                client.send(username.encode('ascii'))
            elif message == 'PASSWORD':
                client.send(password.encode('ascii'))
            else:
                print(message)
        except:
            print("System error")
            client.close()
            break

def sendToServer():
   global iAmRunning
   while iAmRunning:
        message = input()
        if (message == "PM"):
            print("private Message")
            client.send(message.encode('ascii'))
        elif (message == "DM"):
            print("direct Message")
            client.send(message.encode('ascii'))
        elif (message =="EX"):
            print("Exiting...")
            client.send(message.encode('ascii'))
            iAmRunning = False
        else:
            print(' Client - message ' + message)
            client.send(message.encode('ascii'))


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

                
