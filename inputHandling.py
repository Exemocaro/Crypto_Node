import logging
import json

from config import *
from generateMessage import *
from client import *

def handleInput(connection, sender_address, data):
    try:
        data_parsed = json.loads(str(data, encoding="utf-8"))
        print("Data parsed: ", data_parsed)
        if "type" in data_parsed:
            if data_parsed["type"] == "hello":
                print("Hello received")
                return handleHello(data_parsed, sender_address)
            elif data_parsed["type"] == "getPeers":
                print("GetPeers received")
                return handleGetPeers(data_parsed, sender_address)
            elif data_parsed["type"] == "peers":
                print("Peers received")
                return handlePeers(data_parsed, sender_address)
            else:
                print("Error received")
                return handleError(data, sender_address)
        else:
            return generateErrorMessage("Type invalid or not supported!")
    except Exception as e:
        logging.error(f"| ERROR | {sender_address} | HANDLEINPUT | {data} | {e} | {e.args}")
        print(f"\nError on handleInput! {e} | {e.args}\n")
        return generateErrorMessage("invalid json")
    finally:
        pass

def handleHello(data_parsed, sender_address):
    try:
        if "version" in data_parsed:
            if data_parsed["version"][:4] == "0.8.":
                if isValidationPending(sender_address):
                    print(f"\nValidating {sender_address}\n")
                    finalizeValidation(sender_address)
                    print("\nValidation finished!\n")
                else:
                    print("Just answering hello")
                    return generateHelloMessage()
            else:
                logging.error(f"| ERROR | {sender_address} | HELLO | {data_parsed} | Version not supported | {data_parsed['version'][:4]}")
                return generateErrorMessage("Wrong hello version!")
        else:
            logging.error(f"| ERROR | {sender_address} | HELLO | {data_parsed} | No version in data_parsed")
            return generateErrorMessage("No version in hello!")
    except Exception as e:
        logging.error(f"| ERROR | {sender_address} | HELLO | {data_parsed} | {e} | {e.args}")
        print(f"\nError on hello! {e} | {e.args}\n")
    finally:
        pass

def handleGetPeers(data_parsed, sender_address):
    try:
        response = generatePeersMessage(KNOWN_CREDENTIALS)
        return response
    except Exception as e:
        logging.error(f"| ERROR | {sender_address} | GETPEERS | {data_parsed} | {e} | {e.args}")
        print(f"\nError on getPeers! {e} | {e.args}\n")
    finally:
        pass

def handlePeers(data_parsed, sender_address):
    try:
        if "peers" in data_parsed:
            #for peer in data_parsed["peers"]:
            peers = data_parsed["peers"]
                
            for credential_string in peers:
                peer = (credential_string.split(":")[0], int(credential_string.split(":")[1]))
                if not checkCredentials(peer):
                    print(f"\nValidating {peer}\n")
                    validateNode(peer)
                else:
                    print(f"\n{peer} already known!\n")
        else:
            logging.error(f"| ERROR | {sender_address} | PEERS | {data_parsed} | No peers in data_parsed")
            return generateErrorMessage("No peers in data_parsed!")
    except Exception as e:
        logging.error(f"| ERROR | {sender_address} | PEERS | {data_parsed} | {e} | {e.args}")
        print(f"\nError on peers! {e} | {e.args}\n")
    finally:
        pass

def handleError(data_parsed, sender_address):
    try:
        logging.error(f"| ERROR | {sender_address} | ERROR | {data_parsed} | Error message received")
        print(f"\nError message received!\n")
        return generateErrorMessage("Error message received")
    except Exception as e:
        logging.error(f"| ERROR | {sender_address} | ERROR | {data_parsed} | Error on Error: {e} | {e.args}")
        print(f"\nError on error! {e} | {e.args}\n")
        return generateErrorMessage("Error in error!")
    finally:
        pass
