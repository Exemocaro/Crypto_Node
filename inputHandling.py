import logging
import json

from config import *

def handleInput(data, sender_address):
    try:
        data_parsed = json.loads(str(data, encoding="utf-8"))
        if "type" in data_parsed:
            if data_parsed["type"] == "hello":
                return handleHello(data_parsed, sender_address)
            elif data_parsed["type"] == "getPeers":
                return handleGetPeers(data_parsed, sender_address)
            elif data_parsed["type"] == "peers":
                return handlePeers(data_parsed, sender_address)
            else:
                return handleError(data, sender_address)
        else:
            return json.loads("{'type': 'error', 'error': 'No type!'}")
    except Exception as e:
        logging.error(f"| ERROR | {sender_address} | HANDLEINPUT | {data} | {e} | {e.args}")
        print(f"\nError on handleInput! {e} | {e.args}\n")
    finally:
        pass

def handleHello(data_parsed, sender_address):
    try:
        if "version" in data_parsed:
            if data_parsed["version"][:4] == "0.8":
                if isValidationPending(sender_address):
                    finanlizeValidation(sender_address)
                else:
                    return json.loads("{'type': 'hello', 'version': '0.8.0', 'agent': 'Kerma-Core Client 0.8'}")
            else:
                return json.loads("{'type': 'error', 'error': 'Wrong hello version type!'}")
        else:
            return json.loads("{'type': 'error', 'error': 'No version type!'}")
    except Exception as e:
        logging.error(f"| ERROR | {sender_address} | HELLO | {data_parsed} | {e} | {e.args}")
        print(f"\nError on hello! {e} | {e.args}\n")
    finally:
        pass

def handleGetPeers(data_parsed, sender_address):
    try:
        response = json.dumps({"type": "peers", "peers": KNOWN_ADDRESSES})
        return response
    except Exception as e:
        logging.error(f"| ERROR | {sender_address} | GETPEERS | {data_parsed} | {e} | {e.args}")
        print(f"\nError on getPeers! {e} | {e.args}\n")
    finally:
        pass

def handlePeers(data_parsed, sender_address):
    try:
        if "peers" in data_parsed:
            for peer in data_parsed["peers"]:
                if not checkAddress(peer):
                    print(f"\nValidating {peer}\n")
                    client_adress = (peer.split(":")[0], int(peer.split(":")[1]))
                    validateAdress(client_adress)
                else:
                    print(f"\n{peer} already known!\n")
        else:
            logging.error(f"| ERROR | {sender_address} | PEERS | {data_parsed} | No peers in data_parsed")
            return json.loads("{'type': 'error', 'error': 'No peers type!'}")
    except Exception as e:
        logging.error(f"| ERROR | {sender_address} | PEERS | {data_parsed} | {e} | {e.args}")
        print(f"\nError on peers! {e} | {e.args}\n")
    finally:
        pass

def handleError(data_parsed, sender_address):
    try:
        logging.error(f"| ERROR | {sender_address} | ERROR | {data_parsed} | Error message received")
        print(f"\nError message received!\n")
    except Exception as e:
        logging.error(f"| ERROR | {sender_address} | ERROR | {data_parsed} | Error on Error: {e} | {e.args}")
        print(f"\nError on error! {e} | {e.args}\n")
    finally:
        pass
