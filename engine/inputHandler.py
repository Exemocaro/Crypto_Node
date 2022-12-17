import json
import jsonschema


from utility.credentials_utility import *
from utility.logplus import LogPlus

from database.KnownNodesHandler import KnownNodesHandler
from database.ObjectHandler import ObjectHandler

from object.Object import Object
from object.ObjectCreator import ObjectCreator

from engine.MessageGenerator import MessageGenerator

from config import *
from json_keys import *

from utility.json_validation import *


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
        LogPlus.error(f"| ERROR | inputHandler | A | handle_input | {data} | {e} | {e.args}")
        return [(sender_address, MessageGenerator.generate_error_message("Invalid json."))]

    try:
        if type_key in data_parsed:
            message_type = data_parsed[type_key]
            if message_type in message_keys:
                function_name = data_parsed[type_key]
                if handler.message_count == 0: # first message
                    if function_name != hello_key:
                        handler.close()
                        return None
                return  globals()["handle_" + function_name](data_parsed, sender_address)
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
@staticmethod
def handle_hello(data_parsed, sender_address):
    try:
        jsonschema.validate(instance=data_parsed, schema=hello_message_schema)
    except Exception as e:
        LogPlus.error(f"| ERROR | inputHandling.handle_hello | {data_parsed} | {sender_address} | {e}")
        return [(sender_address, MessageGenerator.generate_error_message("Invalid hello message!"))]
    # dont send a hello here, because the hello is already sent in the connection handler
    return []


# This is called when a getpeers message is received
@staticmethod
def handle_getpeers(data_parsed, sender_address):
    try:
        jsonschema.validate(instance=data_parsed, schema=getpeers_message_schema)
    except Exception as e:
        LogPlus.error(f"| ERROR | inputHandling.handle_getpeers | {data_parsed} | {sender_address} | {e}")
        return [(sender_address, MessageGenerator.generate_error_message("Invalid getpeers message!"))]

    return [(sender_address, MessageGenerator.generate_peers_message(KnownNodesHandler.known_nodes))]


# This in called when a peers message is received
@staticmethod
def handle_peers(data_parsed, sender_address):
    try:
        jsonschema.validate(instance=data_parsed, schema=peers_message_schema)
    except Exception as e:
        LogPlus.error(f"| ERROR | inputHandling.handle_peers | {data_parsed} | {sender_address} | {e}")
        return [(sender_address, MessageGenerator.generate_error_message("Invalid peers message!"))]

    # add the peers to the known nodes
    for peer in data_parsed[peers_key]:
        KnownNodesHandler.add_node(peer)

    # we don't do anything besides saving!! 

    ## send the ihaveobject message
    #return [(sender_address, MessageGenerator.generate_ihaveobject_message())]

# This is called when an error message is received
@staticmethod
def handle_error(data_parsed, sender_address):
    try:
        LogPlus.error(f"| ERROR | {sender_address} | ERROR | {data_parsed} | Error message received")
    except Exception as e:
        LogPlus.error(f"| ERROR | inputHandling | handle_error | {data_parsed} | {sender_address} | {e}")
        return [(sender_address, MessageGenerator.generate_error_message("Unknown Error"))]


# This is called when an ihaveobject message is received
@staticmethod
def handle_ihaveobject(data_parsed, sender_address):
    try:
        jsonschema.validate(instance=data_parsed, schema=ihaveobject_schema)
    except Exception as e:
        LogPlus.error(f"| ERROR | inputHandling.handle_ihaveobject | {data_parsed} | {sender_address} | {e}")
        return [(sender_address, MessageGenerator.generate_error_message("Invalid ihaveobject message!"))]

    # send the getobject message if we don't have it
    if not ObjectHandler.is_object_known(data_parsed[objectid_key]):
        return [(sender_address, MessageGenerator.generate_getobject_message(data_parsed[objectid_key]))]

    return []

# This is called when a getobject message is received
@staticmethod
def handle_getobject(data_parsed, sender_address):
    try:
        jsonschema.validate(instance=data_parsed, schema=getobject_schema)
    except Exception as e:
        LogPlus.error(f"| ERROR | inputHandling.handle_getobject | {data_parsed} | {sender_address} | {e}")
        return [(sender_address, MessageGenerator.generate_error_message("Invalid getobject message!"))]

    object_id = data_parsed[objectid_key]
    # get the object
    object = ObjectHandler.get_object(object_id)

    # always send the object independent of it's validaty! 
    res =  [(sender_address, MessageGenerator.generate_object_message(object))]
    return res
    
# This is called when an object message is received
@staticmethod
def handle_object(data_parsed, sender_address):
    try:
        jsonschema.validate(instance=data_parsed, schema=object_schema)
    except Exception as e:
        LogPlus.error(f"| ERROR | inputHandling.handle_object | Invalid schema | {data_parsed} | {sender_address} | {e}")
        return [(sender_address, MessageGenerator.generate_error_message("Invalid object message!"))]

    try:

        responses = []
        object_json = data_parsed[object_key]
        object = ObjectCreator.create_object(object_json)
        object_id = object.get_id()
        object_type = object.get_type()

        if not ObjectHandler.is_object_known(object_id):
            LogPlus.info(f"| INFO | inputHandling | handle_object | New object received | {object_id}")

            verification_result = None
            # validate object and add it to the database - first add the object to the database and then validate it!!
            try:
                # first we add the object
                LogPlus.info(f"| INFO | inputHandling | handle_object | {object_id} | Object added to database")
                try:
                    verification_result = object.verify()
                except Exception as e:
                    LogPlus.error(f"| ERROR | inputHandling.handle_object | Verification failed | {object_id} | {e}")
                    return [(sender_address, MessageGenerator.generate_error_message("Verification failed!"))]
                if not "result" in verification_result:
                    try:
                        LogPlus.error(f"| ERROR | inputHandling | handle_object | {object_id} | No result in verification_result")
                        return []
                    except Exception as e:
                        LogPlus.error(f"| ERROR | inputHandling | handle_object | A | {object_id} | {e}")
                if verification_result["result"] == "True":
                    try:
                        ObjectHandler.add_object(object.get_json(), "valid", object_type)
                        LogPlus.info(f"| INFO | inputHandling | handle_object | {object_id} | Object added to database")
                        # gossip the object (send ihaveobeject to all known nodes)
                        responses += [(node, MessageGenerator.generate_ihaveobject_message(object_id)) for node in KnownNodesHandler.known_nodes]
                        # also check if pending objects can be verified now
                        responses += revalidate_pending_objects()
                    except Exception as e:
                        LogPlus.error(f"| ERROR | inputHandling | handle_object | B | {object_id} | {e}")

                elif verification_result["result"] == "False":
                    try:
                        ObjectHandler.add_object(object.get_json(), "invalid", object_type)
                        LogPlus.error(f"| ERROR | inputHandling | handle_object | {object_id} | Object verification failed")
                        responses.append((sender_address, MessageGenerator.generate_error_message("Object verification failed!")))
                    except Exception as e:
                        LogPlus.error(f"| ERROR | inputHandling | handle_object | C | {object_id} | {e}")
                elif verification_result["result"] == "data missing":
                    try:
                        ObjectHandler.add_object(object.get_json(), "pending", object_type, verification_result["ids"])
                        # request missing data (getobject)
                        for txid in verification_result["ids"]:
                            message =  MessageGenerator.generate_getobject_message(txid)
                            responses += [(node_credentials, message) for node_credentials in KnownNodesHandler.active_nodes]  
                            responses.append((sender_address, message))                
                    except Exception as e:
                        LogPlus.error(f"| ERROR | inputHandling | handle_object | D | {object_id} | {e}")

            except Exception as e:
                LogPlus.error(f"| ERROR | inputHandler | handle_object | Couldn't add object | {e} ")
        else: # Object is already known
            LogPlus.info(f"| INFO | OBJECT | Object already known | {object_id}")

        return responses
    except Exception as e:
        LogPlus.error(f"| ERROR | inputHandling.handle_object | All | {data_parsed} | {sender_address} | {e}")
        return [(sender_address, MessageGenerator.generate_error_message("Unknown Error"))]

    # send the ihaveobject message
    return [(sender_address, MessageGenerator.generate_ihaveobject_message(object.get_id()))]

@staticmethod
def handle_getchaintip(data_parsed, sender_address):
    try:
        jsonschema.validate(instance=data_parsed, schema=getchaintip_schema)
    except Exception as e:
        LogPlus.error(f"| ERROR | inputHandling.handle_getchaintip | {data_parsed} | {sender_address} | {e}")
        return [(sender_address, MessageGenerator.generate_error_message("Invalid getchaintip message!"))]

    # get the chaintip block
    chaintip = ObjectHandler.get_chaintip()

    # send the chaintip message
    return [(sender_address, MessageGenerator.generate_chaintip_message(chaintip))]

@staticmethod
def handle_chaintip(data_parsed, sender_address):
    try:
        jsonschema.validate(instance=data_parsed, schema=chaintip_schema)
    except Exception as e:
        LogPlus.error(f"| ERROR | inputHandling.handle_chaintip | {data_parsed} | {sender_address} | {e}")
        return [(sender_address, MessageGenerator.generate_error_message("Invalid chaintip message!"))]

    # get the chaintip
    chaintip = data_parsed[blockid_key]

    # check if the chaintip is known
    if not ObjectHandler.is_object_known(chaintip):
        # request the chaintip
        message = MessageGenerator.generate_getobject_message(chaintip)
        return [(sender_address, message)]

    # send the chaintip message
    return []

# we now store the missing data for pending objects
# if the missing data is received, the pending object can be verified
# whenever we receive a new object, we check if there are pending objects that are waiting for it
# if there are, we can clear that object from the missing data list
# if the missing data list is empty, we can verify the pending object
@staticmethod
def update_pending_objects(new_object_id):
    pending_objects = ObjectHandler.get_pending_objects()
    responses = []
    for pending_object in pending_objects:
        if new_object_id in pending_object["missing"]:
            pending_object["missing"].remove(new_object_id)
            if len(pending_object["missing"]) == 0:
                try:
                    object = ObjectCreator.create_object(pending_object)
                    verification_result = object.verify()
                    if verification_result["result"] == "True":
                        ObjectHandler.update_object_status(object.get_id(), "valid")
                        # gossip the object
                        message = MessageGenerator.generate_ihaveobject_message(object.get_id())
                        responses += [(node_credentials, message) for node_credentials in KnownNodesHandler.active_nodes]
                    elif verification_result["result"] == "False":
                        ObjectHandler.update_object_status(object.get_id(), "invalid")
                    elif verification_result["result"] == "data missing":
                        ObjectHandler.update_object_status(object.get_id(), "pending", verification_result["ids"])
                        # request missing data (getobject)
                        for txid in verification_result["ids"]:
                            message =  MessageGenerator.generate_getobject_message(txid)
                            responses += [(node_credentials, message) for node_credentials in KnownNodesHandler.active_nodes]  
                except Exception as e:
                    LogPlus.error(f"| ERROR | inputHandling | update_pending_objects | {e}")

@staticmethod
def revalidate_pending_objects():
    try:
        pending_objects = ObjectHandler.get_verifiable_objects()
        responses = []
        for pending_object in pending_objects:
            try:
                object = ObjectCreator.create_object(pending_object)
                verification_result = object.verify()
                if verification_result["result"] == "True":
                    ObjectHandler.update_object_status(object.get_id(), "valid")
                    # gossip the object
                    message = MessageGenerator.generate_ihaveobject_message(object.get_id())
                    responses += [(node_credentials, message) for node_credentials in KnownNodesHandler.active_nodes]
                    # update pending objects
                    ObjectHandler.update_pending_objects(object.get_id())
                    # revalidate pending objects
                    responses += revalidate_pending_objects()
                elif verification_result["result"] == "False":
                    ObjectHandler.update_object_status(object.get_id(), "invalid")
                elif verification_result["result"] == "data missing":
                    ObjectHandler.update_object_status(object.get_id(), "pending")
            except Exception as e:
                LogPlus.error(f"| ERROR | inputHandling.revalidate_pending_objects | object problem inside for loop, object printed above | {e} | {e.args}")
                return []
        return responses
    except Exception as e:
        LogPlus.error(f"| ERROR | inputHandling.revalidate_pending_objects | {e}")
        return []
