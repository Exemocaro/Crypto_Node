
# What NodeNetworking does:
# - Listen on port 18018 for incoming connections
# - Connect to other nodes
# - keep track of all open connections

from threading import Thread
from socket import socket, SOL_SOCKET, SO_REUSEADDR

from engine.inputHandling import *
from network.ConnectionHandler import ConnectionHandler
from utility.credentials_utility import *
from engine.generateMessage import *

from network.NewServer import *
from database.KnownNodesHandler import *

from config import *


class NodeNetworking:

    def __init__(self, peers_db=None):
        self.handlers = []
        self.server = None
        self.server_thread = None
        self.peers_db = peers_db
        self.check_received_data_thread = None

    def start_server(self):
        self.server = socket()
        self.server.setsockopt(SOL_SOCKET, SO_REUSEADDR, 1)
        self.server.bind(SERVER_ADDRESS)
        self.server.listen(CLIENTS_NUMBER)
        print("Server started")

        # start a new thread to accept connections
        self.server_thread = Thread(target=self.accept_connections).start()

        # start a new thread to check for received data
        self.check_received_data_thread = Thread(target=self.check_received_data).start()

    def accept_connections(self):
        while True:
            connection, credentials = self.server.accept()
            LogPlus.info(f"| INFO | New connection from {credentials}")
            handler = self.handle_connection(connection, credentials)
            handler.send(MessageGenerator.generate_hello_message())
            handler.send(MessageGenerator.generate_getpeers_message())

    def handle_connection(self, connection, credentials):
        # use a ConnectionHandler class to handle the connection
        handler = ConnectionHandler(connection, credentials)

        self.handlers.append(handler)
        handler.start()
        return handler

    def remove_closed_connections(self):
        for handler in self.handlers:
            if not handler.is_open:
                self.handlers.remove(handler)

    def check_received_data(self):
        while True:
            for handler in self.handlers:
                if not handler.in_queue.empty():
                    data = handler.in_queue.get()
                    LogPlus.info(f"| INFO | Received {data} from {handler.credentials}")
                    res = handle_input(data, handler.credentials)
                    if res:
                        # if we know the node, we change the port to the known one
                        if self.peers_db:
                            cleaned_credentials = self.peers_db.clean_credentials(convert_tuple_to_string(handler.credentials))
                            self.send_to_node(cleaned_credentials, res)

    # creating a new connection to the credentials, returning handler
    def connect_to_node(self, credentials):
        LogPlus.info(f"| INFO | Connecting to {credentials}")
        try:
            connection = socket()
            connection.connect(convert_string_to_tuple(credentials))
            LogPlus.info(f"| INFO | Connected to {credentials}")
            return self.handle_connection(connection, credentials)
        except Exception as e:
            LogPlus.error(f"| ERROR | Error when connecting to {credentials} | {e}")
            return None

    def send_to_node(self, credentials, data):
        LogPlus.info(f"| INFO | Sending {data} to {credentials}")
        for handler in self.handlers:
            if handler.credentials == convert_string_to_tuple(credentials):
                handler.send(data)
                return True

        # no connection found
        # so we create a new connection and send the data there
        self.connect_to_node(credentials).send(data)
