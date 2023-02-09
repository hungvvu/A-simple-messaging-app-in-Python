#!/usr/bin/python# This is client.py file
import socket
import time
import sys
import errno

BUFFER_SIZE = 10
HEADER_SIZE = 10

# Functions
def recv_file(s: socket, filedir: str):
    f = open(filedir,'wb') #open in binary
    l = s.recv(1024)

    while (l):
        f.write(l)
        l = s.recv(1024)
    f.close

    s.send('Nice potato.'.encode())



IP = "127.0.0.1"
PORT = 12345
my_username = input("Username: ")


client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

client.connect((IP, PORT))

# Set connection to non-blocking
client.setblocking(False)

# create the username for this client and send it to the server
username = my_username.encode()
username_header = f"{len(username):<{HEADER_SIZE}}".encode()
client.send(username_header + username)


while True:

    # message input from the user
    message = input(f'{my_username} > ')

    # check if the message is empty, send it if it is not
    if message:

        message = message.encode('utf-8')
        message_header = f"{len(message):<{HEADER_SIZE}}".encode('utf-8')
        client.send(message_header + message)

    try:
        # loop over the new messages and print them
        while True:

            # receive the sender's username
            sender_uname_header = client.recv(HEADER_SIZE)

            # no data
            if not len(username_header):
                print('Connection closed by the server')
                sys.exit()

            username_length = int(username_header.decode('utf-8').strip())

            username = client.recv(username_length).decode('utf-8')

            # parse the received message
            message_header = client.recv(HEADER_SIZE)
            message_length = int(message_header.decode('utf-8').strip())
            message = client.recv(message_length).decode('utf-8')

            # print message
            print(f'{username} > {message}')


    # handle exceptions
    except IOError as e:
        # ignore the EAGAIN and EWOULDBLOCK because they are expected behaviours, catch the other exceptions
        if e.errno != errno.EAGAIN and e.errno != errno.EWOULDBLOCK:
            print('Read error: {}'.format(str(e)))
            sys.exit()

        # We just did not receive anything
        continue

    except Exception as e:
        print('Exception: '.format(str(e)))
        sys.exit()


'''
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

stop = False
while not stop:
    # msg = s.recv(20500)

    recv_file(s, 'received.jpeg')
    s.close()

    stop = True

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
'''