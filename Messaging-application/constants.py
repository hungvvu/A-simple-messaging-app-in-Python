from enum import Enum
import socket
BUFFER_SIZE = 10
HEADER_SIZE = 10

IP = '127.0.0.1'
HOST = socket.gethostname()
PORT = 12345



class MsgType(Enum):
    ERROR = 0
    TEXT = 1
    TASK = 2
    READ_RECEIPT = 3
    FILE = 4

class TaskType(Enum):
    ADD_CONVO = 1
    RENAME_CONVO = 2
    ADD_MEMBER = 3
    REMV_MEMBER = 4