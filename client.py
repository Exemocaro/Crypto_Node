import socket
import sys

from config import *

# Create a TCP/IP socket
sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

# Connect the socket to the port where the server is listening
#server_address = ('localhost', 10000)
server_address = (HOST, PORT)

print('\nConnecting to %s port %s' % server_address)
sock.connect(server_address)

try:
    # Send data
    # '{"type": "hello", "version": "0.8.0" ,"agent " : "Kerma-Core Client 0.8"}'
    
    message_string = json.dumps({"type": "peers", "peers": KNOWN_ADDRESSES})
    message = str.encode(str(message_string + "\n"))
    
    #message = b'{"type": "hello", "version": "0.8.0" ,"agent " : "Kerma-Core Client 0.8"}'
    #message_string = str(message, encoding="utf-8") # converting from binary to string
    
    print('\nSending: \n"%s"' % message_string)
    sock.sendall(message)

    #sock.setblocking(False) # IMPORTANT
    
    data = str()
    data_string = str()

    try:
        sock.settimeout(1) # time to wait for answer. if we don't get it in x secs, we close the connection
        data = sock.recv(DATA_SIZE)
        data_string = str(data, encoding="utf-8")
    except Exception as e:
        print("\nConnection timed out!")


    # Look for the response
    amount_received = 0
    amount_expected = len(data_string)
    
    """ while amount_received < amount_expected:
        #print("Length of data: ", len(data_string))
        amount_received += len(data_string)
        print('\nReceived: \n"%s"' % data_string)
        print("received:", amount_received, "| expected:", amount_expected) """

finally:
    print('\nClosing socket\n')
    sock.close()
