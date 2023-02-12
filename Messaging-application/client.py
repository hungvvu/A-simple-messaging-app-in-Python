#!/usr/bin/python# This is client.py file
import socket
import time
import datetime
import sys
import errno
from PyQt5.QtCore import pyqtSignal, pyqtSlot, QObject

import constants

MESSAGE_SCAN_DELAY = 0.3 # delay between each scan for new messages, in seconds


# Functions

class Client(QObject):
    def __init__(self, IP, PORT, my_username):
        super().__init__()
        self.IP = IP
        self.PORT = PORT
        self.my_username = my_username
        self.client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.client.connect((self.IP, self.PORT))
        self.client.setblocking(False)

        # create the username for this client and send it to the server
        username = self.my_username.encode()
        username_header = f"{len(username):<{constants.HEADER_SIZE}}".encode()
        self.client.send(username_header + username)

        # dictionary of added conversations, with the conversation name as keys and lists of coresponding username as values
        self.conversations = {}

    # signals for handling message receiving
    text_message_received = pyqtSignal(str)

    def add_convo(self, convo_name, username_set):
        self.conversations[convo_name] = username_set

    def recv_file(self, filedir: str):
        f = open(filedir,'wb') #open in binary
        l = self.client.recv(1024)

        while (l):
            f.write(l)
            l = self.client.recv(1024)
        f.close

        self.client.send('Nice potato.'.encode())


    def send_txt_to(self, target_username, txt):
        # first, send the message type
        a = str(constants.MsgType.TEXT)
        self.client.send(str(constants.MsgType.TEXT.value).encode('utf-8'))

        # second, send the username to the server
        username = target_username.encode()
        username_header = f"{len(username):<{constants.HEADER_SIZE}}".encode()
        self.client.send(username_header + username)

        # next, send the timestamp of the message
        # make a timestamp from the current time
        timestamp = datetime.datetime.now().strftime("%H:%M")
        self.client.send(timestamp.encode('utf-8')) # send the timestamp to the server, since the format is always HH:MM, we can safely assume that it is always 5 bytes

        # finally, send the message to the server
        message = txt.encode('utf-8')
        message_header = f"{len(message):<{constants.HEADER_SIZE}}".encode('utf-8')
        self.client.send(message_header + message)

    @pyqtSlot()
    def run(self):
        while True:
            try:
                # loop over the new messages and print them
                while True:
                    # get the message type
                    msg_type = self.client.recv(1).decode('utf-8')

                    # receive the sender's username
                    sender_uname_header = self.client.recv(constants.HEADER_SIZE)

                    # no data
                    if not len(sender_uname_header):
                        print('Connection closed by the server')
                        sys.exit()


                    # handle the message type accordingly
                    if msg_type == str(constants.MsgType.TEXT.value):
                        # get the sender's username
                        username_length = int(sender_uname_header.decode('utf-8').strip())

                        username = self.client.recv(username_length).decode('utf-8')

                        # get the timestamp of the message, since the format is always HH:MM, we can safely assume that it is always 5 bytes
                        timestamp = self.client.recv(5).decode('utf-8')

                        # parse the received message
                        message_header = self.client.recv(constants.HEADER_SIZE)
                        message_length = int(message_header.decode('utf-8').strip())
                        message = self.client.recv(message_length).decode('utf-8')

                        # emit a message receive signal
                        self.text_message_received.emit(f"[{timestamp}, {username}] > {message}")

                    elif msg_type == str(constants.MsgType.ERROR.value):
                        # get the sender's username
                        username_length = int(sender_uname_header.decode('utf-8').strip())

                        username = self.client.recv(username_length).decode('utf-8')

                        # get the timestamp of the message, since the format is always HH:MM, we can safely assume that it is always 5 bytes
                        timestamp = self.client.recv(5).decode('utf-8')

                        # parse the received message
                        message_header = self.client.recv(constants.HEADER_SIZE)
                        message_length = int(message_header.decode('utf-8').strip())
                        message = self.client.recv(message_length).decode('utf-8')

                        # emit a message receive signal that contain the error message
                        self.text_message_received.emit(f"{message}")



                    
                    
                    



            # handle exceptions
            except IOError as e:
                # ignore the EAGAIN and EWOULDBLOCK because they are expected behaviors, catch the other exceptions
                if e.errno != errno.EAGAIN and e.errno != errno.EWOULDBLOCK:
                    print('Read error: {}'.format(str(e)))
                    sys.exit()

                # We just did not receive anything
                # sleep for a few milliseconds before starting the next scan for new message
                time.sleep(MESSAGE_SCAN_DELAY)
                continue

            except Exception as e:
                print('Exception: '.format(str(e)))
                sys.exit()
        

# client = Client(IP, PORT, my_username)
# client.run()