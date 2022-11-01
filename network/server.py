#import threading

from _thread import *
#from responses import *
from engine.inputHandling import *
from database.KnownPeerHandler import *
from engine.generateMessage import *


# has to run first when we connect to a peer
def hello_protocol(connection, client_address):
    try:
        connection.sendall(generate_hello_message())
        connection.sendall(generate_getpeers_message())
        logging.info(f"| SENT | {client_address} | HELLO | GETPEERS")
        print("Sent HELLO and GETPEERS")
    except Exception as e:
        logging.error(f"| ERROR | {client_address} | {e} | {e.args} | Error when sending hello and getpeers messages")
        print("Error when sending hello and getpeers messages")
        return False
    finally:
        return True


# will process the data we receive and send back some message or something
def multi_threaded_client(connection, client_address):

    # hello protocol
    if not hello_protocol(connection, client_address):
        print("Protocol failed, closing connection")
        connection.close()
        return

    # buffer to store the data we receive
    buffer = b''

    # listen for messages from the client and process them
    while True:
        data = connection.recv(DATA_SIZE)
        if not data:
            break
        data_str = data.decode("utf-8")
        print("Received data: ", data_str)

        buffer += data

        if b'\n' in buffer:
            lines = buffer.split(b'\n')
            buffer = lines.pop()
            for line in lines:
                if line == b'':
                    continue
                print('Received: \n"%s"' % line)
                logging.info(f"| RECEIVED | {client_address} | {line}")

                # get the appropriate response
                response = handle_input(line, client_address)

                if response != "":
                    try:
                        connection.sendall(response)
                        logging.info(f"| SENT | {client_address} | {response}")
                    except Exception as e:
                        print(f"\nError sending response.")
                        logging.error(f"| ERROR | Error sending response. | {e} | {e.args}")




    connection.close()

# I <3 you copilot for this one :), still hate you though
# ughh this is so ugly but it works for now 
# Mateus is working on a better solution
def startSocket():
    serverSideSocket = socket.socket()
    serverSideSocket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1) # this is to avoid the "address already in use" error
    threadCount = 0 # stores the number of total threads opened by the server

    try:
        serverSideSocket.bind(SERVER_ADDRESS)
        #serverSideSocket.bind((HOST, PORT))
    except socket.error as e:
        logging.error(f"| ERROR | {e} | {e.args} | Error when binding the socket to the server address")
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
            #checkAndAddAddresses(client_address)
            
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
