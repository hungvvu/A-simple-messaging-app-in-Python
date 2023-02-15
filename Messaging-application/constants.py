from enum import Enum

BUFFER_SIZE = 10
HEADER_SIZE = 10
IP = "127.0.0.1"
PORT = 12345



class MsgType(Enum):
    ERROR = 0
    TEXT = 1
    TASK = 2
    CONFIRMATION = 3

class TaskType(Enum):
    ADD_CONVO = 1
    RENAME_CONVO = 2