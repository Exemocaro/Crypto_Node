from http import client
import socket
import logging
#import threading
import json

from _thread import *
from config import *
from inputHandling import *

# will process the data we receive and send back some message or something
def multi_threaded_client(connection, client_address):
    #connection.send(str.encode('Server is working:'))
    while True:
        data = connection.recv(DATA_SIZE)
        data_string = str(data, encoding="utf-8") # converting from binary to string
        response = 'Server message: ' + data.decode('utf-8')
        if not data:
            break

        print('Received: \n"%s"' % data)
        logging.info(f"| RECEIVED | {client_address} | {data}")

        # process the data into a json file and send back the appropriate response
        try:
            response = handleInput(connection, client_address, data)
            print(response)
            if response != None:
                connection.sendall(str.encode(response))
        except Exception as e:
            print(f"\nError parsing json.")
            logging.info(f"| ERROR | Error parsing json. | {e} | {e.args}")
            #handleError() # TODO
            #error(connection, client_address, data, "Error parsing json")

    connection.close()

# I <3 you copilot for this one :) (still hate you though)
# ughh this is so ugly but it works for now 
# Mateus is working on a better solution
def startSocket():
    serverSideSocket = socket.socket()
    # prevent glow down after closing the program
    serverSideSocket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)

    threadCount = 0 # stores the number of total threads opened by the server

    try:
        serverSideSocket.bind(SERVER_ADDRESS)
        #serverSideSocket.bind((HOST, PORT))
    except socket.error as e:
        logging.error(f"| ERROR | {SERVER_ADDRESS} | {e} | {e.args} | Error when binding the socket to the server address")
        print(str(e))

    print('Starting up on %s port %s' % SERVER_ADDRESS)
    
    serverSideSocket.listen(CLIENTS_NUMBER)

    while True:
        print('\nWaiting for a connection...\n')
        connection, client_address = serverSideSocket.accept()

        try:
            print('---------- Connection from', client_address, " ----------")
            #checkAddresses(client_address)
            
            start_new_thread(multi_threaded_client, (connection, client_address))
            threadCount += 1
            print('Thread Number: ' + str(threadCount))
        except Exception as e: # to catch errors in case something goes really bad
            logging.error(f"| ERROR | {client_address} | {e} | {e.args}")
    
    serverSideSocket.close()


def main():
    loadAddresses()
    startSocket()

if __name__ == "__main__":
    main()
