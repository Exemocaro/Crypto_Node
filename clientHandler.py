import socket
import logging
#import threading
import json

from _thread import *
from tracemalloc import start # new threading lib
from config import *
from responses import *

class Client:
    def __init__(self, credentials):
        self.credentials = credentials
        self.ip = credentials.split(":")[0]
        self.port = credentials.split(":")[1]
        self.isConnectionOpen = False


def newClient():
    pass

