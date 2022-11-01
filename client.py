import socket
import json

from config import *

#HOST = "192.168.56.1" # LOCAL
#HOST = "143.244.205.206"  # MATEUS
#HOST = "4.231.16.23" # JAN
#HOST = "139.59.205.101" # SIMÃO
#HOST = "128.130.122.101" # bootstrapping node
HOST = "127.0.0.1" # localhost
#HOST = "134.122.88.104" # RANDOM PERSON 1 

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

# sending hello

output = json.dumps({"type": "hello", "version": "0.8.0", "agent ": "Kerma-Core Client 0.8"})
output += "\n"
output = str.encode(str(output))
ClientMultiSocket.send(output)

res = ClientMultiSocket.recv(DATA_SIZE)
print(res.decode('utf-8'))

while True:
    waitForResponse = True  
    Input = input('Hey there: ')
    if Input == "hello":
        output = json.dumps({"type": "hello", "version": "0.8.0" ,"agent " : "Kerma-Core Client 0.8"})
        output += "\n"
    
    elif Input == "peers":
        loadAddresses()
        #loadAddressesWithPorts()
        output = json.dumps({"type": "peers", "peers": KNOWN_CREDENTIALS})
        output += "\n"
        waitForResponse = False

    elif Input.lower() == "getpeers":
        output = json.dumps({"type": "getpeers"})
        output += "\n"

    elif Input == "doublemessage":
        output = json.dumps({"type": "hello", "version": "0.8.0" ,"agent " : "Kerma-Core Client 0.8"}) + "\n" + \
                json.dumps({"type": "getpeers"})
        output += "\n"
    elif Input == "splitA": # send only the first part of the message
        output = '{"type": "hello", "version": "0.8'
        waitForResponse = False
    elif Input == "splitB": # send only the second part of the message
        output = '.0" ,"agent " : "Kerma-Core Client 0.8"}\n'
        
    ClientMultiSocket.send(str.encode(output))
    if waitForResponse:
        res = ClientMultiSocket.recv(DATA_SIZE)
        print(res.decode('utf-8'))
ClientMultiSocket.close()
