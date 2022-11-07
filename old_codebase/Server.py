from engine.inputHandling import *
from database.KnownNodesHandler import *
from engine.generateMessage import *
from utility.credentials_utility import *

from threading import Thread


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

                send_response(client_address, connection, response)

    connection.close()


def send_response(client_address, connection, response):
    if response != "":
        try:
            connection.sendall(response)
            logging.info(f"| SENT | {client_address} | {response}")
        except Exception as e:
            print(f"\nError sending response.")
            logging.error(f"| ERROR | Error sending response. | {e} | {e.args}")


# refactoring the functions above into a class
class Server:
    def __init__(self, port):
        self.port = port
        self.isRunning = False
        self.socket = None
        self.thread_count = 0
        self.threads = []

    def start(self):
        self.socket = socket.socket()
        self.socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)  # to avoid "address already in use" error

        print('Starting up on port %s' % self.port)
        try:
            self.socket.bind(('', self.port))
        except socket.error as e:
            logging.error(f"| ERROR | {e} | {e.args} | Error when binding the socket to the server address")
            print(str(e))

        self.socket.listen(CLIENTS_NUMBER)
        while True:
            self.accept_connections()

    def accept_connections(self):
        print('\nWaiting for a connection...\n')
        connection, client_address = self.socket.accept()
        client_address = convert_tuple_to_string(client_address)
        # checkAndAddAddresses(client_address)

        print('---------- Connection from', client_address, " ----------")

        try:
            # start_new_thread(multi_threaded_client, (connection, client_address))
            thread = Thread(target=multi_threaded_client, args=(connection, client_address)).start()
            self.thread_count += 1
            self.threads.append(thread)
            print('Thread Number: ' + str(self.thread_count))
        except Exception as e:
            logging.error(f"| ERROR | Starting a new thread failed | {client_address} | {e} | {e.args}")
            print("Error: unable to start thread")

        self.thread_count += 1
        logging.info(f"| NEW THREAD | {client_address} | {self.thread_count}")
        print('Thread Number: ' + str(self.thread_count))

    def stop(self):
        self.isRunning = False
        self.socket.close()
        logging.info(f"| STOPPED | Server stopped")
