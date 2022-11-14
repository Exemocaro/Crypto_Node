import socket
import json

from config import *
from engine.generateMessage import *

# HOST = "192.168.56.1" # LOCAL
HOST = "143.244.205.206"  # MATEUS
# HOST = "4.231.16.23"  # JAN
# HOST = "128.130.122.101" # bootstrapping node
# HOST = "127.0.0.1" # localhost

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
    
client_socket = socket.socket()

print('Waiting for connection response: ' + host)
try:
    client_socket.connect((host, port))
except socket.error as e:
    print(str(e))

print("Connected to " + host + ":" + str(port))

# send hello message to verify connection
hello_message = MessageGenerator.generate_hello_message()
client_socket.send(hello_message)
print("Sent hello message")


def get_input():
    input_data = input('Hey there: ')
    if input_data == "hello":
        print("Sending hello")
        input_data = MessageGenerator.generate_hello_message()

    elif input_data == "peers":
        input_data = json.dumps({"type": "peers", "peers": ["128.130.122.101:18018"]})

    elif input_data.lower() == "getpeers":
        input_data = MessageGenerator.generate_getpeers_message().decode("utf-8")
        print("Sending" + input_data)

    if input_data != "":
        input_data = str(input_data) + "\n"
    return str(input_data)


client_socket.setblocking(False)

while True:
    message = get_input()
    print("message: " + str(message))
    client_socket.send(message.encode("utf-8"))
    print("Sent message")

    try:
        res = client_socket.recv(DATA_SIZE)
        print('"' + res.decode('utf-8') + '"')
    except socket.error as e:
        res = "It's okay, just nothing to receive"

