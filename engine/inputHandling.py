import logging
import json

from utility.credentials_utility import *
from utility.logplus import *

from database.KnownNodesHandler import *
from database.ObjectHandler import *

from engine.Object import Object
from engine.generateMessage import MessageGenerator

from config import *

from engine.ObjectCreator import ObjectCreator


# This is called when a message is received
# It calls the appropriate function based on the type of the message
# It returns the response (as byte-like data) to be sent back to the sender
# If no response is needed, it returns None
# If the message is not valid, it returns an error message
def handle_input(data, sender_address):
    try:
        data_parsed = json.loads(str(data, encoding="utf-8"))
    except Exception as e:
        LogPlus.error(f"| ERROR | inputHandler | handle_input | {data} | {e} | {e.args}")
        return [(sender_address, MessageGenerator.generate_error_message("Invalid json."))]

    try:
        if "type" in data_parsed:
            message_type = data_parsed["type"]
            if message_type in ["hello", "getpeers", "peers", "error", "ihaveobject", "getobject", "object"]:
                function_name = data_parsed["type"]
                print("function name: ", function_name)
                response = globals()["handle_" + function_name](data_parsed, sender_address)
                print(response)
                return response
            else:
                LogPlus.warning(f"| WARNING | {sender_address} | HANDLEINPUT | {data} | Invalid type | {message_type}")
                return [(sender_address, MessageGenerator.generate_error_message("Type \"" + message_type + "\"invalid or not supported!"))]
        else:
            LogPlus.warning(f"| WARNING | {sender_address} | HANDLEINPUT | {data} | No type in message")
            return [(sender_address, MessageGenerator.generate_error_message("No type in message!"))]
    except Exception as e:
        LogPlus.error(f"| ERROR | inputHandling | handle_input | {data} | {sender_address} | {e}")
        return [(sender_address, MessageGenerator.generate_error_message("Unknown Error"))]


# This is called when a hello message is received
def handle_hello(data_parsed, sender_address):
    try:
        if "version" in data_parsed:
            if data_parsed["version"][:4] == "0.8.":
                return [(sender_address, MessageGenerator.generate_hello_message())]
            else:
                LogPlus.warning(f"| WARNING | {sender_address} | HELLO | {data_parsed} | Version not supported | {data_parsed['version'][:4]}")
                return [(sender_address, MessageGenerator.generate_error_message("Wrong hello version!"))]
        else:
            LogPlus.error(f"| ERROR | {sender_address} | HELLO | {data_parsed} | No version in data_parsed")
            return [(sender_address, MessageGenerator.generate_error_message("No version in hello!"))]
    except Exception as e:
        LogPlus.error(f"| ERROR | ObjectHandler | handle_hello | {data_parsed} | {sender_address} | {e}")
        return [(sender_address, MessageGenerator.generate_error_message("Unknown Error"))]


# This is called when a getpeers message is received
def handle_getpeers(data_parsed, sender_address):
    try:
        peers = KnownNodesHandler.known_nodes
        response = MessageGenerator.generate_peers_message(peers)
        return [(sender_address, response)]
    except Exception as e:
        LogPlus.error(f"| ERROR | ObjectHandler | handle_getpeers | {data_parsed} | {sender_address} | {e}")
        return [(sender_address, MessageGenerator.generate_error_message("Unknown Error"))]


# This in called when a peers message is received
def handle_peers(data_parsed, sender_address):
    try:
        if "peers" in data_parsed:
            for credential_string in data_parsed["peers"]:
                if not KnownNodesHandler.is_node_known(credential_string):
                    KnownNodesHandler.add_node(credential_string)
                    LogPlus.info(f"| INFO | {sender_address} | PEERS | {data_parsed} | New peer added | {credential_string}")
        else:
            LogPlus.error(f"| ERROR | {sender_address} | PEERS | {data_parsed} | No peers in data_parsed")
            return [(sender_address, MessageGenerator.generate_error_message("No peers in data_parsed!"))]
    except Exception as e:
        LogPlus.error(f"| ERROR | ObjectHandler | handle_peers | {data_parsed} | {sender_address} | {e}")
        return [(sender_address, MessageGenerator.generate_error_message("Unknown Error"))]


# This is called when an error message is received
def handle_error(data_parsed, sender_address):
    try:
        LogPlus.error(f"| ERROR | {sender_address} | ERROR | {data_parsed} | Error message received")
    except Exception as e:
        LogPlus.error(f"| ERROR | inputHandling | handle_error | {data_parsed} | {sender_address} | {e}")
        return [(sender_address, MessageGenerator.generate_error_message("Unknown Error"))]


# This is called when an ihaveobject message is received
def handle_ihaveobject(data_parsed, sender_address):
    try:
        if "object_id" in data_parsed:
            if not ObjectHandler.is_object_known(data_parsed["object_id"]):
                LogPlus.info(f"| INFO | inputHandling | handle_ihaveobject | New object requested | {data_parsed['object_id']}")
                return [(sender_address, MessageGenerator.generate_getobject_message(data_parsed["object_id"]))]
            else:
                LogPlus.info(f"| INFO | inputHandling | handle_ihaveobject | Object already known | {data_parsed['object_id']}")
                return []
        else:
            LogPlus.error(f"| ERROR | IHAVEOBJECT | No object in data_parsed | {data_parsed}")
            return [(sender_address, MessageGenerator.generate_error_message("No object_id in ihaveobject"))]
    except Exception as e:
        LogPlus.error(f"| ERROR | inputHandling | handle_ihaveobject | {data_parsed} | {sender_address} | {e}")
        return [(sender_address, MessageGenerator.generate_error_message("Unknown Error"))]


# This is called when a getobject message is received
def handle_getobject(data_parsed, sender_address):
    print("getobject starting")
    try:
        LogPlus.info(f"| INFO | ObjectHandler | handle_getobject |")
        if "object_id" in data_parsed:
            if ObjectHandler.is_object_known(data_parsed["object_id"]):
                LogPlus.info(f"| INFO | {sender_address} | GETOBJECT | {data_parsed} | Object requested | {data_parsed['object_id']}")
                return [(sender_address, MessageGenerator.generate_object_message(ObjectHandler.get_object(data_parsed["object_id"])))]
            else:
                LogPlus.info(f"| INFO | {sender_address} | GETOBJECT | {data_parsed} | Object not known | {data_parsed['object_id']}")
                return [(sender_address, MessageGenerator.generate_error_message("Object not known"))]
        else:
            LogPlus.error(f"| ERROR | {sender_address} | GETOBJECT | {data_parsed} | No object in data_parsed")
            return [(sender_address, MessageGenerator.generate_error_message("No object_id in getobject"))]
    except Exception as e:
        LogPlus.error(f"| ERROR | inputHandling | handle_getobject | {sender_address} | {e}")
        return [(sender_address, MessageGenerator.generate_error_message("Unknown Error"))]


# This is called when an object message is received
def handle_object(data_parsed, sender_address):
    try:
        responses = []
        if "object" in data_parsed:
            object_json = data_parsed["object"]
            print(Fore.CYAN + str(object_json) + Style.RESET_ALL)
            object = ObjectCreator.create_object(object_json)
            object_id = object.get_id()

            print(Fore.BLUE + str(object) + Style.RESET_ALL)
            if not ObjectHandler.is_object_known(object_id):  # If the object is not known, right? -- yes!
                LogPlus.info(f"| INFO | inputHandling | handle_object | New object received | {object_id}")

                # validate object and add it to the database
                try:
                    if object.verify():
                        print(Fore.GREEN + "Object verified" + Style.RESET_ALL)
                        ObjectHandler.add_object(object)
                    else:
                        LogPlus.warning(f"| WARNING | inputHandling | hande_object | Object not valid | {object_id}")
                        return [(sender_address, MessageGenerator.generate_error_message("Object not valid"))]
                except Exception as e:
                    LogPlus.error(f"| ERROR | inputHandler | handle_object | Couldn't add object | {e} ")
                
                # send ihaveobject message to active nodes
                try:
                    message = MessageGenerator.generate_ihaveobject_message(object_id)
                    print(message)
                    print(KnownNodesHandler.active_nodes)
                    #for node_credentials in KnownNodesHandler.active_nodes:
                    #    responses.append((node_credentials, message))

                    # make the for loop in one line
                    responses = [(node_credentials, message) for node_credentials in KnownNodesHandler.active_nodes]
                    LogPlus.info(f"| INFO | OBJECT | ihaveobject message sent to active nodes | {object_id}")
                    return responses

                    #KnownNodesHandler.get_active_object(object_id)
                    #return MessageGenerator.generate_ihaveobject_message(object_id)

                    # return MessageGenerator.generate_error_message("No object_id in ihaveobject")
                    # NODE_NETWOKRING.send_to_node(credentials, data)
                except Exception as e:
                    LogPlus.error(f"| ERROR | OBJECT | Couldn't gossip | {e} | {e.args}")
            else:
                LogPlus.info(f"| INFO | OBJECT | Object already known | {object_id}")
        else:
            LogPlus.error(f"| ERROR | OBJECT | No object in data_parsed | {data_parsed}")
            return [(sender_address, MessageGenerator.generate_error_message("No object in object message"))]
    except Exception as e:
        LogPlus.error(f"| ERROR | inputHandling | handle_object | {data_parsed} | {sender_address} | {e}")
        return [(sender_address, MessageGenerator.generate_error_message("Unknown Error"))]


