from http import client
import platform
import logging

from database.KnownNodesHandler import KnownNodesHandler
from database.ObjectHandler import ObjectHandler
from network.NewServer import *
from database.KnownNodesHandler import *

PORT = 18018  # The port used by the server
SERVER_ADDRESS = ('', PORT)

INCOMING_DATA_BUFFER = 1024

CLIENTS_NUMBER = 500
DATA_SIZE = 2048  # size of data to read from each received message

ADDRESSES_FILE = 'database/known_credentials.txt'  # file that stores the known addresses
OBJECTS_FILE = 'database/known_objects.json'  # file that stores the known objects

SYSTEM = platform.system().lower()  # our operating system

AGENT_NAME = "This could be your node!"

NODE_HANDLER = KnownNodesHandler(known_nodes_file=ADDRESSES_FILE)
OBJECT_HANDLER = ObjectHandler(objects_file=OBJECTS_FILE)
NETWORKING = NodeNetworking(NODE_HANDLER)

# logging things
logging.basicConfig(
    filename='logs.log',
    level=logging.DEBUG,
    format='%(asctime)s %(message)s', 
    datefmt='%d/%m/%Y %H:%M:%S'
)



