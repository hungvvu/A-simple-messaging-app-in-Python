#!/usr/bin/python# This is client.py file
import socket
import time

BUFFER_SIZE = 10
HEADER_SIZE = 10

s = socket.socket()
host = socket.gethostname() # get the server host name
port = 12345 # the port of the server

s.connect((host, port)) # connect to the server

# send a test text to the server
# test_str = "Hello, is there anybody in here?"
# test_str = f'{len(test_str):<{HEADER_SIZE}}' + test_str
# s.send(test_str.encode())

# time.sleep(3*len(test_str))


full_msg = ''
new_msg = True

while True:
    msg = s.recv(20500)

    # reminder 
    with open('received.jpeg', 'wb') as f:
        f.write(msg)

    # # get the message length from the header
    # if new_msg:
    #     mLen = int(msg[:HEADER_SIZE])
    #     new_msg = False

    # full_msg += msg # append the buffered part to the full msg
    # if (len(full_msg)-HEADER_SIZE == mLen): # if we got the full message already
    #     # print('Message from server: ' + full_msg[HEADER_SIZE:])
    #     with open('received.jpeg', 'wb') as f:
    #         f.write(bytes(full_msg,'utf-8'))
    #     new_msg = True # set the new msg flag to prepare for the next message
    #     full_msg = '' # empty the full message temporary string


    # s.close() # close the connection