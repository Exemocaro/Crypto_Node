import socket
import logging
import json

from _thread import *
from tracemalloc import start # new threading lib
from config import *


class Client:
    def __init__(self, credentials):
        self.credentials = credentials
        self.ip = credentials.split(":")[0]
        self.port = credentials.split(":")[1]
        self.isConnectionOpen = False
        self.socket = None

    def connect(self):
        self.socket = socket.socket()
        self.socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)

        try:
            self.socket.connect((self.ip, int(self.port)))
        except socket.error as e:
            logging.error(f"| ERROR | {e} | {e.args} | Error when connecting to {self.credentials}")
            print(str(e))
            return False

        self.isConnectionOpen = True
        logging.info(f"| CONNECTED | {self.credentials}")
        print(f"Connected to {self.credentials}")
        return True

    def send(self, data):
        # check if data is byte-like and convert it to bytes if it's not
        if not isinstance(data, bytes):
            data = data.encode()

        try:
            self.socket.sendall(data)
        except socket.error as e:
            logging.error(f"| ERROR | {e} | {e.args} | Error when sending data to {self.credentials}")
            print(str(e))
            return False

        logging.info(f"| SENT | {self.credentials} | {data}")
        print(f"Sent data to {self.credentials}")
        return True





