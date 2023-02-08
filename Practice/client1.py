#!/usr/bin/python# This is client.py file
import socket
s = socket.socket()
host = socket.gethostname() # get the server host name
port = 12345 # the port of the server

s.connect((host, port)) # connect to the server

# send a test text to the server
test_str = "Hello, is there anybody in here?"
s.send(test_str.encode())

print("Text from server: " + s.recv(1024).decode()) # print the message recieved from the server


s.close() # close the connection