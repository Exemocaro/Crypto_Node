
# What NodeNetworking does:
# - Listen on port 18018 for incoming connections
# - Connect to other nodes
# - keep track of all open connections

from threading import Thread
from socket import socket, SOL_SOCKET, SO_REUSEADDR

from engine.inputHandler import *
from engine.MessageGenerator import *

from network.ConnectionHandler import ConnectionHandler

from utility.credentials_utility import *

from database.KnownNodesHandler import *
from database.ObjectHandler import *
from database.UTXO import *

from config import *


class NodeNetworking:

    handlers = []
    server = None
    server_thread = None
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

        # connect to the known nodes
        for node in KnownNodesHandler.known_nodes:
            NodeNetworking.connect_to_node(node)

        # ask all peers for their chaintip
        NodeNetworking.send_to_all_nodes(MessageGenerator.generate_hello_message())
        NodeNetworking.send_to_all_nodes(MessageGenerator.generate_getchaintip_message())
        # NodeNetworking.send_to_all_nodes(MessageGenerator.generate_getpeers_message())
        NodeNetworking.send_to_all_nodes(MessageGenerator.generate_getmempool_message())
        # Height 17
        # NodeNetworking.send_to_all_nodes(MessageGenerator.generate_getobject_message("00000000deacae40c9a486b5443ad7a437062e34109267229924bbb0dcbd341b"))
        # Height 3XX
        # NodeNetworking.send_to_all_nodes(MessageGenerator.generate_getobject_message("00000000c5a4617bf184142c54f137de6cca2046825608b42cb69cfc9ed10384"))

        # Update the pending / missing objects
        ObjectHandler.update_all_pending_objects()
        revalidate_pending_objects()

    @staticmethod
    def accept_connections():
        print("Accepting connections...")
        while True:
            try:
                connection, credentials = NodeNetworking.server.accept()
                LogPlus.info(f"| INFO | New connection from {credentials}")
                NodeNetworking.handler = NodeNetworking.handle_connection(connection, credentials)
                KnownNodesHandler.add_node(convert_tuple_to_string(credentials)) # add the credentials into the database
                NodeNetworking.handler.send(MessageGenerator.generate_hello_message())
                NodeNetworking.handler.send(MessageGenerator.generate_getpeers_message())
            except Exception as e:
                LogPlus.error(f"| ERROR | NodeNetworking.accept_connections | {e}")

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
                    responses = handle_input(data, handler)
                    if responses is None:
                        continue
                    for (cleaned_credentials, res) in responses:
                        # if credantials is None, send to all nodes
                        if cleaned_credentials is None:
                            NodeNetworking.send_to_all_nodes(res)
                            continue
                        # if cleanead credentials is a tuple, convert it to a string
                        if type(cleaned_credentials) is tuple:
                            cleaned_credentials = convert_tuple_to_string(cleaned_credentials)
                        cleaned_credentials = KnownNodesHandler.clean_credentials(cleaned_credentials)
                        NodeNetworking.send_to_node(cleaned_credentials, res)

    # creating a new connection to the credentials, returning handler
    @staticmethod
    def connect_to_node(credentials):
        LogPlus.info(f"| INFO | Connecting to {credentials}")
        try:
            # connection = socket()
            # connection.connect(convert_string_to_tuple(credentials))
            # LogPlus.info(f"| INFO | Connected to {credentials}")
            return NodeNetworking.handle_connection(None, credentials)
        except Exception as e:
            LogPlus.error(f"| ERROR | Error when connecting to {credentials} | {e}")
            return None

    @staticmethod
    def send_to_node(credentials, data):
        LogPlus.info(f"| INFO | Sending {data} to {credentials}")
        # convert credentials to tuple if it is a string
        if type(credentials) is str:
            credentials = convert_string_to_tuple(credentials)
        for handler in NodeNetworking.handlers:
            if handler.credentials == credentials:
                handler.send(data)
                return True

        # no connection found
        # so we create a new connection and send the data there

        handler = NodeNetworking.connect_to_node(credentials)
        if handler is None:
            return False
        handler.send(data)

    @staticmethod
    def send_to_all_nodes(data):
        for handler in NodeNetworking.handlers:
            handler.send(data)

    @staticmethod
    def copy_utxo(set):
        """"Takes a set an creates a deep copy of it"""
        copy = {}
        for key in set:
            copy[key] = []
            for value in set[key]:
                copy[key].append(value)
        return copy

