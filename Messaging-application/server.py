#!/usr/bin/python# This is server.py file
import socket
import time
import select

import constants

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



server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
server.bind((constants.IP, constants.PORT)) # bind the port

sockets_list = [server]

client_info = {}

server.listen(5) #  wait for client connection.


while True:
    read_sockets, _, exception_sockets = select.select(sockets_list, [], sockets_list)

    # iterate over the sockets that have something for us to read
    for s in read_sockets:

        # if we see the server socket, it means there is no new message to read and we should wait and accept incoming connections
        if s == server:
            client, client_addr = server.accept()

            user = receive_txt(client)
            if user is False:
                # do something
                continue

        
            sockets_list.append(client)

            client_info[client] = user

            print("New connection from {}:{}, username: {}".format(*client_addr, user['data'].decode('utf-8')))
            

        # if s is a socket other than the server, we have gotten a new message to read
        else:
            user = client_info[s]

            # first, get the user info
            target_info = receive_txt(s)

            # get the timestamp of the message, since the format is always HH:MM, we can safely assume that it is always 5 bytes
            timestamp = s.recv(5)

            # next, parse out the message
            message = receive_txt(s)

            


            # if there is no message, close the connection
            if message is False:
                print('Closed connection from: {}'.format(client_info[s]['data'].decode('utf-8')))
                sockets_list.remove(s)
                del client_info[s]


            else:
                # if the username does not exist, send back an error message to the client
                if target_info not in client_info.values():
                    error_msg = "error: username not found".encode()
                    error_header = f"{len(error_msg):<{constants.HEADER_SIZE}}".encode()
                    s.send(user['header'] + user['data'] + timestamp + error_header + error_msg)
                
                
                else:
                    # extract the socket from the username
                    key_list = list(client_info.keys())
                    val_list = list(client_info.values())
                    
                    pos = val_list.index(target_info)

                    target_socket = key_list[pos]

                    # send the message to the target client(s)
                    target_socket.send(user['header'] + user['data'] + timestamp + message['header'] + message['data'])

                    print(f'{timestamp.decode("utf-8")}, received message from {user["data"].decode("utf-8")}: {message["data"].decode("utf-8")}')

            # handle exception sockets
            for es in exception_sockets:
                
                # Remove from list for socket.socket()
                sockets_list.remove(es)

                # Remove from our list of users
                del client_info[es]