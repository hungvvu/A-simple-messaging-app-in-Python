#!/usr/bin/python# This is server.py file
import socket
import time
import select
import pickle
import datetime

import constants

MESSAGE_SCAN_DELAY = 0.1

## helper functions ##

# return a encoded header that contain the length of given encoded string
def getLenHeader(encodedString):
    return f"{len(encodedString):<{constants.HEADER_SIZE}}".encode()

# wrapper for a user info, include the username and the header for that username
class UserInfo():
    def __init__(self, header, data, online_status=False):
        self.header = header
        self.data = data
        self.online_status = online_status # the user default state is offline
        self.msg_buffer = [] # the message buffer to store messages when user go offline
        self.last_online = '' # timestamp to when the user last online

    def __hash__(self):
        return hash((self.name, self.age))

    def isEqualTo(self, thatUserInfo):
        if self.data == thatUserInfo.data:
            return True
        return False
    
    def online(self):
        self.online_status = True

    def offline(self):
        self.online_status = False

    # def get_header(self):
    #     return self.header

    # def get_uname

# helper class to manage conversations on the server
class Conversation():
    def __init__(self, name, member_list=None, owner=None):
        self.name = name
        self.owner = owner
        self.member_list = member_list

    # take in a UserInfo object and determine whether the user is the owner or not
    def is_owner(self, user):
        if user.isEqualTo(self.owner):
            return True
        return False
    
    # find index of a member in the conversation with a certain condition function
    def indexOfMemberWith(self, condition_func):
        try:
            return next(i for i, element in enumerate(self.member_list) if condition_func(element))
        except StopIteration:
            return -1
        
    # take in a UserInfo object and remove that user from the group
    def remove_member(self, user):
        index = self.indexOfMemberWith(user.isEqualTo)
        del self.member_list[index]

    def has_member(self, user):
        for u in self.member_list:
            if u.isEqualTo(user):
                return True
        return False

class Server():
    def __init__(self, IP, PORT):
        self.server = socket.create_server((IP, PORT), family=socket.AF_INET6, dualstack_ipv6=True)

        # # Set the option to also listen on an IPv4 address
        # self.server.setsockopt(socket.IPPROTO_IPV6, socket.IPV6_V6ONLY, False)

        # self.server.bind((IP, PORT)) # bind the port

        self.sockets_list = [self.server]

        self.client_info = {}
        self.conversations = {}
        self.group_owners = {}

    # def send_file(self, client_socket, file_dir: str):
    #     filesize = os.path.getsize(filename)
    # # read a photo from a file as binary
    #     f = open(filedir, 'rb')
    #     l = f.read(1024)
    #     # send the photo
    #     while (l):
    #         c.send(l)
    #         l = f.read(1024)
    #     f.close()
    #     # c.send('done'.encode())
        
    #     # conf = ''
    #     # # wait for confirmation from the client
    #     # while conf == '':
    #     #     conf = c.recv(20).decode()
    #     # print("here")
    #     # # print out confirmation
    #     # print("Text from client: " + conf)
    
    # take in a raw error message and send it to the specified socket, with encoding and header
    def send_error_to(self, client_socket, err_msg):
        timestamp = datetime.datetime.now().strftime("%H:%M").encode('utf-8')
        err_msg_encoded = err_msg.encode('utf-8')
        error_header = f"{len(err_msg_encoded):<{constants.HEADER_SIZE}}".encode()
        content = str(constants.MsgType.ERROR.value).encode('utf-8') + self.client_info[client_socket].header \
        + self.client_info[client_socket].data + timestamp + error_header + err_msg_encoded

        client_socket.send(content)

    # take in an old_name and a new_name in the form {'header': ..., 'data'}, and send it to a client
    def send_renameTask_to(self, client_socket, old_name, new_name):
        # inform the client that a task will be sent next
        client_socket.send(str(constants.MsgType.TASK.value).encode('utf-8'))

        # ask the client to rename this conversation back to the old name
        client_socket.send(str(constants.TaskType.RENAME_CONVO.value).encode('utf-8'))

        # send the old convo name to the client
        client_socket.send(old_name['header'] + old_name['data'])

        # send the new convo name to the client
        client_socket.send(new_name['header'] + new_name['data'])

    # take in convo_name and member username in the form {'header': ..., 'data'}, and send it to a client
    def send_addMemTask_to(self, client_socket, convo_name, mem_uname):
        # inform the client that a task will be sent next
        client_socket.send(str(constants.MsgType.TASK.value).encode('utf-8'))

        # ask the client to add the member to its local list for the conversation
        client_socket.send(str(constants.TaskType.ADD_MEMBER.value).encode('utf-8'))

        # send the convo name to the client
        client_socket.send(convo_name['header'] + convo_name['data'])

        # send the new member username to the client
        client_socket.send(mem_uname['header'] + mem_uname['data'])

    # take in convo_name and member username in the form {'header': ..., 'data'}, and send a remove member task to a client
    def send_remvMemTask_to(self, client_socket, convo_name, mem_uname):
        # inform the client that a task will be sent next
        client_socket.send(str(constants.MsgType.TASK.value).encode('utf-8'))

        # ask the client to add the member to its local list for the conversation
        client_socket.send(str(constants.TaskType.ADD_MEMBER.value).encode('utf-8'))

        # send the convo name to the client
        client_socket.send(convo_name['header'] + convo_name['data'])

        # send the new member username to the client
        client_socket.send(mem_uname['header'] + mem_uname['data'])

    # take in convo_name in the form {'header': ..., 'data'}, and a UserInfo object
    # send a read receipt to the client_socket
    def send_readReceipt_to(self, client_socket, convo_name, receipt_sender):
        # tell the client that a read receipt will be send next
        client_socket.send(str(constants.MsgType.READ_RECEIPT.value).encode('utf-8'))

        # send the convo name that this receipt apply to
        # username_header = f"{len(convo_name):<{constants.HEADER_SIZE}}".encode('utf-8')
        client_socket.send(convo_name['header'] + convo_name['data'])

        # send the original_sender
        # sender_header = f"{len(original_sender):<{constants.HEADER_SIZE}}".encode('utf-8')
        client_socket.send(receipt_sender.header + receipt_sender.data)
        

    # receive a text message from the client (with header + content) and parse it
    def receive_txt(self, client_socket):
        header = client_socket.recv(constants.HEADER_SIZE)

        if not len(header):
            return False
        
        message_length = int(header.decode().strip())

        return {"header": header, "data": client_socket.recv(message_length)}

    def user_exist(self, user_info):
        for u in self.client_info.values():
            if user_info.data == u.data:
                return True
        
        return False

    def convo_exist(self, convo_name):
        for c in self.conversations.values():
            if convo_name == c.name:
                return True
            
        return False
    
    # find a convo by name
    def find_convo(self, convo_name):
        for c in self.conversations.values():
            if convo_name == c.name:
                return c
            
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
                sock = key_list[pos]
                return sock
                # # check if the socket is valid or not first, socket can become invalid once the user go offline
                # if sock in self.sockets_list:
                #     return sock
                # else:
                #     return False
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

                    user_info = UserInfo(user['header'], user['data'])
                    u_sock = self.get_sock_by_uinfo(user_info)
                    # if the user already exist in the database
                    if u_sock:
                        # change the socket info of the user to the new socket
                        self.client_info[client] = self.client_info.pop(u_sock)
                        self.client_info[client].online() # make the user online again

                        # append the new socket connection into the socket list
                        self.sockets_list.append(client)

                        
                        # forward the messages this client received while offline
                        # inform the client about offline messages
                        m_buffer = self.client_info[client].msg_buffer
                        self.send_error_to(client, "[INFO] You received {} messages while you were offline:".format(len(m_buffer)))

                        for msg in m_buffer:
                            # send the message to the target client
                            client.send(msg)
                        
                        # empty the buffer
                        self.client_info[client].msg_buffer = []


                        # send the message to the target client(s)
                        print("[INFO] User {} went online, address: {}:{}"\
                              .format(user['data'].decode('utf-8'), *client_addr))
                    else:
                        # add the user to the socket and info list if they don't exist
                        self.sockets_list.append(client)
                        
                        self.client_info[client] = UserInfo(user['header'], user['data'], True)
                        client_addr_values = client_addr[:2]
                        ip, port = client_addr_values
                        print("[INFO] New connection from user {}, address: {}:{}"\
                              .format(user['data'].decode('utf-8'), ip, port))
                    

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
                            print('[INFO] Closed connection from: {}'.format(self.client_info[s].data.decode('utf-8')))
                            self.sockets_list.remove(s)
                            del self.client_info[s]


                        else:
                            # if there is only one person (other than the sender) in the conversation, it is a direct message
                            convo = self.find_convo(target_info['data'])
                            if len(convo.member_list) <= 1:
                                # get the user socket
                                target_socket = self.get_sock_by_uinfo(convo.member_list[0])

                                # if the username does not exist, send back an error message to the client
                                if not target_socket:
                                    error_msg = f"[ERROR] \"{target_info['data'].decode('utf-8')}\" username not found".encode()
                                    error_header = f"{len(error_msg):<{constants.HEADER_SIZE}}".encode()
                                    s.send(str(constants.MsgType.ERROR.value).encode('utf-8') + user.header + user.data + timestamp + error_header + error_msg)
                            
                            
                                else:
                                    # get the user info
                                    target_user = self.client_info[target_socket]
                                    
                                    # if the user is online
                                    if target_user.online_status:
                                        # send the message to the target client(s)
                                        target_socket.send(str(msg_type).encode('utf-8') + user.header + user.data + timestamp + message['header'] + message['data'])

                                        print(f'[INFO] Received message from {user.data.decode("utf-8")} to {target_user.data.decode("utf-8")}: '\
                                            + f'{message["data"].decode("utf-8")}')
                                    else:
                                        # buffer the message and inform the sender
                                        target_user.msg_buffer.append(str(msg_type).encode('utf-8') + user.header + user.data \
                                                                           + timestamp + message['header'] + message['data'])
                                        
                                        self.send_error_to(s, "[INFO] User {} is currently offline, last online at {}\n".format(target_user.data.decode('utf-8'), target_user.last_online) \
                                                            + "Your message will be stored and forwarded once they go online again")


                            # else it is a group message
                            else:
                                group_name = target_info["data"].decode("utf-8")

                                # append the group name to the sender's username to distinguish from normal messages
                                appended_username = (group_name + '/' + user.data.decode('utf-8')).encode('utf-8')
                                appended_user_header = getLenHeader(appended_username)

                                print(f'[INFO] Received message from {user.data.decode("utf-8")} ' \
                                    + f'to group {group_name}: {message["data"].decode("utf-8")}')
                                    
                                
                                # loop through all the user in the conversation
                                convo = self.find_convo(target_info['data'])
                                if convo.has_member(user): # if the user is in this conversation
                                    for u in convo.member_list:
                                        
                                        if not u.isEqualTo(user):
                                            # get the user socket
                                            target_socket = self.get_sock_by_uinfo(u)

                                            # if the username does not exist, send back an error message to the client
                                            if not target_socket:
                                                error_msg = f"[ERROR] \"{u.data.decode('utf-8')}\" username not found".encode()
                                                error_header = f"{len(error_msg):<{constants.HEADER_SIZE}}".encode()
                                                s.send(str(constants.MsgType.ERROR.value).encode('utf-8') + user.header + user.data + timestamp + error_header + error_msg)
                                        
                                        
                                            else:
                                                # get the user info
                                                target_user = self.client_info[target_socket]
                                                # if the user is online
                                                if target_user.online_status:
                                                    # send the message to the target client(s)
                                                    target_socket.send(str(msg_type).encode('utf-8') + appended_user_header \
                                                                        + appended_username + timestamp + message['header'] + message['data'])

                                                else:
                                                    # buffer the message and inform the sender
                                                    target_user.msg_buffer.append(str(msg_type).encode('utf-8') + appended_user_header + appended_username \
                                                                                    + timestamp + message['header'] + message['data'])
                                                    
                                                    self.send_error_to(s, "[INFO] User {} is currently offline, last online at {}\n".format(target_user.data.decode('utf-8'), target_user.last_online) \
                                                                + "Your message will be stored and forwarded once they go online again")
                                                    
                                else:
                                    self.send_error_to(s, "[ERROR] You are not in this conversation")


                    elif msg_type == str(constants.MsgType.READ_RECEIPT.value): # a read receipt for an earlier message
                        # get the conversation this receipt apply to
                        convo_name = self.receive_txt(s)

                        # get the user whom  this receipt is for
                        target_user = self.receive_txt(s)

                        # get the user socket
                        target_socket = self.get_sock_by_uinfo(UserInfo(target_user['header'],target_user['data']))

                        # if the username does not exist, send back an error message to the client
                        if not target_socket:
                            continue # do nothing for the time being
                    
                        else:
                            # forward the read receipt to the user
                            self.send_readReceipt_to(target_socket, convo_name, self.client_info[s])



                    elif msg_type == str(constants.MsgType.FILE.value): # a file                        
                        # get the target user
                        target_user_byte = self.receive_txt(s)
                        target_user = UserInfo(target_user_byte['header'],target_user_byte['data'])

                        # get the user socket
                        target_socket = self.get_sock_by_uinfo(target_user)

                        # get the file name
                        file_name = self.receive_txt(s)

                        # get the file size
                        file_size = int(s.recv(constants.HEADER_SIZE).decode('utf-8'))

                        print(f'[INFO] Received file from {user.data.decode("utf-8")} ' \
                                    + f'to {target_user.data.decode("utf-8")}')

                        # send all the information above to the target
                        # inform the user that a file will be sent next
                        target_socket.send(str(constants.MsgType.FILE.value).encode('utf-8'))

                        target_socket.send(user.header + user.data)

                        target_socket.send(file_name['header'] + file_name['data'])

                        # Send the file size
                        target_socket.send(f"{file_size:<{constants.HEADER_SIZE}}".encode('utf-8'))

                        # Receive the file and forward it to the target in small chunks
                        total_received = 0
                        while total_received < file_size:
                            # Receive a chunk of the file
                            chunk = s.recv(min(file_size - total_received, constants.BUFFER_SIZE))

                            # Update the total number of bytes received
                            total_received += len(chunk)

                            # forward the chunk to the target
                            target_socket.send(chunk)



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

                            # save the conversation to the database if it is a new conversation
                            if not self.convo_exist(convo_name['data']):
                                
                                self.conversations[convo_name['data']] = Conversation(convo_name['data'], conversation_info)

                                print("[TASK] New conversation {} added by {}, members: {}"\
                                    .format(convo_name['data'].decode('utf-8'), user.data.decode('utf-8'), username_set))

                                if (len(conversation_info) != 1): # if this is a group chat (more than 2 people), add the person who created the group as a group owner
                                    self.conversations[convo_name['data']].owner = user
                        

                        elif task_type == str(constants.TaskType.RENAME_CONVO.value): # rename a conversation in the database
                            # get the old conversation name
                            old_name = self.receive_txt(s)
                            # old_name_str = old_name.decode('utf-8')

                            # get the new conversation name
                            new_name = self.receive_txt(s)
                            # new_name_str = new_name.decode('utf-8')

                            # check if the user have owner rights or not
                            if self.conversations[old_name['data']].is_owner(user):
                                # rename the conversation on the local dictionary
                                self.conversations[new_name['data']] = self.conversations.pop(old_name['data'])
                                # rename the conversation object's name variable
                                self.conversations[new_name['data']].name = new_name['data']

                                # inform the other member in the group about the name change
                                # loop through all the user in the conversation
                                for u in self.conversations[new_name['data']].member_list:
                                    
                                    if not u.isEqualTo(user):
                                        # get the user socket
                                        target_socket = self.get_sock_by_uinfo(u)

                                        # if the username does not exist, send back an error message to the client
                                        if not target_socket:
                                            continue # do nothing for the time being
                                    
                                    
                                        else:
                                            # send the message to the target client(s)
                                            self.send_renameTask_to(target_socket, old_name, new_name)

                                print("[TASK] Conversation {} renamed to {} by {}"\
                                    .format(old_name['data'].decode('utf-8'), new_name['data'].decode('utf-8'), user.data.decode('utf-8')))

                            else:
                                # send an error message to the user
                                self.send_error_to(s, "[ERROR] No required permission for name change")

                                ## send a task to the user to revert the name change
                                # inform the client that a task will be sent next
                                s.send(str(constants.MsgType.TASK.value).encode('utf-8'))

                                # ask the client to rename this conversation back to the old name
                                s.send(str(constants.TaskType.RENAME_CONVO.value).encode('utf-8'))

                                # send the new convo name to the client
                                s.send(new_name['header'] + new_name['data'])

                                # send the old convo name to the client
                                s.send(old_name['header'] + old_name['data'])


                        elif task_type == str(constants.TaskType.ADD_MEMBER.value):
                            # get the conversation name
                            convo_name = self.receive_txt(s)

                            # get the new member username
                            mem_uname = self.receive_txt(s)


                            # check if the user have owner rights or not
                            if self.conversations[convo_name['data']].is_owner(user):
                                # add new member to the conversation on the local dictionary
                                self.conversations[convo_name['data']].member_list.append(UserInfo(mem_uname['header'], mem_uname['data']))

                                ## inform the other member in the group about the new member
                                # loop through all the user in the conversation
                                for u in self.conversations[convo_name['data']].member_list:
                                    
                                    # tell everyone except the original sender
                                    if not u.isEqualTo(user):
                                        # get the user socket
                                        target_socket = self.get_sock_by_uinfo(u)

                                        # if the username does not exist, send back an error message to the client
                                        if not target_socket:
                                            continue # do nothing for the time being
                                    
                                        else:
                                            # send the message to the target client(s)
                                            self.send_addMemTask_to(target_socket, convo_name, mem_uname)
                            else:
                                # send an error message to the user
                                self.send_error_to(s, "[ERROR] No required permission for member management")


                        elif task_type == str(constants.TaskType.REMV_MEMBER.value):
                            # get the conversation name
                            convo_name = self.receive_txt(s)

                            # get the new member username
                            mem_uname = self.receive_txt(s)


                            # check if the user have owner rights or not
                            if self.conversations[convo_name['data']].is_owner(user):
                                print(self.conversations[convo_name['data']].indexOfMemberWith(user.isEqualTo))
                                # remove the member from the conversation on the local dictionary
                                self.conversations[convo_name['data']].remove_member(UserInfo(mem_uname['header'], mem_uname['data']))

                                ## inform the other member in the group about the removal
                                # loop through all the user in the conversation
                                for u in self.conversations[convo_name['data']].member_list:
                                    
                                    # tell everyone except the original sender
                                    if not u.isEqualTo(user):
                                        # get the user socket
                                        target_socket = self.get_sock_by_uinfo(u)

                                        # if the username does not exist, send back an error message to the client
                                        if not target_socket:
                                            continue # do nothing for the time being
                                    
                                    
                                        else:
                                            # send the message to the target client(s)
                                            self.send_remvMemTask_to(target_socket, convo_name, mem_uname)

                            else:
                                # send an error message to the user
                                self.send_error_to(s, "[ERROR] No required permission for member management")
                        
                                            
                    elif msg_type == '': # connection closed
                        s.close()
                        self.sockets_list.remove(s)

                        self.client_info[s].offline() # set the client's online status to offline
                        self.client_info[s].last_online = datetime.datetime.now().strftime("%H:%M") # store the user last online time


                        print("[INFO] User {} went offline, address: {}:{}"\
                              .format(user.data.decode('utf-8'), *client_addr))

                    # except s.error as e:
                    #     if e.errno == socket.errno.ECONNRESET:
                    #         # This error means the socket has been closed by the client
                    #         # Clean up the socket and move on to the next client
                    #         s.close()
                    #     continue

                    # handle exception sockets
                    for es in exception_sockets:
                        
                        # Remove from list for socket.socket()
                        self.sockets_list.remove(es)

                        # Remove from our list of users
                        del self.client_info[es]
            
            time.sleep(MESSAGE_SCAN_DELAY)

# start the server
host_name = socket.gethostname()
server = Server('', constants.PORT)
server.run()