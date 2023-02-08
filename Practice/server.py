#!/usr/bin/python# This is server.py file
import socket

s = socket.socket()
host = socket.gethostname() # get local machine name
port = 12345 # reserve a port for this server
s.bind((host, port)) # bind the port

s.listen(5) #  wait for client connection.
while True:
    c, addr = s.accept() # establish connection with client.
    print('Got connection from', addr)
    test_str = c.recv(1024).decode()
    if (test_str != ""):
        c.send("Yes, I'm here!".encode())
        print("Text from client: " + test_str)
    # c.send('Hello World!'.encode())
    c.close() # close the connection