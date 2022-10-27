import platform
import logging
import json
import socket

PORT = 18018  # The port used by the server

CLIENTS_NUMBER = 5000
DATA_SIZE = 2048 # size of data to read from each received message
KNOWN_ADDRESSES = [] # stores all the addresses this node knows
VALIDATION_SETTINGS = [] # stores the addresses that are waiting for validation
ADDRESSES_FILE = 'known_addresses.txt' # file that stores the known addresses
SYSTEM = platform.system().lower() # our operating system
SERVER_ADDRESS = ('', PORT)

# logging things
logging.basicConfig(
    filename='logs.log', 
    #encoding='utf-8', 
    level=logging.DEBUG,
    format='%(asctime)s %(message)s', 
    datefmt='%d/%m/%Y %H:%M:%S'
)


# ------------------------------------------- AUX FUNCTIONS ------------------------------------------- #


# loads the addresses from the file into the list of addresses
def loadAddresses():
    global KNOWN_ADDRESSES
    try:
        with open(ADDRESSES_FILE, 'r') as f:
            addresses_unparsed = f.readlines()
            temp = [x.strip() for x in addresses_unparsed] # to remove whitespace characters like `\n` at the end of each line
            for a in temp:
                KNOWN_ADDRESSES.append(a)
            size = len(KNOWN_ADDRESSES)
            logging.info(f"| READING ADDRESSES | Addresses read: {size}")
    except IOError: # if the file doesn't exist
        with open('known_addresses.txt', 'w+') as f:
            addresses_unparsed = f.readlines()
            logging.info(f"| CREATING ADDRESSES FILE")
            KNOWN_ADDRESSES = [x.strip() for x in addresses_unparsed] # to remove whitespace characters like `\n` at the end of each line

    print("Known Addresses:")
    print(KNOWN_ADDRESSES, end="\n\n")


def addAddress(address):
    if address not in KNOWN_ADDRESSES:
        print(f"\nUnknown address {address}! Saving it...")
        with open('known_addresses.txt', 'a') as f:
            f.write(f"{address}\n")
        KNOWN_ADDRESSES.append(address)
        logging.info(f"| SAVED ADDRESS | {address}")
    else:
        print(f"\nKnown address {address}.")

# checks if the passed address is in the list of known ones, and if not adds it.
def checkAddresses(client_address):
    if client_address[0] not in KNOWN_ADDRESSES:
        print(f"\nUnknown address {client_address}! Saving it...")
        with open('known_addresses.txt', 'a') as f:
            f.write(f"{client_address[0]}\n")
        KNOWN_ADDRESSES.append(client_address[0])
        logging.info(f"| SAVED ADDRESS | {client_address}")
    else:
        print(f"\nKnown address {client_address}.")

def checkAddress(address):
    return address in KNOWN_ADDRESSES


def validateAdress(address):
    try:
        data = {"type": "hello", "version": "0.8.0" ,"agent " : "Kerma-Core Client 0.8"}
        data_to_send = json.dumps(data)
        data_to_send = str.encode(str(data_to_send + "\n"))

        VALIDATION_SETTINGS.append(address)

        print(f"\nSending data: \n{data}")
        clientSocket = socket.socket()
        clientSocket.connect(address)
        clientSocket.send(data_to_send)
        logging.info(f"| SENT | {address} | {data}")

    except Exception as e:
        logging.error(f"| ERROR | {address} | VALIDATE | {e} | {e.args}")
        print(f"\nError on validate! {e} | {e.args}\n")
    finally:
        pass


def isValidationPending(address):
    return address in VALIDATION_SETTINGS

def finanlizeValidation(address):
    VALIDATION_SETTINGS.remove(address)
    KNOWN_ADDRESSES.append(address)
    print(f"\nValidation finalized for {address}!")
    logging.info(f"| VALIDATION FINALIZED | {address}")
