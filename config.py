from http import client
import platform
import logging

PORT = 18018  # The port used by the server
SERVER_ADDRESS = ('', PORT)

TIMEOUT = 10  # The timeout for the server

INCOMING_DATA_BUFFER = 1024

CLIENTS_NUMBER = 500
DATA_SIZE = 2048  # size of data to read from each received message

ADDRESSES_FILE = 'database/known_credentials.txt'  # file that stores the known addresses
OBJECTS_FILE = 'database/known_objects.json'  # file that stores the known objects

SYSTEM = platform.system().lower()  # our operating system

AGENT_NAME = "This could be your node!"


# logging things
logging.basicConfig(
    filename='logs.log',
    level=logging.DEBUG,
    format='%(asctime)s %(message)s', 
    datefmt='%d/%m/%Y %H:%M:%S'
)



