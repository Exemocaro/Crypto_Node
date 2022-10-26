from http import client
import socket
import logging
import threading
import json

from config import *
from responses import *

# will process the data we receive and send back some message or something
def process(connection, client_address, data):
    try:
        data_parsed = json.loads(str(data, encoding="utf-8"))

        # run function with name 
        function_name = data_parsed["type"]

        # if the function exists
        if function_name in ["hello", "getPeers", "peers", "error"]:
            if function_name == "error":
                print(f"\nError parsing json.")
                logging.info(f"| ERROR | {function_name} | Received an error message, somethin probably went wrong")
            else:
                eval(function_name + "(connection, client_address, data)")
        else:
            print(f"\nError parsing json.")
            logging.info(f"| ERROR | {function_name} | Wrong message type or type not yet supported")
            error(connection, client_address, data)

    except Exception as e:
        print(f"\nError parsing json.")
        logging.info(f"| ERROR | Error parsing json. | {e} | {e.args}")
        error(connection, client_address, data)

# main
def main():
    loadAddresses()

    # to store the message's id
    data_id = 0

    # Create a TCP/IP socket
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

    # Bind the socket to the port
    server_address = ('', PORT) # '' means that it will listen to every message from this port

    #sys.stderr
    print('Starting up on %s port %s' % server_address)
    sock.bind(server_address)

    # Listen for incoming connections
    sock.listen(400)

    # so it works within the error thing
    data = None

    while True:
        # Wait for a connection
        print('\nWaiting for a connection...\n')
        connection, client_address = sock.accept()

        try:
            print('---------- Connection from', client_address, " ----------")

            checkAddresses(client_address)

            # Receive the data in small chunks and retransmit it
            while True:
                data = connection.recv(DATA_SIZE)
                data_string = str(data, encoding="utf-8") # converting from binary to string
                if data:
                    print("\nID: ", data_id)
                    print('Received: \n"%s"' % data)
                    logging.info(f"| RECEIVED | {data_id} | {client_address} | {data}") # saving what we got
                    data_id += 1

                    # runs the function process in a new thread, as to not stop the loop
                    threading.Thread(target=process,args=(connection, client_address, data)).start()
                else:
                    print('\nNo more data from ', client_address)
                    break

        except Exception as e: # to catch errors in case something goes really bad
            print("Error! Message with id: %d", data_id)
            logging.error(f"| ERROR | {client_address} | {data_id} | {data} | {e} | {e.args}") # saving what we got
                
        finally: # closes the connection
            connection.close()

if __name__ == "__main__":
    main()
