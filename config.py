import platform
import logging
import json

HOST = "128.130.248.242" # LOCAL
#HOST = "143.244.205.206"  # MINE
#HOST = "144.126.247.134" #JAN
PORT = 18018  # The port used by the server

DATA_SIZE = 2048 # size of data to read from each received message
KNOWN_ADDRESSES = [] # stores all the addresses this node knows
ADDRESSES_FILE = 'known_addresses.txt' # file that stores the known addresses
SYSTEM = platform.system().lower() # our operating system

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
