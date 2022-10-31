import socket


HOST = "192.168.56.1" # LOCAL
#HOST = "143.244.205.206"  # MINE
#HOST = "144.126.247.134" #JAN
PORT = 18018  # The port used by the server

CLIENTS_NUMBER = 5000
DATA_SIZE = 2048 # size of data to read from each received message
KNOWN_CREDENTIALS = [] # stores all the addresses this node knows
ADDRESSES_FILE = 'known_credentials.json' # file that stores the known addresses
#SYSTEM = platform.system().lower() # our operating system


host = HOST
port = PORT

ClientMultiSocket = socket.socket()
#host = '127.0.0.1'
#port = 2004

print('Waiting for connection response')
try:
    ClientMultiSocket.connect((host, port))
except socket.error as e:
    print(str(e))
res = ClientMultiSocket.recv(DATA_SIZE)
while True:
    Input = input('Hey there: ')
    ClientMultiSocket.send(str.encode(Input))
    res = ClientMultiSocket.recv(DATA_SIZE)
    print(res.decode('utf-8'))
ClientMultiSocket.close()