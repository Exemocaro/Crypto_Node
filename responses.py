import socket
import logging
import json
import sys

from config import *

def hello(connection, client_address, data):
    try:
        data_parsed = json.loads(str(data, encoding="utf-8"))

        if "version" in data_parsed:
            if data_parsed["version"][:4] != "0.8.":
                logging.error(f"| ERROR | {client_address} | HELLO | {data} | Version not supported")
                print(f"\nWrong hello version!\n")
                error(connection, client_address, data)
            else:
                data_to_send = b'{"type": "hello", "version": "0.8.0" ,"agent " : "Kerma-Core Client 0.8"}\n'

                print(f"\nSending data: \n{data_to_send}")
                #data_string = str(data, encoding="utf-8")

                connection.sendall(data_to_send) # we can't send str(data) because it must be a "byte-like object"
                logging.info(f"| SENT | {client_address} | {data}")
    except Exception as e:
        logging.error(f"| ERROR | {client_address} | HELLO | {data} | {e} | {e.args}")
        print(f"\nError on hello! {e} | {e.args}\n")
        error(connection, client_address, data)
    finally:
        pass
        
def getPeers(connection, client_address, data):
    try:
        data_to_send = json.dumps({"type": "peers", "peers": KNOWN_ADDRESSES})
        data_to_send = str.encode(str(data_to_send + "\n"))

        #data_to_send = b'{"type " : " peers " ,"peers " : }'

        print(f"\nSending data: \n{data_to_send}")
        data_string = str(data, encoding="utf-8")

        connection.sendall(data_to_send) # we can't send str(data) because it must be a "byte-like object"
        logging.info(f"| SENT | {client_address} | {data_string}")
    except Exception as e:
        logging.error(f"| ERROR | {client_address} | GETPEERS | {data_string} | {e} | {e.args}")
        print(f"\nError on getPeers! {e} | {e.args}\n")
        error(connection, client_address, data)
    finally:
        pass

def peers(connection, client_address, data):
    try:
        data_parsed = json.loads(str(data, encoding="utf-8"))

        if "peers" in data_parsed:
            nPeers = len(data_parsed["peers"])
            if nPeers > 0: # might be empty, we don't know
                for peer in data_parsed["peers"]:
                    checkAddresses(peer)
                print(f"\nChecked {nPeers} new peers!\n")
            else:
                logging.error(f"| ERROR | {client_address} | PEERS | {data} | Received empty peers list!")

    except Exception as e:
        logging.error(f"| ERROR | {client_address} | PEERS | {data} | {e} | {e.args}")
        print(f"\nError on peers! {e} | {e.args}\n")
        error(connection, client_address, data)
    finally:
        pass

def error(connection, client_address, data, message="Wrong hello version type!"):
    try:
        data_to_send = json.dumps({"type " : " error " , "error " : message})
        data_to_send = str.encode(str(data_to_send + "\n"))

        print(f"\nSending data: \n{data_to_send}")
        #data_string = str(data, encoding="utf-8")

        connection.sendall(data_to_send) # we can't send str(data) because it must be a "byte-like object"
        logging.info(f"| SENT | {client_address} | {data}")
    except Exception as e:
        logging.error(f"| ERROR | {client_address} | ERROR | {data} | {e} | {e.args}")
        print(f"\nError on error! {e} | {e.args}\n")
        #error(connection, client_address, data)
    finally:
        pass
