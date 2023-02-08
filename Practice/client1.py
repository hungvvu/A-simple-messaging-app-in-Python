#!/usr/bin/python# This is client.py file
import socket
s = socket.socket()
host = socket.gethostname() # get the server host name
port = 12345 # the port of the server

s.connect((host, port)) # connect to the server
print(s.recv(1024).decode()) # print the message recieved from the server
s.close() # close the connection