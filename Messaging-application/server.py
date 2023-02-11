#!/usr/bin/python# This is server.py file
import socket
import time
import select

HEADER_SIZE = 10 # the length of the message header
BUFFER_SIZE = 10

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
        header = client_socket.recv(HEADER_SIZE)

        if not len(header):
            return False
        
        message_length = int(header.decode().strip())

        return {"header": header, "data": client_socket.recv(message_length)}
    except:
        return False


IP = "127.0.0.1"
PORT = 12345

server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
server.bind((IP, PORT)) # bind the port

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
            # target = target_info['data'].decode()

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
                    error_header = f"{len(error_msg):<{HEADER_SIZE}}".encode()
                    s.send(user['header'] + user['data'] + error_header + error_msg)
                    
                    # discard the message since it has no receiver
                    message = ''
                
                
                else:
                    # extract the socket from the username
                    key_list = list(client_info.keys())
                    val_list = list(client_info.values())
                    
                    pos = val_list.index(target_info)

                    target_socket = key_list[pos]
                    
                # send the message to the target client(s)
                target_socket.send(user['header'] + user['data'] + message['header'] + message['data'])

                print(f'Received message from {user["data"].decode("utf-8")}: {message["data"].decode("utf-8")}')

            # handle exception sockets
            for es in exception_sockets:
                
                # Remove from list for socket.socket()
                sockets_list.remove(es)

                # Remove from our list of users
                del client_info[es]
            


'''
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
    
    send_file(s, c, 'resources/potato.jpg')
    c.close()
    
        

    # # send the photo to the client
    # msg = str(data.decode('utf-8'))
    # msg = f'{len(msg):<{HEADER_SIZE}}' + msg # append the header to the message (currently contain only msg length)
    # c.send(bytes(msg, 'utf-8'))
        
    
    # time.sleep(3*len(msg)) # to avoid closing the connection immediately and allow the transmitting to finish
    # c.close() # close the connection
'''