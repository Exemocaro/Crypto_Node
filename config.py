import platform
import logging
import json
import socket

HOST = "192.168.56.1" # LOCAL
#HOST = "143.244.205.206"  # MINE
#HOST = "4.231.16.23" #JAN
#HOST = "139.59.205.101" #SIMÃO
PORT = 18018  # The port used by the server

CLIENTS_NUMBER = 5000
DATA_SIZE = 2048 # size of data to read from each received message
KNOWN_CREDENTIALS = [] # stores all the addresses this node knows
VALIDATION_PENDING_ADRESSES = [] # stores the addresses that are waiting for validation
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


#checking if the credentials are valid
def isValidCredentials(credentials):
    credentials = credentials.split(":")
    if len(credentials) == 2:
        if isValidIP(credentials[0]) and isValidPort(credentials[1]):
            return True
        else:
            return False
    else:
        return False

#checking if the format of the ip-address is valid
def isValidIP(address):
    try:
        socket.inet_aton(address)
        return True
    except socket.error:
        return False

#checking if the formt of the port is valid
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
                if a not in KNOWN_CREDENTIALS:
                    if isValidCredentials(a):
                        KNOWN_CREDENTIALS.append(a)
            size = len(KNOWN_CREDENTIALS)
            logging.info(f"| READING ADDRESSES | Addresses read: {size}")
    except IOError: # if the file doesn't exist
        with open(ADDRESSES_FILE, 'w+') as f:
            addresses_unparsed = f.readlines()
            logging.info(f"| CREATING ADDRESSES FILE")
            KNOWN_CREDENTIALS = [x.strip("\n") for x in addresses_unparsed] # to remove whitespace characters like `\n` at the end of each line

    print("Known Addresses:")
    print(KNOWN_CREDENTIALS, end="\n\n")

def addAddress(address):
    if address not in KNOWN_CREDENTIALS:
        print(f"\nUnknown address {address}! Saving it...")
        with open('KNOWN_CREDENTIALS.txt', 'a') as f:
            f.write(f"{address}\n")
        KNOWN_CREDENTIALS.append(address)
        logging.info(f"| SAVED ADDRESS | {address}")
    else:
        print(f"\nKnown address {address}.")

# checks if the passed address is in the list of known ones, and if not adds it.
def checkAddresses(client_address):
    if client_address[0] not in KNOWN_CREDENTIALS:
        print(f"\nUnknown address {client_address}! Saving it...")
        with open('KNOWN_CREDENTIALS.txt', 'a') as f:
            f.write(f"{client_address[0]}\n")
        KNOWN_CREDENTIALS.append(client_address[0])
        logging.info(f"| SAVED ADDRESS | {client_address}")
    else:
        print(f"\nKnown address {client_address}.")

def checkAddress(client_address):
    return client_address[0] in KNOWN_CREDENTIALS


def validateAdress(connection, address):
    try:
        data = {"type": "hello", "version": "0.8.0" ,"agent " : "Kerma-Core Client 0.8"}
        data_to_send = json.dumps(data)
        data_to_send = str.encode(str(data_to_send + "\n"))

        VALIDATION_PENDING_ADRESSES.append(address)

        print(f"\nSending data: \n{data}")
        connection.sendall(data_to_send) # we can't send str(data) because it must be a "byte-like object"
        logging.info(f"| SENT | {address} | {data}")

    except Exception as e:
        logging.error(f"| ERROR | {address} | VALIDATE | {e} | {e.args}")
        print(f"\nError on validate! {e} | {e.args}\n")
    finally:
        pass


# checks if the passed ip address is in the validation list
def isValidationPending(address):
    return address in VALIDATION_PENDING_ADRESSES

# validates  
def finalizeValidation(address):
    if address in VALIDATION_PENDING_ADRESSES:
        VALIDATION_PENDING_ADRESSES.remove(address)
    VALIDATION_PENDING_ADRESSES.remove(address)
    KNOWN_CREDENTIALS.append(address)
    print(f"\nValidation finalized for {address}!")
    logging.info(f"| VALIDATION FINALIZED | {address}")
