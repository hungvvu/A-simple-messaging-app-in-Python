#!/usr/bin/python# This is client.py file
import socket
import time
import datetime
import sys
import os
import errno
import pickle
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
        self.server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.server.connect((self.IP, self.PORT))
        self.server.setblocking(False)

        # create the username for this client and send it to the server
        username = self.my_username.encode()
        username_header = f"{len(username):<{constants.HEADER_SIZE}}".encode()
        self.server.send(username_header + username)

        # dictionary of added conversations, with the conversation name as keys and lists of coresponding username as values
        self.conversations = {}

        # store all conversations and a list of user who have read this user's newest message
        self.msg_read = {}

        self.halt = False # variable to halt client execution

    # signals for handling message receiving
    text_message_received = pyqtSignal(str)
    rename_task_received = pyqtSignal(str, str)
    file_message_received = pyqtSignal(str, str, int)

    # take in a raw text string and send that to the server, encoded and with a header prepended
    def send_txt_to_server(self, text):
        header = f"{len(text):<{constants.HEADER_SIZE}}".encode('utf-8')
        self.server.send(header + text.encode('utf-8'))

    def send_readReceipt(self, convo_name, original_sender):
        # tell the server that a read receipt will be send next
        self.server.send(str(constants.MsgType.READ_RECEIPT.value).encode('utf-8'))

        # send the convo name that this receipt apply to
        # username_header = f"{len(convo_name):<{constants.HEADER_SIZE}}".encode('utf-8')
        # self.server.send(username_header + convo_name.encode('utf-8'))
        self.send_txt_to_server(convo_name)

        # send the original_sender
        # sender_header = f"{len(original_sender):<{constants.HEADER_SIZE}}".encode('utf-8')
        # self.server.send(sender_header + original_sender.encode('utf-8'))
        self.send_txt_to_server(original_sender)

    # add a new conversation
    def add_convo(self, convo_name, username_set):
        self.conversations[convo_name] = username_set

        # inform the server that a task will be sent next
        self.server.send(str(constants.MsgType.TASK.value).encode('utf-8'))

        # ask the server to add this new conversation to the database
        t = constants.TaskType.ADD_CONVO.value
        self.server.send(str(constants.TaskType.ADD_CONVO.value).encode('utf-8'))

        # send the convo name to the server
        username_header = f"{len(convo_name):<{constants.HEADER_SIZE}}".encode('utf-8')
        self.server.send(username_header + convo_name.encode('utf-8'))

        # serialize the data
        data_serialized = pickle.dumps(username_set)

        # send the length of the data first
        header = len(data_serialized).to_bytes(constants.HEADER_SIZE, byteorder='big')
        self.server.send(header)

        # send the username set
        self.server.sendall(data_serialized)

    def rename_convo(self, old_name, new_name):
        # rename the conversation on the local dictionary
        self.conversations[new_name] = self.conversations.pop(old_name)        

        # inform the server that a task will be sent next
        self.server.send(str(constants.MsgType.TASK.value).encode('utf-8'))

        # ask the server to rename this conversation to a new name
        self.server.send(str(constants.TaskType.RENAME_CONVO.value).encode('utf-8'))

        # send the current convo name to the server
        username_header = f"{len(old_name):<{constants.HEADER_SIZE}}".encode('utf-8')
        self.server.send(username_header + old_name.encode('utf-8'))

        # send the new convo name to the server
        new_header = f"{len(new_name):<{constants.HEADER_SIZE}}".encode('utf-8')
        self.server.send(new_header + new_name.encode('utf-8'))

    def add_new_member(self, convo_name, member_uname):
        # add the member if they are not in the conversation yet
        if member_uname not in self.conversations[convo_name]:
            # add member to the local dictionary
            self.conversations[convo_name].add(member_uname)

            # inform the server that a task will be sent next
            self.server.send(str(constants.MsgType.TASK.value).encode('utf-8'))

            # ask the server to add this new member
            self.server.send(str(constants.TaskType.ADD_MEMBER.value).encode('utf-8'))

            # send the conversation name to the server
            self.send_txt_to_server(convo_name)

            # send the member name to the server
            self.send_txt_to_server(member_uname)
            
            # print the status to the screen
            self.text_message_received.emit(f"[INFO] Member {member_uname} added to {convo_name}")
        
        else:
            self.text_message_received.emit(f"[ERROR] Member {member_uname} is already in the group")

    def remv_member(self, convo_name, member_uname):
        # remove the member if they are in the conversation
        if member_uname in self.conversations[convo_name]:
            # add member to the local dictionary
            self.conversations[convo_name].remove(member_uname)

            # inform the server that a task will be sent next
            self.server.send(str(constants.MsgType.TASK.value).encode('utf-8'))

            # ask the server to remove this member
            self.server.send(str(constants.TaskType.REMV_MEMBER.value).encode('utf-8'))

            # send the conversation name to the server
            self.send_txt_to_server(convo_name)

            # send the member name to the server
            self.send_txt_to_server(member_uname)
            
            # print the status to the screen
            self.text_message_received.emit(f"[INFO] Member {member_uname} removed from {convo_name}")
        
        else:
            self.text_message_received.emit(f"[ERROR] Member {member_uname} is not in the group")

    def view_member_list(self, convo_name):
        # make the member list string
        memL_str = ''
        for mem in self.conversations[convo_name]:
            memL_str = memL_str + mem + '; '
        
        # remove the last '; ' character
        memL_str = memL_str[:-2]
        # print the members to the screen
        self.text_message_received.emit(f"[INFO] Member list: {memL_str}")

    def check_readStatus(self, convo_name):
        read_members = ''
        
        if convo_name not in self.msg_read.keys():
            self.text_message_received.emit("[INFO] You have not texted this person yet")
            return
        # loop through the member who have read the message
        for mem in self.msg_read[convo_name]:
            read_members = read_members + mem + '; '

        if read_members == '':
            self.text_message_received.emit("[INFO] Your latest message has not been read")
        else:
            # remove the last '; ' character
            read_members = read_members[:-2]
            self.text_message_received.emit("[INFO] Your latest message has been read by: " + read_members)

    # receive a text message from the server (with header + content) and parse it
    def receive_txt(self, client_socket):
        try:
            header = client_socket.recv(constants.HEADER_SIZE)

            if not len(header):
                return False
            
            message_length = int(header.decode().strip())

            return {"header": header, "data": client_socket.recv(message_length)}
        except:
            return False

    def recv_file(self, accept, filedir=None, file_size=None):
        if accept:# the client accepted the file
            # Initialize a variable to keep track of the total number of bytes received
            total_received = 0
            f = open(filedir,'wb') #open in binary

            # Receive the file in small chunks
            while total_received < file_size:
                # Receive a chunk of the file
                chunk = self.server.recv(min(file_size - total_received, constants.BUFFER_SIZE))

                # Update the total number of bytes received
                total_received += len(chunk)

                # Write the received data to the file
                with open(filedir, 'ab') as f:
                    f.write(chunk)

            f.close()
            # f = open(filedir,'wb') #open in binary
            # l = self.server.recv(1024)

            # while (l):
            #     f.write(l)
            #     l = self.server.recv(1024)
            # f.close

            # self.server.send('Nice potato.'.encode())
        
        else: # the client declined the file
            # discard the file by calling receive but not write it to anywhere
            total_received = 0

            # Receive the file in small chunks
            while total_received < file_size:
                # Receive a chunk of the file
                chunk = self.server.recv(min(file_size - total_received, constants.BUFFER_SIZE))

                # Update the total number of bytes received
                total_received += len(chunk)

            # something
        return True


    def send_txt_to(self, target_username, txt):
        # first, send the message type
        self.server.send(str(constants.MsgType.TEXT.value).encode('utf-8'))

        # second, send the username to the server
        username = target_username.encode()
        username_header = f"{len(username):<{constants.HEADER_SIZE}}".encode()
        self.server.send(username_header + username)

        # next, send the timestamp of the message
        # make a timestamp from the current time
        timestamp = datetime.datetime.now().strftime("%H:%M")
        self.server.send(timestamp.encode('utf-8')) # send the timestamp to the server, since the format is always HH:MM, we can safely assume that it is always 5 bytes

        # finally, send the message to the server
        message = txt.encode('utf-8')
        message_header = f"{len(message):<{constants.HEADER_SIZE}}".encode('utf-8')
        self.server.send(message_header + message)

        # empty the message read list for this conversation because there is a new message
        self.msg_read[target_username] = []

    def send_file_to(self, target_username, file_dir):
        # Open the file to be sent
        f = open(file_dir, 'rb')
        file_name = file_dir.split("/")[-1]

        # Get the file size
        file_size = os.path.getsize(file_dir)

        # inform the server that a file will be sent next
        self.server.send(str(constants.MsgType.FILE.value).encode('utf-8'))

        # send the username to the server $here
        username = target_username.encode()
        username_header = f"{len(username):<{constants.HEADER_SIZE}}".encode()
        self.server.send(username_header + username)

        # send the file name
        self.send_txt_to_server(file_name)

        # Send the file size
        self.server.send(f"{file_size:<{constants.HEADER_SIZE}}".encode('utf-8'))#$here

        # Split the file into small chunks and send each chunk
        total_sent = 0
        while total_sent < file_size:
            chunk = f.read(min(file_size - total_sent, constants.BUFFER_SIZE))

            # Update the total number of bytes received
            total_sent += len(chunk)

            if not chunk:
                break
            self.server.send(chunk)

        # Close the file
        f.close()

    @pyqtSlot()
    def run(self):
        while True:
            try:
                # loop over the new messages and print them
                while True:
                    # get the message type
                    msg_type = self.server.recv(1).decode('utf-8')

                    # handle the message type accordingly
                    if msg_type == str(constants.MsgType.TEXT.value):
                        # receive the sender's username
                        sender_uname_header = self.server.recv(constants.HEADER_SIZE)

                        # no data
                        if not len(sender_uname_header):
                            print('Connection closed by the server')
                            sys.exit()
                        
                        # get the sender's username
                        username_length = int(sender_uname_header.decode('utf-8').strip())

                        username = self.server.recv(username_length).decode('utf-8')

                        # get the timestamp of the message, since the format is always HH:MM, we can safely assume that it is always 5 bytes
                        timestamp = self.server.recv(5).decode('utf-8')

                        # parse the received message
                        message_header = self.server.recv(constants.HEADER_SIZE)
                        message_length = int(message_header.decode('utf-8').strip())
                        message = self.server.recv(message_length).decode('utf-8')

                        # emit a message receive signal
                        self.text_message_received.emit(f"[{timestamp}, {username}] > {message}")

                        # parse the appended username into convo_name and "actual" username
                        parsed_uname = username.split('/')

                        # if the parse has more than 2 element, this was originally a message sent to a group
                        if len(parsed_uname) >= 2:
                            self.send_readReceipt(parsed_uname[0], parsed_uname[1])

                        else:# just a direct message, username == conversation name on the sender side
                            self.send_readReceipt(self.my_username, username)



                    elif msg_type == str(constants.MsgType.READ_RECEIPT.value):
                        # get the conversation this receipt apply to
                        convo_name = self.receive_txt(self.server)
                        convo_name_str = convo_name['data'].decode('utf-8')

                        # get the user who sent this receipt
                        username = self.receive_txt(self.server)
                        username_str = username['data'].decode('utf-8')

                        # add the user to the msg_read list for this conversation if they are not in the list yet
                        if username_str not in self.msg_read[convo_name_str]:

                            self.msg_read[convo_name_str].append(username_str)


                    elif msg_type == str(constants.MsgType.FILE.value):
                        #$here
                        # receive the sender's username header
                        sender_uname_header = self.server.recv(constants.HEADER_SIZE)

                        # no data
                        if not len(sender_uname_header):
                            print('Connection closed by the server')
                            sys.exit()
                        
                        # get the sender's username
                        username_length = int(sender_uname_header.decode('utf-8').strip())

                        username = self.server.recv(username_length).decode('utf-8')

                        # get the filename
                        filename = self.receive_txt(self.server)
                        filename_str = filename['data'].decode('utf-8')


                        file_size = self.server.recv(constants.HEADER_SIZE).decode('utf-8')

                        self.file_message_received.emit(username, filename_str, int(file_size))
                        self.halt = True # halt until user made decision on accepting the file or not
                        while self.halt:
                            time.sleep(MESSAGE_SCAN_DELAY)


                    elif msg_type == str(constants.MsgType.ERROR.value):
                        # receive the sender's username
                        sender_uname_header = self.server.recv(constants.HEADER_SIZE)

                        # no data
                        if not len(sender_uname_header):
                            print('Connection closed by the server')
                            sys.exit()
                        
                        # get the sender's username
                        username_length = int(sender_uname_header.decode('utf-8').strip())

                        username = self.server.recv(username_length).decode('utf-8')

                        # get the timestamp of the message, since the format is always HH:MM, we can safely assume that it is always 5 bytes
                        timestamp = self.server.recv(5).decode('utf-8')

                        # parse the received message
                        message_header = self.server.recv(constants.HEADER_SIZE)
                        message_length = int(message_header.decode('utf-8').strip())
                        message = self.server.recv(message_length).decode('utf-8')

                        # emit a message receive signal that contain the error message
                        self.text_message_received.emit(f"{message}")


                    elif msg_type == str(constants.MsgType.TASK.value):
                        # get the task type
                        task_type = self.server.recv(1).decode('utf-8')
                        
                        if task_type == str(constants.TaskType.RENAME_CONVO.value):
                            # get the old conversation name
                            old_name = self.receive_txt(self.server)
                            old_name_str = old_name['data'].decode('utf-8')

                            # get the new conversation name
                            new_name = self.receive_txt(self.server)
                            new_name_str = new_name['data'].decode('utf-8')

                            
                            # check if the member has the group on their side already or not
                            if old_name_str in self.conversations.keys():
                                # rename the conversation on the local dictionary
                                # print(f'conversation at old_name is: {old_name_str}')
                                self.conversations[new_name_str] = self.conversations.pop(old_name_str)

                                # change the UI's group name
                                self.rename_task_received.emit(old_name_str, new_name_str)
                            
                            # if the member hasn't add the conversation yet, no need to change anything

                        
                        elif task_type == str(constants.TaskType.ADD_MEMBER.value):
                            # get the conversation name
                            convo_name = self.receive_txt(self.server)
                            convo_name_str = convo_name['data'].decode('utf-8')

                            # get the new member name
                            newMem_uname = self.receive_txt(self.server)
                            newMem_uname_str = newMem_uname['data'].decode('utf-8')

                            
                            # check if the member has the groupchat on their side already or not
                            if convo_name_str in self.conversations.keys():
                                # add the member to the local dictionary
                                self.conversations[convo_name_str].add(newMem_uname_str)
                            
                            # if the member hasn't add the conversation yet, no need to change anything


                        elif task_type == str(constants.TaskType.REMV_MEMBER.value):
                            # get the conversation name
                            convo_name = self.receive_txt(self.server)
                            convo_name_str = convo_name['data'].decode('utf-8')

                            # get the member name
                            mem_uname = self.receive_txt(self.server)
                            mem_uname_str = mem_uname['data'].decode('utf-8')

                            
                            # check if the member has the groupchat on their side already or not
                            if convo_name_str in self.conversations.keys():
                                # remove the member if they are in the conversation
                                if mem_uname in self.conversations[convo_name_str]:
                                    # add the member to the local dictionary
                                    self.conversations[convo_name_str].remove(newMem_uname_str)


                            
                            # if the member hasn't add the conversation yet, no need to change anything


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
                print('Exception: {}'.format(str(e)))
                sys.exit()
        
    def close(self):
        self.server.close()


# client = Client(IP, PORT, my_username)
# client.run()