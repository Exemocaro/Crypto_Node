from multiprocessing.connection import wait
import socket
import json

#HOST = "192.168.56.1" # LOCAL
#HOST = "143.244.205.206"  #MATEUS
#HOST = "144.126.247.134" #JAN
HOST = "127.0.0.1" #LOCALHOST


PORT = 18018  # The port used by the server

CLIENTS_NUMBER = 5000
DATA_SIZE = 2048 # size of data to read from each received message
KNOWN_ADDRESSES = [] # stores all the addresses this node knows
ADDRESSES_FILE = 'known_addresses.txt' # file that stores the known addresses
#SYSTEM = platform.system().lower() # our operating system

host = HOST
port = PORT

ClientMultiSocket = socket.socket()
#host = '127.0.0.1'
#port = 2004

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
        Input = json.dumps({"type": "hello", "version": "0.8.0" ,"agent " : "Kerma-Core Client 0.8"})
    
    elif Input == "peers":
        Input = json.dumps({"type": "peers", "peers": ["144.126.247.134:18018"]})
        waitForResponse = False

    elif Input == "getPeers":
        Input = json.dumps({"type": "getPeers"})
        
    ClientMultiSocket.send(str.encode(Input))
    if waitForResponse:
        res = ClientMultiSocket.recv(DATA_SIZE)
        print(res.decode('utf-8'))
    print("done.")
ClientMultiSocket.close()