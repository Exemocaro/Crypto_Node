import socket
import json

from config import *

#HOST = "192.168.56.1" # LOCAL
#HOST = "143.244.205.206" #MATEUS
#HOST = "144.126.247.134" #JAN
#HOST = 139.59.205.101" #SIMÃO
HOST = "127.0.0.1"  # LOCALHOST

PORT = 18018  # The port used by the server

host = HOST
port = PORT

ClientMultiSocket = socket.socket()
# host = '127.0.0.1'
# port = 2004

print('Connecting to Server')
try:
    ClientMultiSocket.connect((host, port))
except socket.error as e:
    print(str(e))

print("Connected to Server")
while True:
    waitForResponse = True
    Input = input('Hey there: ')
    if Input == "hello":
        Input = json.dumps({"type": "hello", "version": "0.8.0", "agent ": "Kerma-Core Client 0.8"})

    elif Input == "peers":
        loadAddresses()
        Input = json.dumps({"type": "peers", "peers": "[143.244.205.206:18018]"})
        waitForResponse = False

    elif Input == "getPeers":
        Input = json.dumps({"type": "getPeers"})

    ClientMultiSocket.send(str.encode(Input))
    if waitForResponse:
        res = ClientMultiSocket.recv(DATA_SIZE)
        print(res.decode('utf-8'))
    print("done.")
ClientMultiSocket.close()
