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
    """ Handles the input from the network. Returns a list of tuples (address, message) to be sent back to other nodes. """
    sender_address = handler.credentials
    try:
        data_parsed = json.loads(str(data, encoding="utf-8"))
    except Exception as e:
        # Maybe we should seperate for internal and external errors, this is an external error, so we should not log it as an error
        LogPlus.info(f"| INFO | inputHandler | handle_input | Inavlid JSON | {data} | {e}")
        return [(sender_address, MessageGenerator.generate_error_message("Invalid json."))]

    try:
        if type_key in data_parsed:
            message_type = data_parsed[type_key]
            if message_type in message_keys:
                if not validate_message_schema(data_parsed, message_type):
                    return [(sender_address, MessageGenerator.generate_error_message("Invalid message schema."))]
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

@staticmethod
def validate_message_schema(data_parsed, message_type):
    """ Validates the message schema.
    Returns True if the schema is valid, False otherwise. """
    # Message schema name is the message type with _message_schema
    schema_name = message_type + "_message_schema"
    schema = globals()[schema_name]
    try:
        jsonschema.validate(instance=data_parsed, schema=schema)
    except Exception as e:
        LogPlus.error(f"| ERROR | inputHandling | validate_message_schema | {data_parsed} | {e}")
        return False
    return True


@staticmethod
def handle_hello(data_parsed, sender_address):
    """ This is called when a hello message is received """
    # dont send a hello here, because the hello is already sent in the connection handler
    return []


@staticmethod
def handle_getpeers(data_parsed, sender_address):
    """ This is called when a getpeers message is received """
    return [(sender_address, MessageGenerator.generate_peers_message(KnownNodesHandler.known_nodes))]


@staticmethod
def handle_peers(data_parsed, sender_address):
    """ This is called when a peers message is received """
    # add the peers to the known nodes
    for peer in data_parsed[peers_key]:
        KnownNodesHandler.add_node(peer)


@staticmethod
def handle_error(data_parsed, sender_address):
    """ This is called when an error message is received """
    # nothing has to be done here, but logging is a good idea
    LogPlus.error(f"| ERROR | inputHandling.handle_error | {data_parsed} | {sender_address}")
    return []


@staticmethod
def handle_ihaveobject(data_parsed, sender_address):
    """ This is called when an ihaveobject message is received"""
    # send the getobject message if we don't have it
    if not ObjectHandler.is_object_known(data_parsed[objectid_key]):
        return [(sender_address, MessageGenerator.generate_getobject_message(data_parsed[objectid_key]))]

    return []


@staticmethod
def handle_getobject(data_parsed, sender_address):
    """ This is called when a getobject message is received """
    object_id = data_parsed[objectid_key]
    # get the object
    object = ObjectHandler.get_object(object_id)
    # always send the object independent of it's validaty! 
    return [(sender_address, MessageGenerator.generate_object_message(object))]
    

@staticmethod
def handle_object(data_parsed, sender_address):
    """ This is called when an object message is received """
    responses = []
    object_json = data_parsed[object_key]
    object = ObjectCreator.create_object(object_json)
    object_id = object.get_id()

    if ObjectHandler.is_object_known(object_id):
        LogPlus.info(f"| INFO | inputHandling | Object already known | {object_id}")
        return responses
        
    # add the object to the database
    ObjectHandler.add_object(object.get_json(), "received", object.get_type(), sender_address)

    # validate the object
    responses += revalidate_pending_objects(sender_address)

    LogPlus.info(f"| INFO | inputHandling | Object received | {object_id}")

    return responses


@staticmethod
def handle_getchaintip(data_parsed, sender_address):
    """ This is called when a getchaintip message is received """
    # get the chaintip block
    chaintip = ObjectHandler.get_chaintip()
    # send the chaintip message
    return [(sender_address, MessageGenerator.generate_chaintip_message(chaintip))]


@staticmethod
def handle_chaintip(data_parsed, sender_address):
    """ This is called when a chaintip message is received """
    # get the chaintip
    chaintip = data_parsed[blockid_key]
    # check if the chaintip is known, if so, do nothing
    if ObjectHandler.is_object_known(chaintip):
        return []
    # request the chaintip
    message = MessageGenerator.generate_getobject_message(chaintip)
    return [(sender_address, message)]

@staticmethod
def revalidate_pending_objects(sender_address = None):
    """ Revalidates all pending objects and returns a list of responses """
    try:
        revalidate = True
        responses = []
        while revalidate:
            revalidate = False
            pending_objects = ObjectHandler.get_verifiable_objects()
            for pending_object in pending_objects:
                verification_results = verify_object(ObjectCreator.create_object(pending_object), sender_address)
                responses += verification_results["responses"]
                if not revalidate:
                    revalidate = verification_results["revalidation"]
        return responses
    except Exception as e:
        LogPlus.error(f"| ERROR | inputHandling.revalidate_pending_objects | {e}")
        return []

@staticmethod 
def verify_object(object, sender_address = None):
    """ Verifies an object (given as Object type) and returns a list of responses """
    verification_result = None

    object_id = object.get_id()
    object_type = object.get_type()

    responses = []
    revalidation = False


    # validate object and add it to the database - first add the object to the database and then validate it!!
    try:
        if not ObjectHandler.is_object_known(object_id):
            ObjectHandler.add_object(object.get_json(), "received", object_type, sender_address)
            LogPlus.info(f"| INFO | inputHandling | verify_object | {object_id} | Object added to database")

        if ObjectHandler.get_status(object_id) in ["valid", "invalid"]:
            LogPlus.info(f"| INFO | inputHandling | verify_object | {object_id} | Object already validated")
            return {"responses": [], "revalidation": False}

        verification_result = object.verify()
        if verification_result["result"] not in ["valid", "invalid", "pending"]:
            # This should never happen, would be an internal issue
            LogPlus.error(f"| ERROR | inputHandling | verify_object | {object_id} | Invalid verification result | {verification_result}")
            return {"responses": [], "revalidation": False}
        
        status = verification_result["result"]
        missing = [] if not "missing" in verification_result.keys() else verification_result["missing"]
        pending = [] if not "pending" in verification_result.keys() else verification_result["pending"]

        ObjectHandler.update_object_status(object_id, status, missing, pending)

    except Exception as e:
        LogPlus.error(f"| ERROR | inputHandling | verify_object | {object_id} | Object verification failed | {e}")

    LogPlus.info(f"| INFO | inputHandling | {object_id} | Object verification result | {verification_result}")

    try:
        if status == "valid":
            # gossip the object (send ihaveobeject to all known nodes)
            message = MessageGenerator.generate_ihaveobject_message(object_id)
            responses += [(node, message) for node in KnownNodesHandler.known_nodes]
            revalidation = True

        elif status == "invalid":
            original_sender = ObjectHandler.get_orginal_sender(object_id)
            if original_sender is not None:
                responses.append((original_sender, MessageGenerator.generate_error_message("Object verification failed!")))
            revalidation = True

        elif status == "pending":
            if "missing" in verification_result.keys():
                for txid in verification_result["missing"]:
                    message =  MessageGenerator.generate_getobject_message(txid)
                    responses += [(node_credentials, message) for node_credentials in KnownNodesHandler.known_nodes]
                    if sender_address is not None: 
                        responses.append((sender_address, message))      

    except Exception as e:
        LogPlus.error(f"| ERROR | inputHandling | verify_object | Result handling | {object_id} | {e}")


    return {"responses": responses, "revalidation": revalidation }