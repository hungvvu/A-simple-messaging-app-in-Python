#!/usr/bin/python# This is server.py file
import socket
import time
import select
import pickle

import constants

MESSAGE_SCAN_DELAY = 0.1

## helper functions ##

# return a encoded header that contain the length of given encoded string
def getLenHeader(encodedString):
    return f"{len(encodedString):<{constants.HEADER_SIZE}}".encode()

# wrapper for a user info, include the username and the header for that username
class UserInfo():
    def __init__(self, header, data):
        self.header = header
        self.data = data

    def isEqualTo(self, thatUserInfo):
        if self.data == thatUserInfo.data:
            return True
        return False

    # def get_header(self):
    #     return self.header

    # def get_uname

class Server():
    def __init__(self, IP, PORT):
        self.server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.server.bind((IP, PORT)) # bind the port

        self.sockets_list = [self.server]

        self.client_info = {}
        self.conversations = {}
        self.group_owners = {}

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

    # receive a text message from the client (with header + content) and parse it
    def receive_txt(self, client_socket):
        try:
            header = client_socket.recv(constants.HEADER_SIZE)

            if not len(header):
                return False
            
            message_length = int(header.decode().strip())

            return {"header": header, "data": client_socket.recv(message_length)}
        except:
            return False

    def user_exist(self, user_info):
        for u in self.client_info.values():
            if user_info.data == u.data:
                return True
        
        return False

    # get the socket by the user info
    def get_sock_by_uinfo(self, user_info):
        # # if the username does not exist, return false
        # if not self.user_exist(user_info):
        #     return False
        
        
        # else:
        # extract the socket from the username
        key_list = list(self.client_info.keys())
        val_list = list(self.client_info.values())
        
        pos = 0
        for v in val_list:
            if (user_info.data == v.data):
                return key_list[pos]
            pos += 1

        return False

    def run(self):
        self.server.listen(5) #  wait for client connection.


        while True:
            read_sockets, _, exception_sockets = select.select(self.sockets_list, [], self.sockets_list)

            # iterate over the sockets that have something for us to read
            for s in read_sockets:

                # if we see the server socket, it means there is no new message to read and we should wait and accept incoming connections
                if s == self.server:
                    client, client_addr = self.server.accept()

                    user = self.receive_txt(client)
                    if user is False:
                        # do something
                        continue

                
                    self.sockets_list.append(client)

                    self.client_info[client] = UserInfo(user['header'], user['data'])

                    print("New connection from {}:{}, username: {}".format(*client_addr, user['data'].decode('utf-8')))
                    

                # if s is a socket other than the server, we have gotten a new message to read
                else:
                    user = self.client_info[s]

                    # first, get the message type
                    msg_type = s.recv(1).decode('utf-8')

                    
                    # handle the given message type accordingly
                    if msg_type == str(constants.MsgType.TEXT.value): # a normal text message
                        # second, get the user info
                        target_info = self.receive_txt(s)

                        # get the timestamp of the message, since the format is always HH:MM, we can safely assume that it is always 5 bytes
                        timestamp = s.recv(5)

                        # next, parse out the message
                        message = self.receive_txt(s)

                        # if there is no message, close the connection
                        if message is False:
                            print('Closed connection from: {}'.format(self.client_info[s].data.decode('utf-8')))
                            self.sockets_list.remove(s)
                            del self.client_info[s]


                        else:
                            # if there is only two person in the conversation, it is a direct message
                            if len(self.conversations[target_info['data']]) <= 2:
                                # get the user socket
                                target_socket = self.get_sock_by_uinfo(self.conversations[target_info['data']][0])

                                # if the username does not exist, send back an error message to the client
                                if not target_socket:
                                    error_msg = f"Error: \"{target_info['data'].decode('utf-8')}\" username not found".encode()
                                    error_header = f"{len(error_msg):<{constants.HEADER_SIZE}}".encode()
                                    s.send(str(constants.MsgType.ERROR.value).encode('utf-8') + user.header + user.data + timestamp + error_header + error_msg)
                            
                            
                                else:
                                    # send the message to the target client(s)
                                    target_socket.send(str(msg_type).encode('utf-8') + user.header + user.data + timestamp + message['header'] + message['data'])

                                    print(f'{timestamp.decode("utf-8")}, received message from {user.data.decode("utf-8")}: {message["data"].decode("utf-8")}')

                            # else it is a group message
                            else:
                                group_name = target_info["data"].decode("utf-8")

                                # append the group name to the sender's username to distinguish from normal messages
                                appended_username = (group_name + '/' + user.data.decode('utf-8')).encode('utf-8')
                                appended_user_header = getLenHeader(appended_username)

                                print(f'[INFO] {timestamp.decode("utf-8")}, received message from {user.data.decode("utf-8")} ' \
                                    + f'to group {group_name}: {message["data"].decode("utf-8")}')
                                    
                                
                                # loop through all the user in the conversation
                                for u in self.conversations[target_info['data']]:
                                    
                                    if not u.isEqualTo(user):
                                        # get the user socket
                                        target_socket = self.get_sock_by_uinfo(u)

                                        # if the username does not exist, send back an error message to the client
                                        if not target_socket:
                                            error_msg = f"Error: \"{u.data.decode('utf-8')}\" username not found".encode()
                                            error_header = f"{len(error_msg):<{constants.HEADER_SIZE}}".encode()
                                            s.send(str(constants.MsgType.ERROR.value).encode('utf-8') + user.header + user.data + timestamp + error_header + error_msg)
                                    
                                    
                                        else:
                                            # send the message to the target client(s)
                                            target_socket.send(str(msg_type).encode('utf-8') + appended_user_header + appended_username + timestamp + message['header'] + message['data'])


                    elif msg_type == str(constants.MsgType.TASK.value): # a task to be executed
                        # get the task type
                        task_type = s.recv(1).decode()

                        if task_type == str(constants.TaskType.ADD_CONVO.value): # add a new conversation to the database
                            # get the conversation name
                            convo_name = self.receive_txt(s)

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

                            # calculate username header for the usernames in the set and save it into conversation dictionary for later use
                            conversation_info = []
                            for username in username_set:
                                username_encoded = username.encode()
                                username_header = f"{len(username):<{constants.HEADER_SIZE}}".encode()

                                conversation_info.append(UserInfo(username_header, username_encoded))
                            

                            # add the sender into the conversation
                            # conversation_info.add(UserInfo(user.header, user.data))

                            # save the conversation to the database
                            self.conversations[convo_name['data']] = conversation_info

                            if (len(conversation_info) != 1): # if this is a group chat (more than 2 people), add the person who created the group as a group owner
                                self.group_owners[convo_name['data']] = user





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