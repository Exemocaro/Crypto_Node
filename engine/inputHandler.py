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

    try:

        responses = []
        object_json = data_parsed[object_key]
        object = ObjectCreator.create_object(object_json)
        object_id = object.get_id()
        LogPlus.debug(f"| DEBUG | inputHandling | handle_object | Object received | {object_id}")

        if not ObjectHandler.is_object_known(object_id):
            LogPlus.info(f"| INFO | inputHandling | handle_object | New object received | {object_id}")
            verification_results = verify_object(object, sender_address)
            LogPlus.debug(f"| DEBUG | inputHandling | handle_object | Verification results | {verification_results}")
            responses += verification_results["responses"]
            revalidate = verification_results["revalidation"]
            if revalidate:
                responses += revalidate_pending_objects(sender_address)
                
        else: # Object is already known
            LogPlus.info(f"| INFO | inputHandling | Object already known | {object_id}")

        return responses
    except Exception as e:
        LogPlus.error(f"| ERROR | inputHandling.handle_object | All | {data_parsed} | {sender_address} | {e}")
        return [(sender_address, MessageGenerator.generate_error_message("Unknown Error"))]

@staticmethod 
def verify_object(object, sender_address = None):
    verification_result = None

    object_id = object.get_id()
    object_type = object.get_type()

    responses = []
    revalidation = False


    # validate object and add it to the database - first add the object to the database and then validate it!!
    try:
        if not ObjectHandler.is_object_known(object_id):
            ObjectHandler.add_object(object.get_json(), "validation started", object_type)
            LogPlus.info(f"| INFO | inputHandling | handle_object | {object_id} | Object added to database")

        verification_result = object.verify()
        if verification_result["result"] == "True":
            try:
                ObjectHandler.update_object_status(object_id, "valid")
                # gossip the object (send ihaveobeject to all known nodes)
                message = MessageGenerator.generate_ihaveobject_message(object_id)
                responses += [(node, message) for node in KnownNodesHandler.known_nodes]
                revalidation = True
                # also check if pending objects can be verified now
                ObjectHandler.update_pending_objects(object_id)
            except Exception as e:
                LogPlus.error(f"| ERROR | inputHandling | handle_object | B | {object_id} | {e}")

        elif verification_result["result"] == "False":
            try:
                ObjectHandler.update_object_status(object_id, "invalid")
                ObjectHandler.update_pending_objects(object_id)
                LogPlus.error(f"| ERROR | inputHandling | handle_object | {object_id} | Object verification failed")
                if sender_address is not None:
                    responses.append((sender_address, MessageGenerator.generate_error_message("Object verification failed!")))
                revalidation = True
            except Exception as e:
                LogPlus.error(f"| ERROR | inputHandling | handle_object | C | {object_id} | {e}")

        elif verification_result["result"] == "data missing":
            try:
                ObjectHandler.update_object_status(object.get_id(), "pending")
                ObjectHandler.set_requirements(object.get_id(), verification_result["missing"], verification_result["pending"])# request missing data (getobject)
                LogPlus.debug(f"| DEBUG | inputHandling | handle_object | {object_id} | Missing data | {verification_result['missing']}")
                for txid in verification_result["missing"]:
                    message =  MessageGenerator.generate_getobject_message(txid)
                    responses += [(node_credentials, message) for node_credentials in KnownNodesHandler.active_nodes]
                    if sender_address is not None: 
                        responses.append((sender_address, message))                
            except Exception as e:
                LogPlus.error(f"| ERROR | inputHandling | handle_object | D | {object_id} | {e}")

    except Exception as e:
        LogPlus.error(f"| ERROR | inputHandler | handle_object | Couldn't add object | {e} ")

    return {"responses": responses, "revalidation": revalidation }

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

@staticmethod
def revalidate_pending_objects(sender_address = None):
    try:
        revalidate = True
        while revalidate:
            revalidate = False
            LogPlus.debug(f"| DEBUG | inputHandling.revalidate_pending_objects | revalidating pending objects")
            pending_objects = ObjectHandler.get_verifiable_objects()
            responses = []
            for pending_object in pending_objects:
                try:
                    verification_results = verify_object(ObjectCreator.create_object(pending_object), sender_address)
                    LogPlus.debug(f"| DEBUG | inputHandling.revalidate_pending_objects | verification results for {Object.get_id_from_json(pending_object)[:10]}... | {verification_results}")
                    responses += verification_results["responses"]
                    if not revalidate:
                        revalidate = verification_results["revalidation"]
                except Exception as e:
                    LogPlus.error(f"| ERROR | inputHandling.revalidate_pending_objects | object problem inside for loop, object printed above | {e} | {e.args}")
        return responses
    except Exception as e:
        LogPlus.error(f"| ERROR | inputHandling.revalidate_pending_objects | {e}")
        return []
