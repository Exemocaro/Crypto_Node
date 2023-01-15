from http import client
import platform
import logging

PORT = 18018  # The port used by the server
SERVER_ADDRESS = ('', PORT)

TIMEOUT = 2  # The timeout for the server

BLOCK_REWARD = 50 * (10 ** 12)

AUTO_SAVE_INTERVAL = 5  # seconds

INCOMING_DATA_BUFFER = 1024
CLIENTS_NUMBER = 500
DATA_SIZE = 2048  # size of data to read from each received message

ADDRESSES_FILE = 'database/known_credentials.txt'  # file that stores the known addresses
OBJECTS_FILE = 'database/known_objects.json'  # file that stores the known objects
UTXO_FILE = 'database/utxo.json'  # file that stores the utxo

BOOTSTRAP_NODE = "128.130.122.101:18018" # bootstrapping node

SYSTEM = platform.system().lower()  # our operating system

AGENT_NAME = "THIS COULD BE YOUR NODE"
LOG_LIMIT = 18000000
# logging things
logging.basicConfig(
    filename='logs.log',
    level=logging.DEBUG,
    format='%(asctime)s %(message)s', 
    datefmt='%d/%m/%Y %H:%M:%S'
)

TARGET = "00000002af000000000000000000000000000000000000000000000000000000"
TARGET_INT = int(TARGET, 16)

GENESIS_BLOCK = {
    "T": TARGET,
    "created": 1624219079,
    "miner" : "dionyziz",
    "nonce": "0000000000000000000000000000000000000000000000000000002634878840",
    "note" : "The Economist 2021-06-20: Crypto-miners are probably to blame for the graphics-chip shortage" ,
    "previd" : None,
    "txids" : [],
    "type" : "block"
}
GENESIS_BLOCK_ID = "00000000a420b7cefa2b7730243316921ed59ffe836e111ca3801f82a4f5360e"

# Genesis block always has to be in the known objects, otherwise the node will not be able to accept any other blocks
DEFAULT_OBJECTS = [
    {
        "type": "block",
        "validity": "valid",
        "txid": GENESIS_BLOCK_ID,
        "object": GENESIS_BLOCK
    }
]
    

SAMPLE_BLOCK = {
            "type": "block",
            "txids": [],
            "nonce": "c5ee71be4ca85b160d352923a84f86f44b7fc4fe60002214bc1236ceedc5c615",
            "miner": "Jan",
            "note": "420",
            "previd": "00000000a420b7cefa2b7730243316921ed59ffe836e111ca3801f82a4f5360e",
            "created": 1649827795114,
            "T": "00000002af000000000000000000000000000000000000000000000000000000"
        }

