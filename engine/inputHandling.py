import logging
import json

from config import *
from engine.generateMessage import *
from utility.credentials_utility import *
from database.KnownNodesHandler import *
from utility.logplus import *


# This is called when a message is received
# It calls the appropriate function based on the type of the message
# It returns the response (as byte-like data) to be sent back to the sender
# If no response is needed, it returns None
# If the message is not valid, it returns an error message
def handle_input(data, sender_address):
    try:
        data_parsed = json.loads(str(data, encoding="utf-8"))
        print("Data parsed: ", data_parsed)

        if "type" in data_parsed:
            message_type = data_parsed["type"]
            if type in ["hello", "getpeers", "peers", "error"]:
                function_name = data_parsed["type"]
                return eval("handle_" + function_name + "(data_parsed, sender_address)")
            else:
                LogPlus.warning(f"| WARNING | {sender_address} | HANDLEINPUT | {data} | Invalid type | {message_type}")
                return MessageGenerator.generate_error_message("Type \"" + message_type + "\"invalid or not supported!")
        else:
            LogPlus.warning(f"| WARNING | {sender_address} | HANDLEINPUT | {data} | No type in message")
            return MessageGenerator.generate_error_message("No type in message!")
    except Exception as e:
        LogPlus.error(f"| ERROR | {sender_address} | HANDLEINPUT | {data} | {e} | {e.args}")
        return MessageGenerator.generate_error_message("Invalid json.")


# This is called when a hello message is received
def handle_hello(data_parsed, sender_address):
    if "version" in data_parsed:
        if data_parsed["version"][:4] == "0.8.":
            return MessageGenerator.generate_hello_message()
        else:
            LogPlus.warning(f"| WARNING | {sender_address} | HELLO | {data_parsed} | Version not supported | {data_parsed['version'][:4]}")
            return MessageGenerator.generate_error_message("Wrong hello version!")
    else:
        LogPlus.error(f"| ERROR | {sender_address} | HELLO | {data_parsed} | No version in data_parsed")
        return MessageGenerator.generate_error_message("No version in hello!")


# This is called when a getpeers message is received
def handle_getpeers(data_parsed, sender_address):
    peers_db = KnownNodesHandler()
    peers = peers_db.known_nodes
    response = MessageGenerator.generate_peers_message(peers)
    return response


# This in called when a peers message is received
def handle_peers(data_parsed, sender_address):
    if "peers" in data_parsed:
        for credential_string in data_parsed["peers"]:
            peers_db = KnownNodesHandler()

            if not peers_db.is_known(credential_string):
                peers_db.add_node(credential_string)
                LogPlus.info(f"| INFO | {sender_address} | PEERS | {data_parsed} | New peer added | {credential_string}")
    else:
        LogPlus.error(f"| ERROR | {sender_address} | PEERS | {data_parsed} | No peers in data_parsed")
        return MessageGenerator.generate_error_message("No peers in data_parsed!")


# This is called when an error message is received
def handle_error(data_parsed, sender_address):
    LogPlus.error(f"| ERROR | {sender_address} | ERROR | {data_parsed} | Error message received")
    return MessageGenerator.generate_error_message("Error message received")
