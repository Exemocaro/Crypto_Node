from http import client
import platform
import logging
import json
import socket

PORT = 18018  # The port used by the server

CLIENTS_NUMBER = 5000
DATA_SIZE = 2048 # size of data to read from each received message
KNOWN_CREDENTIALS = [] # stores all the addresses this node knows
VALIDATION_PENDING_CREDENTIALS = [] # stores the addresses that are waiting for validation
ADDRESSES_FILE = 'known_credentials.txt' # file that stores the known addresses
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


# checking if the credentials are valid
def isValidCredentials(credentials):
    credentials = credentials.split(":")
    if len(credentials) == 2:
        if isValidIP(credentials[0]) and isValidPort(credentials[1]):
            return True
        else:
            return False
    else:
        return False

# checking if the format of the ip-address is valid
def isValidIP(address):
    try:
        socket.inet_aton(address)
        return True
    except socket.error:
        return False

# checking if the format of the port is valid
def isValidPort(port):
    try:
        port = int(port)
        if port > 0 and port < 65536:
            return True
        else:
            return False
    except ValueError:
        return False

# loads the addresses from the file into the list of addresses
def loadAddresses():
    global KNOWN_CREDENTIALS
    try:
        with open(ADDRESSES_FILE, 'r') as f:
            addresses_unparsed = f.readlines()
            temp = [x.strip("\n") for x in addresses_unparsed] # to remove whitespace characters like `\n` at the end of each line
            for a in temp:
                a = a.split(":")[0] # removes the ip out of the address
                print("\na:")
                print(a)
                if a not in KNOWN_CREDENTIALS:
                    KNOWN_CREDENTIALS.append(a)
            size = len(KNOWN_CREDENTIALS)
            logging.info(f"| READING ADDRESSES | Addresses read: {size}")
    except IOError: # if the file doesn't exist
        with open(ADDRESSES_FILE, 'w+') as f:
            addresses_unparsed = f.readlines()
            logging.info(f"| CREATING ADDRESSES FILE")
            KNOWN_CREDENTIALS = [x.strip() for x in addresses_unparsed] # to remove whitespace characters like `\n` at the end of each line

    print("Known Addresses:")
    print(KNOWN_CREDENTIALS, end="\n\n")

# adds an address into the list of addresses
def addCredentials(credentials):
    ip_port = credentials.split(":") # list with ip and port
    if credentials not in KNOWN_CREDENTIALS:
        with open(ADDRESSES_FILE, 'a') as f:
            f.write(f"{credentials}\n")
        KNOWN_CREDENTIALS.append(ip_port[0])
        logging.info(f"| SAVED ADDRESS | {credentials}")
    else:
        print(f"\nKnown address {credentials}.")

# checks if the passed address is in the list of known ones, and if not adds it.
def checkAndAddAddresses(credentials):
    ip_port = credentials.split(":") # list with ip and port
    if ip_port[0] not in KNOWN_CREDENTIALS:
        if isValidCredentials(credentials):
            print(f"\nUnknown address {credentials}! Saving it...")
            addCredentials(credentials)
            logging.info(f"| SAVED ADDRESS | {credentials}")
        else:
            print(f"\nInvalid address {credentials}!")
            logging.info(f"| INVALID ADDRESS | {credentials}")
    else:
        print(f"\nKnown address {credentials}.")

""" 
def validateAdress(connection, address):
    try:
        data = {"type": "hello", "version": "0.8.0" ,"agent " : "Kerma-Core Client 0.8"}
        data_to_send = json.dumps(data)
        data_to_send = str.encode(str(data_to_send + "\n"))

        VALIDATION_SETTINGS.append(address)

        print(f"\nSending data: \n{data}")
        connection.sendall(data_to_send) # we can't send str(data) because it must be a "byte-like object"
        logging.info(f"| SENT | {address} | {data}")

    except Exception as e:
        logging.error(f"| ERROR | {address} | VALIDATE | {e} | {e.args}")
        print(f"\nError on validate! {e} | {e.args}\n")
    finally:
        pass
"""
