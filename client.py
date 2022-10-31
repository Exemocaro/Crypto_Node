import socket
import json
import logging

from config import *
from generateMessage import *

def validateNode(credentials):
    try:
        print(f"\nValidating {credentials}\n")
        client_socket = socket.socket()
        client_socket.connect(credentials)
        data_to_send = generateHelloMessage()
        client_socket.sendall(data_to_send)
        VALIDATION_PENDING_ADRESSES.append(credentials["ip"])
    except Exception as e:
        print(f"\nError validating node! {e} | {e.args}\n")
        logging.info(f"| ERROR | Error validating node! | {e} | {e.args}")
    finally:
        pass




def connectToServer(address):
    try:
        clientSocket = socket.socket()
        clientSocket.connect(address)
        return clientSocket
    except Exception as e:
        print(f"Error on connectToServer! {e} | {e.args}")
        return None
    finally:
        pass

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