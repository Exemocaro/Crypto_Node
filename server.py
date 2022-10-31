import socket
import logging
#import threading
import json

from _thread import *
from tracemalloc import start # new threading lib
from config import *
from responses import *

# will process the data we receive and send back some message or something
def multi_threaded_client(connection, client_address):
    connection.send(str.encode('Server is working:'))
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
            data_parsed = json.loads(str(data, encoding="utf-8"))

            # run function with name 
            function_name = data_parsed["type"]

            # if the function exists
            if function_name in ["hello", "getPeers", "peers", "error"]:
                if function_name == "error":
                    print(f"\nReceived error message.")
                    logging.info(f"| ERROR | {function_name} | Received an error message, something probably went wrong")
                else:
                    eval(function_name + "(connection, client_address, data)") #runs the functions with the type name
            else:
                print(f"\nError unknown type.")
                logging.info(f"| ERROR | {function_name} | Wrong message type or type not yet supported")
                error(connection, client_address, data, "Wrong message type or type not yet supported")

        except Exception as e:
            print(f"\nError parsing json.")
            logging.info(f"| ERROR | Error parsing json. | {e} | {e.args}")
            error(connection, client_address, data, "Error parsing json")

    connection.close()

# I <3 you copilot for this one :), still hate you though
# ughh this is so ugly but it works for now 
# Mateus is working on a better solution
def startSocket():
    serverSideSocket = socket.socket()
    serverSideSocket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    threadCount = 0 # stores the number of total threads opened by the server

    try:
        serverSideSocket.bind(SERVER_ADDRESS)
        #serverSideSocket.bind((HOST, PORT))
    except socket.error as e:
        logging.error(f"| ERROR | {client_address} | {e} | {e.args} | Error when binding the socket to the server address")
        print(str(e))

    print('Starting up on %s port %s' % SERVER_ADDRESS)
    
    serverSideSocket.listen(CLIENTS_NUMBER)

    while True:
        print('\nWaiting for a connection...\n')
        connection, client_address = serverSideSocket.accept()

        try:
            ip = client_address[0]
            port = str(client_address[1])
            client_address = str(ip + ":" + port)
            checkAddresses(client_address)
            
            print('---------- Connection from', client_address, " ----------")
            start_new_thread(multi_threaded_client, (connection, client_address))
            threadCount += 1
            print('Thread Number: ' + str(threadCount))
        except Exception as e: # to catch errors in case something goes really bad
            logging.error(f"| ERROR | {client_address} | {e} | {e.args}")
    
    serverSideSocket.close()
    
# main
def main():
    loadAddresses()
    startSocket()

if __name__ == "__main__":
    main()
