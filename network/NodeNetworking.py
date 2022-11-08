
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

from network.NodeNetworking import *
from database.KnownNodesHandler import *

from config import *


class NodeNetworking:

    handlers = []
    server = None
    server_thread = None
    peers_db = None
    check_received_data_thread = None

    @staticmethod
    def start_server():
        NodeNetworking.server = socket()
        NodeNetworking.server.setsockopt(SOL_SOCKET, SO_REUSEADDR, 1)
        NodeNetworking.server.bind(SERVER_ADDRESS)
        NodeNetworking.server.listen(CLIENTS_NUMBER)
        print("Server started")

        # start a new thread to accept connections
        NodeNetworking.server_thread = Thread(target=NodeNetworking.accept_connections).start()

        # start a new thread to check for received data
        NodeNetworking.check_received_data_thread = Thread(target=NodeNetworking.check_received_data).start()

    @staticmethod
    def accept_connections():
        while True:
            connection, credentials = NodeNetworking.server.accept()
            LogPlus.info(f"| INFO | New connection from {credentials}")
            NodeNetworking.handler = NodeNetworking.handle_connection(connection, credentials)
            NodeNetworking.handler.send(MessageGenerator.generate_hello_message())
            NodeNetworking.handler.send(MessageGenerator.generate_getpeers_message())

    @staticmethod
    def handle_connection(connection, credentials):
        # use a ConnectionHandler class to handle the connection
        handler = ConnectionHandler(connection, credentials)

        NodeNetworking.handlers.append(handler)
        handler.start()
        return handler

    @staticmethod
    def remove_closed_connections():
        for handler in NodeNetworking.handlers:
            if not handler.is_open:
                NodeNetworking.handlers.remove(handler)

    @staticmethod
    def check_received_data():
        while True:
            for handler in NodeNetworking.handlers:
                if not handler.in_queue.empty():
                    data = handler.in_queue.get()
                    LogPlus.info(f"| INFO | Received {data} from {handler.credentials}")
                    res = handle_input(data, handler.credentials)
                    if res:
                        # if we know the node, we change the port to the known one
                        if NodeNetworking.peers_db:
                            cleaned_credentials = NodeNetworking.peers_db.clean_credentials(convert_tuple_to_string(handler.credentials))
                            NodeNetworking.send_to_node(cleaned_credentials, res)

    # creating a new connection to the credentials, returning handler
    @staticmethod
    def connect_to_node(credentials):
        LogPlus.info(f"| INFO | Connecting to {credentials}")
        try:
            connection = socket()
            connection.connect(convert_string_to_tuple(credentials))
            LogPlus.info(f"| INFO | Connected to {credentials}")
            return NodeNetworking.handle_connection(connection, credentials)
        except Exception as e:
            LogPlus.error(f"| ERROR | Error when connecting to {credentials} | {e}")
            return None

    @staticmethod
    def send_to_node(credentials, data):
        LogPlus.info(f"| INFO | Sending {data} to {credentials}")
        for handler in NodeNetworking.handlers:
            if handler.credentials == convert_string_to_tuple(credentials):
                handler.send(data)
                return True

        # no connection found
        # so we create a new connection and send the data there
        NodeNetworking.connect_to_node(credentials).send(data)


