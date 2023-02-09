#!/usr/bin/python# This is server.py file
import socket
import time

HEADER_SIZE = 10 # the length of the message header
BUFFER_SIZE = 10


s = socket.socket()
host = socket.gethostname() # get local machine name
port = 12345 # reserve a port for this server
s.bind((host, port)) # bind the port

s.listen(5) #  wait for client connection.
new_msg = False # the server right now temporarily not able to receive message

###################################################
# REMINDER: FIND A WAY TO FIX THIS PROBLEM 
################################################### 

full_msg = ''
while True:
    c, addr = s.accept() # establish connection with client.
    print('Got connection from', addr)

    message_completed = True # the server right now temporarily not able to receive message
    # while not message_completed:
        # msg = c.recv(BUFFER_SIZE).decode()
        
        # # get the message length from the header
        # if new_msg:
        #     mLen = int(msg[:HEADER_SIZE])
        #     new_msg = False

        # full_msg += msg # append the buffered part to the full msg

        # if (len(full_msg)-HEADER_SIZE == mLen): # if we got the full message already
        # print("Text from client: " + full_msg[HEADER_SIZE:])
    # read a photo from a file as binary
    with open('resources/potato.jpg', 'rb') as f:
        data = f.read()
        c.sendfile(f)
        f.close

    # # send the photo to the client
    # msg = str(data.decode('utf-8'))
    # msg = f'{len(msg):<{HEADER_SIZE}}' + msg # append the header to the message (currently contain only msg length)
    # c.send(bytes(msg, 'utf-8'))
        
    
    # time.sleep(3*len(msg)) # to avoid closing the connection immediately and allow the transmitting to finish
    # c.close() # close the connection