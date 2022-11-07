from config import *
from queue import Queue
from threading import Thread
from socket import socket, SOL_SOCKET, SO_REUSEADDR

from utility.logplus import LogPlus

# What ConnectionHandler does:
# - Store connection, credentials, in_queue and out_queue
# - Send messages from out_queue regularly
# - Listen for received messages and put them in in_queue


class ConnectionHandler:

    def __init__(self, connection=None, credentials=None):
        self.connection = connection
        self.credentials = credentials
        self.in_buffer = b""
        self.in_queue = Queue()
        self.out_queue = Queue()
        self.is_open = connection is not None

    def start_connection(self):
        self.is_open = False
        self.connection = socket.socket()
        self.connection.setsockopt(SOL_SOCKET, SO_REUSEADDR, 1)
        try:
            self.connection.connect(self.credentials)
        except Exception as e:
            LogPlus.error(f"| ERROR | Could not connect to {self.credentials}")
            return False

        self.is_open = True

    def start(self):
        # start thread to not block main thread
        thread = Thread(target=self.run)
        thread.start()

    def run(self):
        while self.is_open:
            self.send_from_queue()
            self.receive()

    def send_from_queue(self):
        if not self.out_queue.empty():
            message = self.out_queue.get_nowait()
            if not self.send_packet_instantly(message):
                self.is_open = False

    def receive(self):
        try:
            self.connection.setblocking(False)
            incoming_data = self.connection.recv(1024)
        except Exception as e:
            # this will happen when there is no data to receive (so almost every time)
            return

        if incoming_data not in [None, b'']:
            self.in_buffer += incoming_data

        if b'\n' in self.in_buffer:
            # split buffer into messages
            messages = self.in_buffer.split(b'\n')
            # put all messages except the last one in the queue
            for message in messages[:-1]:
                self.in_queue.put(message)
                LogPlus.info(f"| INFO | Received message {message} from {self.credentials}. Added to queue.")
            # put the last message in the buffer
            self.in_buffer = messages[-1]

    # normal send function just adds to the queue
    def send(self, message):
        LogPlus.info(f"| INFO | Adding message {message} to {self.credentials} queue")
        self.out_queue.put(message)

    def send_packet_instantly(self, message):
        try:
            # make sure the message is byte-like object
            if not isinstance(message, bytes):
                message = str(message).encode()
            self.connection.sendall(message)
        except Exception as e:
            LogPlus.error(f"| ERROR | Could not send message {message} to {self.credentials}")
            self.is_open = False
            return False
        return True

    def close(self):
        self.is_open = False
        self.connection.close()
