#!/usr/bin/python3

import socket
import threading

username = ''
password = ''

def receive():
    while True:
        try:
            message = client.recv(1024).decode('ascii')
            if message == 'USERNAME':
                client.send(username.encode('ascii'))
            else:
                print(message)
        except:
            print("System error")
            client.close()
            break

def write():
    while True:
        message = '{}: {}'.format(username, input(''))
        client.send(message.encode('ascii'))


username = input("Enter Username: ")
password = input("Enter Password: ")

hostname = socket.gethostname()
host = socket.gethostbyname(hostname)
port = 56017

client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
client.connect((host, port))

receiving = threading.Thread(target=receive)
receiving.start()

writing = threading.Thread(target=write)
writing.start()

                
