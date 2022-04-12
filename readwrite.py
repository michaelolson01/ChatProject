#!/usr/bin/python3

userlist = None

def writefile():
    try:
        userlist = open('userlist.data', 'r+')
    except:
        print("Userfile does not exist, creating.")
        userlist = open('userlist.data', 'w+')
    finally:
        userlist.write("Username Password")
        userlist.close()

def readfile():
    try:
        userlist = open('userlist.data', 'r+')
        strinput = userlist.read()
        print(strinput)
    except:
        print("Userfile does not exist, creating.")
        userlist = open('userlist.data', 'w+')
    finally:
        userlist.close()

writefile()
readfile()

