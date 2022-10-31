import socket
import json

from config import *

host = HOST
port = PORT

ClientMultiSocket = socket.socket()

print('Waiting for connection response')
try:
    ClientMultiSocket.connect((host, port))
except socket.error as e:
    print(str(e))
res = ClientMultiSocket.recv(DATA_SIZE)

while True:
    waitForResponse = True  
    Input = input('Hey there: ')
    if Input == "hello":
        Input = json.dumps({"type": "hello", "version": "0.8.0" ,"agent " : "Kerma-Core Client 0.8"})
    
    elif Input == "peers":
        loadAddresses()
        Input = json.dumps({"type": "peers", "peers": KNOWN_ADDRESSES})
        waitForResponse = False

    elif Input == "getPeers":
        Input = json.dumps({"type": "getPeers"})
        
    ClientMultiSocket.send(str.encode(Input))
    if waitForResponse:
        res = ClientMultiSocket.recv(DATA_SIZE)
    print(res.decode('utf-8'))
ClientMultiSocket.close()
