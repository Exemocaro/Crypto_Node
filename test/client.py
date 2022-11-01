import socket
import json

from config import *

#HOST = "192.168.56.1" # LOCAL
#HOST = "143.244.205.206"  # MATEUS
#HOST = "4.231.16.23" # JAN
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
        size = len(CREDENTIALS) """
    
ClientMultiSocket = socket.socket()

print('Waiting for connection response: ' + host)
try:
    ClientMultiSocket.connect((host, port))
except socket.error as e:
    print(str(e))

res = ClientMultiSocket.recv(DATA_SIZE)
print('"' + res.decode("utf-8") + '"')
res = ClientMultiSocket.recv(DATA_SIZE)
print('"' + res.decode("utf-8") + '"')

print("Connected to " + host + ":" + str(port))
while True:
    waitForResponse = True
    input_data = input('Hey there: ')
    if input_data == "hello":
        print("Sending hello")
        input_data = json.dumps({"type": "hello", "version": "0.8.0" , "agent " : "Kerma-Core Client 0.8"})
    
    elif input_data == "peers":
        loadAddresses()
        #loadAddressesWithPorts()
        input_data = json.dumps({"type": "peers", "peers": ["128.130.122.101:18018"]})
        waitForResponse = False

    elif input_data.lower() == "getpeers":
        input_data = json.dumps({"type": "getpeers"})
        
    ClientMultiSocket.send(str.encode(input_data + "\n"))
    if waitForResponse:
        res = ClientMultiSocket.recv(DATA_SIZE)
    print('"' + res.decode('utf-8') + '"')
ClientMultiSocket.close()
