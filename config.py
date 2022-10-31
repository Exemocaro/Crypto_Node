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
            print(addresses_unparsed)
            temp = [x.strip("\n") for x in addresses_unparsed] # to remove whitespace characters like `\n` at the end of each line
            print("\ntemp:")
            print(temp)
            for a in temp:
                a = a.split(":")[0] # removes the ip out of the address
                print("\na:")
                print(a)
                if a not in KNOWN_CREDENTIALS:
                    KNOWN_CREDENTIALS.append(a)
            size = len(KNOWN_CREDENTIALS)
            logging.info(f"| READING ADDRESSES | Addresses read: {size}")
    except IOError: # if the file doesn't exist
        with open(KNOWN_CREDENTIALS, 'w+') as f:
            addresses_unparsed = f.readlines()
            logging.info(f"| CREATING ADDRESSES FILE")
            KNOWN_CREDENTIALS = [x.strip() for x in addresses_unparsed] # to remove whitespace characters like `\n` at the end of each line

    print("Known Addresses:")
    print(KNOWN_CREDENTIALS, end="\n\n")

# adds an address into the list of addresses
def addAddress(address):
    if address not in KNOWN_CREDENTIALS:
        with open(KNOWN_CREDENTIALS, 'a') as f:
            f.write(f"{address[0]}")
            f.write(f":{address[1]}\n")
        KNOWN_CREDENTIALS.append(address[0])
        logging.info(f"| SAVED ADDRESS | {address}")
    else:
        print(f"\nKnown address {address}.")

# checks if the passed address is in the list of known ones, and if not adds it.
def checkAddresses(client_address):
    if client_address[0] not in KNOWN_CREDENTIALS:
        print(f"\nUnknown address {client_address}! Saving it...")
        addAddress(client_address)
        logging.info(f"| SAVED ADDRESS | {client_address}")
    else:
        print(f"\nKnown address {client_address}.")

# returns true if an address is already known to us
def checkAddress(client_address):
    client_address.split(":")[0]
    return client_address in KNOWN_CREDENTIALS


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
