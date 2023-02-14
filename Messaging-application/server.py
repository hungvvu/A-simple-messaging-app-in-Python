#!/usr/bin/python# This is server.py file
import socket
import time
import select
import pickle

import constants

MESSAGE_SCAN_DELAY = 0.1

# Functions
def send_file(s: socket, c: socket, filedir: str):
  # read a photo from a file as binary
    f = open(filedir, 'rb')
    l = f.read(1024)
    # send the photo
    while (l):
        c.send(l)
        l = f.read(1024)
    f.close()
    # c.send('done'.encode())
    
    # conf = ''
    # # wait for confirmation from the client
    # while conf == '':
    #     conf = c.recv(20).decode()
    # print("here")
    # # print out confirmation
    # print("Text from client: " + conf)

def receive_txt(client_socket):
    try:
        header = client_socket.recv(constants.HEADER_SIZE)

        if not len(header):
            return False
        
        message_length = int(header.decode().strip())

        return {"header": header, "data": client_socket.recv(message_length)}
    except:
        return False

class Server():
    def __init__(self, IP, PORT):
        self.server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.server.bind((IP, PORT)) # bind the port

        self.sockets_list = [self.server]

        self.client_info = {}
        self.conversations = {}



    def run(self):
        self.server.listen(5) #  wait for client connection.


        while True:
            read_sockets, _, exception_sockets = select.select(self.sockets_list, [], self.sockets_list)

            # iterate over the sockets that have something for us to read
            for s in read_sockets:

                # if we see the server socket, it means there is no new message to read and we should wait and accept incoming connections
                if s == self.server:
                    client, client_addr = self.server.accept()

                    user = receive_txt(client)
                    if user is False:
                        # do something
                        continue

                
                    self.sockets_list.append(client)

                    self.client_info[client] = user

                    print("New connection from {}:{}, username: {}".format(*client_addr, user['data'].decode('utf-8')))
                    

                # if s is a socket other than the server, we have gotten a new message to read
                else:
                    user = self.client_info[s]

                    # first, get the message type
                    msg_type = s.recv(1).decode('utf-8')

                    
                    # handle the given message type accordingly
                    if msg_type == str(constants.MsgType.TEXT.value): # a normal text message
                        # second, get the user info
                        target_info = receive_txt(s)

                        # get the timestamp of the message, since the format is always HH:MM, we can safely assume that it is always 5 bytes
                        timestamp = s.recv(5)

                        # next, parse out the message
                        message = receive_txt(s)

                        # if there is no message, close the connection
                        if message is False:
                            print('Closed connection from: {}'.format(self.client_info[s]['data'].decode('utf-8')))
                            self.sockets_list.remove(s)
                            del self.client_info[s]


                        else:
                            # if the username does not exist, send back an error message to the client
                            if target_info not in self.client_info.values():
                                error_msg = "Error: username not found".encode()
                                error_header = f"{len(error_msg):<{constants.HEADER_SIZE}}".encode()
                                s.send(str(constants.MsgType.ERROR.value).encode('utf-8') + user['header'] + user['data'] + timestamp + error_header + error_msg)
                            
                            
                            else:
                                # extract the socket from the username
                                key_list = list(self.client_info.keys())
                                val_list = list(self.client_info.values())
                                
                                pos = val_list.index(target_info)

                                target_socket = key_list[pos]

                                # send the message to the target client(s)
                                target_socket.send(str(msg_type).encode('utf-8') + user['header'] + user['data'] + timestamp + message['header'] + message['data'])

                                print(f'{timestamp.decode("utf-8")}, received message from {user["data"].decode("utf-8")}: {message["data"].decode("utf-8")}')


                    elif msg_type == str(constants.MsgType.TASK.value): # a task to be executed
                        # get the task type
                        task_type = s.recv(1).decode()

                        if task_type == str(constants.TaskType.ADD_CONVO.value): # add a new conversation to the database
                            # get the conversation name
                            convo_name = receive_txt(s)

                            # receive the header to get the length of the data
                            set_header = s.recv(constants.HEADER_SIZE)
                            username_set_len = int.from_bytes(set_header, byteorder='big')

                            # receive the data
                            username_set = b''
                            while len(username_set) < username_set_len:
                                chunk = s.recv(constants.BUFFER_SIZE)
                                if chunk == b'':
                                    raise RuntimeError("socket connection broken")
                                username_set += chunk

                            username_set = pickle.loads(username_set)

                            self.conversations[convo_name['data']] = username_set
                            self.conversations[convo_name['data']]





                    # handle exception sockets
                    for es in exception_sockets:
                        
                        # Remove from list for socket.socket()
                        self.sockets_list.remove(es)

                        # Remove from our list of users
                        del self.client_info[es]
            
            time.sleep(MESSAGE_SCAN_DELAY)

# start the server
server = Server(constants.IP, constants.PORT)
server.run()