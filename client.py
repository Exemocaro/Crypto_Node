import socket
import json

from config import *

#HOST = "192.168.56.1" # LOCAL
#HOST = "143.244.205.206"  # MATEUS
#HOST = "144.126.247.134" # JAN
#HOST = "139.59.205.101" # SIMÃO
#HOST = "128.130.122.101" # bootstrapping node
HOST = "127.0.0.1" # localhost

host = HOST
port = PORT

""" 
CREDENTIALS = []

# loads the addresses from the file into the list of addresses
def loadAddressesWithPorts():
    with open(ADDRESSES_FILE, 'r') as f:
        addresses_unparsed = f.readlines()
        temp = [x.strip("\n") for x in addresses_unparsed] # to remove whitespace characters like `\n` at the end of each line
        for a in temp:
            if a not in CREDENTIALS:
                CREDENTIALS.append(a)
        size = len(CREDENTIALS)
"""
    
ClientMultiSocket = socket.socket()

print('Waiting for connection response')
try:
    ClientMultiSocket.connect((host, port))
except socket.error as e:
    print(str(e))
res = ClientMultiSocket.recv(DATA_SIZE)
print("First received: " + str(res))
res = ClientMultiSocket.recv(DATA_SIZE)
print("First received: " + str(res))


while True:
    waitForResponse = True  
    Input = input('Hey there: ')
    if Input == "hello":
        Input = json.dumps({"type": "hello", "version": "0.8.0" ,"agent " : "Kerma-Core Client 0.8"})
    
    elif Input == "peers":
        loadAddresses()
        #loadAddressesWithPorts()
        Input = json.dumps({"type": "peers", "peers": KNOWN_CREDENTIALS})
        waitForResponse = False

    elif Input.lower() == "getpeers":
        Input = json.dumps({"type": "getpeers"})

    elif Input.lower() == "doublemessage":
        Input = json.dumps({"type": "hello", "version": "0.8.0" ,"agent " : "Kerma-Core Client 0.8"}) + "\n" + \
                json.dumps({"type": "getpeers"})
        
    ClientMultiSocket.send(str.encode(Input))
    if waitForResponse:
        res = ClientMultiSocket.recv(DATA_SIZE)
    print(res.decode('utf-8'))
ClientMultiSocket.close()
