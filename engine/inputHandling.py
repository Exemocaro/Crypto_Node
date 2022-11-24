import logging
import json
import jsonschema


from utility.credentials_utility import *
from utility.logplus import *

from database.KnownNodesHandler import *
from database.ObjectHandler import *

from object.Object import Object

from engine.generateMessage import MessageGenerator

from config import *

from utility.json_validation import *

from object.ObjectCreator import ObjectCreator


# This is called when a message is received
# It calls the appropriate function based on the type of the message
# It returns the response (as byte-like data) to be sent back to the sender
# If no response is needed, it returns None
# If the message is not valid, it returns an error message
def handle_input(data, handler):
    sender_address = handler.credentials
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
                if handler.message_count == 0: # first message
                    if function_name != "hello":
                        handler.close()
                        return None
                elif handler.message_count == 1: # second message
                    if function_name != "getpeers":
                        handler.close()
                        return None
                response = globals()["handle_" + function_name](data_parsed, sender_address)
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
        jsonschema.validate(instance=data_parsed, schema=hello_message_schema)
    except Exception as e:
        LogPlus.error(f"| ERROR | inputHandling.handle_hello | {data_parsed} | {sender_address} | {e}")
        return [(sender_address, MessageGenerator.generate_error_message("Invalid hello message!"))]

    return [(sender_address, MessageGenerator.generate_hello_message())]


# This is called when a getpeers message is received
def handle_getpeers(data_parsed, sender_address):
    try:
        jsonschema.validate(instance=data_parsed, schema=getpeers_message_schema)
    except Exception as e:
        LogPlus.error(f"| ERROR | inputHandling.handle_getpeers | {data_parsed} | {sender_address} | {e}")
        return [(sender_address, MessageGenerator.generate_error_message("Invalid getpeers message!"))]

    return [(sender_address, MessageGenerator.generate_peers_message())]


# This in called when a peers message is received
def handle_peers(data_parsed, sender_address):
    try:
        jsonschema.validate(instance=data_parsed, schema=peers_message_schema)
    except Exception as e:
        LogPlus.error(f"| ERROR | inputHandling.handle_peers | {data_parsed} | {sender_address} | {e}")
        return [(sender_address, MessageGenerator.generate_error_message("Invalid peers message!"))]

    # add the peers to the known nodes
    for peer in data_parsed["peers"]:
        KnownNodesHandler.add_known_node(peer)

    # send the ihaveobject message
    return [(sender_address, MessageGenerator.generate_ihaveobject_message())]

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
        jsonschema.validate(instance=data_parsed, schema=ihaveobject_schema)
    except Exception as e:
        LogPlus.error(f"| ERROR | inputHandling.handle_ihaveobject | {data_parsed} | {sender_address} | {e}")
        return [(sender_address, MessageGenerator.generate_error_message("Invalid ihaveobject message!"))]

    # add the object to the known objects
    ObjectHandler.add_known_object(data_parsed["objectid"])

    # send the getobject message
    return [(sender_address, MessageGenerator.generate_getobject_message())]


# This is called when a getobject message is received
def handle_getobject(data_parsed, sender_address):
    try:
        jsonschema.validate(instance=data_parsed, schema=getobject_schema)
    except Exception as e:
        LogPlus.error(f"| ERROR | inputHandling.handle_getobject | {data_parsed} | {sender_address} | {e}")
        return [(sender_address, MessageGenerator.generate_error_message("Invalid getobject message!"))]

    # get the object
    object = ObjectHandler.get_object(data_parsed["objectid"])

    # send the object
    return [(sender_address, MessageGenerator.generate_object_message(object))]


# This is called when an object message is received
def handle_object(data_parsed, sender_address):
    """try:
        responses = []
        if "object" in data_parsed:
            object_json = data_parsed["object"]
            object = ObjectCreator.create_object(object_json)
            object_id = object.get_id()

            if not ObjectHandler.is_object_known(object_id):  # If the object is not known, right? -- yes!
                LogPlus.info(f"| INFO | inputHandling | handle_object | New object received | {object_id}")

                # validate object and add it to the database
                try:
                    verification_result = object.verify()
                    if not "result" in verification_result:
                        LogPlus.error(f"| ERROR | inputHandling | handle_object | {object_id} | No result in verification_result")
                        return []
                    if verification_result["result"] == "True":
                        ObjectHandler.add_object(object)
                        LogPlus.info(f"| INFO | inputHandling | handle_object | {object_id} | Object added to database")
                    elif verification_result["result"] == "False":
                        LogPlus.error(f"| ERROR | inputHandling | handle_object | {object_id} | Object verification failed")
                        return []
                    elif verification_result["result"] == "Information missing":
                        # request missing information (getobject)
                        messages_to_send = []
                        for txid in verification_result["txids"]:
                            messages_to_send.append((sender_address, MessageGenerator.generate_getobject_message(txid)))
                        return messages_to_send

                except Exception as e:
                    LogPlus.error(f"| ERROR | inputHandler | handle_object | Couldn't add object | {e} ")
                
                # send ihaveobject message to active nodes
                try:
                    message = MessageGenerator.generate_ihaveobject_message(object_id)
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
        return [(sender_address, MessageGenerator.generate_error_message("Unknown Error"))] """
    try:
        jsonschema.validate(instance=data_parsed, schema=object_schema)
    except Exception as e:
        LogPlus.error(f"| ERROR | inputHandling.handle_object | {data_parsed} | {sender_address} | {e}")
        return [(sender_address, MessageGenerator.generate_error_message("Invalid object message!"))]

    # get the object
    object = ObjectCreator.create_object(data_parsed["object"])

    # add the object to the database
    ObjectHandler.add_object(object)

    # send the ihaveobject message
    return [(sender_address, MessageGenerator.generate_ihaveobject_message(object.get_id()))]


