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

        if "type" in data_parsed:
            message_type = data_parsed["type"]
            if message_type in ["hello", "getpeers", "peers", "error", "ihaveobject", "getobject", "object"]:
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
    peers = NODE_HANDLER.known_nodes
    response = MessageGenerator.generate_peers_message(peers)
    return response


# This in called when a peers message is received
def handle_peers(data_parsed, sender_address):
    if "peers" in data_parsed:
        for credential_string in data_parsed["peers"]:
            if not NODE_HANDLER.is_node_known(credential_string):
                NODE_HANDLER.add_node(credential_string)
                LogPlus.info(f"| INFO | {sender_address} | PEERS | {data_parsed} | New peer added | {credential_string}")
    else:
        LogPlus.error(f"| ERROR | {sender_address} | PEERS | {data_parsed} | No peers in data_parsed")
        return MessageGenerator.generate_error_message("No peers in data_parsed!")


# This is called when an error message is received
def handle_error(data_parsed, sender_address):
    LogPlus.error(f"| ERROR | {sender_address} | ERROR | {data_parsed} | Error message received")


# This is called when an ihaveobject message is received
def handle_ihaveobject(data_parsed, sender_adress):
    if "objectid" in data_parsed:
        if not OBJECT_HANDLER.is_object_known(data_parsed["objectid"]):
            LogPlus.info(f"| INFO | {sender_adress} | IHAVEOBJECT | {data_parsed} | New object requested | {data_parsed['objectid']}")
            return MessageGenerator.generate_getobject_message(data_parsed["objectid"])
        else:
            LogPlus.info(f"| INFO | {sender_adress} | IHAVEOBJECT | {data_parsed} | Object already known | {data_parsed['object']}")
    else:
        LogPlus.error(f"| ERROR | {sender_adress} | IHAVEOBJECT | {data_parsed} | No object in data_parsed")
        return MessageGenerator.generate_error_message("No objectid in ihaveobject")


# This is called when a getobject message is received
def handle_getobject(data_parsed, sender_adress):
    if "objectid" in data_parsed:
        if OBJECT_HANDLER.is_object_known(data_parsed["objectid"]):
            LogPlus.info(f"| INFO | {sender_adress} | GETOBJECT | {data_parsed} | Object requested | {data_parsed['objectid']}")
            return MessageGenerator.generate_object_message(OBJECT_HANDLER.get_object(data_parsed["objectid"]))
        else:
            LogPlus.info(f"| INFO | {sender_adress} | GETOBJECT | {data_parsed} | Object not known | {data_parsed['objectid']}")
            return MessageGenerator.generate_error_message("Object not known")
    else:
        LogPlus.error(f"| ERROR | {sender_adress} | GETOBJECT | {data_parsed} | No object in data_parsed")
        return MessageGenerator.generate_error_message("No objectid in getobject")


# This is called when an object message is received
def handle_object(data_parsed, sender_adress):
    if "object" in data_parsed:
        object_id = OBJECT_HANDLER.get_id(data_parsed["object"])
        if not OBJECT_HANDLER.is_object_known(object_id):
            LogPlus.info(f"| INFO | {sender_adress} | OBJECT | {data_parsed} | New object received | {object_id}")
            OBJECT_HANDLER.add_object(data_parsed["object"])
        else:
            LogPlus.info(f"| INFO | {sender_adress} | OBJECT | {data_parsed} | Object already known | {object_id}")
    else:
        LogPlus.error(f"| ERROR | {sender_adress} | OBJECT | {data_parsed} | No object in data_parsed")
        return MessageGenerator.generate_error_message("No object in object message")
