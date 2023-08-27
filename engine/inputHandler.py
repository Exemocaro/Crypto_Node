import json
import jsonschema

from utility.credentials_utility import *
from utility.logplus import LogPlus

from database.KnownNodesHandler import KnownNodesHandler
from database.ObjectHandler import ObjectHandler
from database.Mempool import Mempool
from database.UTXO import UTXO

from object.Object import Object
from object.ObjectCreator import ObjectCreator
from object.Transaction import Transaction
from object.Block import Block
from object.CoinbaseTransaction import CoinbaseTransaction

from engine.MessageGenerator import MessageGenerator

from config import *
from json_keys import *

from utility.json_validation import *
from utility.TimeTracker import TimeTracker

# This is called when a message is received
# It calls the appropriate function based on the type of the message
# It returns the response (as byte-like data) to be sent back to the sender
# If no response is needed, it returns None
# If the message is not valid, it returns an error message


def handle_input(data, handler):
    """Handles the input from the network. Returns a list of tuples (address, message) to be sent back to other nodes."""
    sender_address = handler.credentials
    try:
        data_parsed = json.loads(str(data, encoding="utf-8"))
    except Exception as e:
        # Maybe we should seperate for internal and external errors, this is an external error, so we should not log it as an error
        LogPlus.info(
            f"| INFO | inputHandler | handle_input | Inavlid JSON | {data} | {e}"
        )
        return [
            (sender_address, MessageGenerator.generate_error_message("Invalid json."))
        ]

    # validate the message schema
    try:
        jsonschema.validate(instance=data_parsed, schema=message_schema)
    except jsonschema.exceptions.ValidationError as e:
        LogPlus.info(
            f"| INFO | inputHandler | handle_input | Invalid message schema | {data} | {e}"
        )
        return [
            (
                sender_address,
                MessageGenerator.generate_error_message("Invalid message schema."),
            )
        ]

    try:
        message_type = data_parsed[type_key]

        # validate the message schema
        if not validate_message_schema(data_parsed, message_type):
            return [
                (
                    sender_address,
                    MessageGenerator.generate_error_message("Invalid message schema."),
                )
            ]

        # first message must be a hello message
        if handler.message_count == 0:
            if message_type != hello_key:
                handler.close()
                return None

        # call the appropriate function based on the message type
        return globals()["handle_" + message_type](data_parsed, sender_address)
    except Exception as e:
        LogPlus.error(
            f"| ERROR | inputHandling | handle_input | {data} | {sender_address} | {e}"
        )
        return [
            (sender_address, MessageGenerator.generate_error_message("Unknown Error"))
        ]


@staticmethod
def validate_message_schema(data_parsed, message_type):
    """Validates the message schema.
    Returns True if the schema is valid, False otherwise."""
    # Message schema name is the message type with _message_schema
    schema_name = message_type + "_message_schema"
    schema = globals()[schema_name]
    try:
        jsonschema.validate(instance=data_parsed, schema=schema)
    except Exception as e:
        LogPlus.error(
            f"| ERROR | inputHandling | validate_message_schema | {data_parsed} | {e}"
        )
        return False
    return True


@staticmethod
def handle_hello(data_parsed, sender_address):
    """This is called when a hello message is received"""
    # dont send a hello here, because the hello is already sent in the connection handler
    return []


@staticmethod
def handle_getpeers(data_parsed, sender_address):
    """This is called when a getpeers message is received"""
    return [
        (
            sender_address,
            MessageGenerator.generate_peers_message(KnownNodesHandler.known_nodes),
        )
    ]


@staticmethod
def handle_peers(data_parsed, sender_address):
    """This is called when a peers message is received"""
    # add the peers to the known nodes
    for peer in data_parsed[peers_key]:
        KnownNodesHandler.add_node(peer)


@staticmethod
def handle_error(data_parsed, sender_address):
    """This is called when an error message is received"""
    # nothing has to be done here, but logging is a good idea
    LogPlus.error(
        f"| ERROR | inputHandling.handle_error | {data_parsed} | {sender_address}"
    )
    return []


@staticmethod
def handle_ihaveobject(data_parsed, sender_address):
    """This is called when an ihaveobject message is received"""
    # send the getobject message if we don't have it
    if not ObjectHandler.is_object_known(data_parsed[objectid_key]):
        return [
            (
                sender_address,
                MessageGenerator.generate_getobject_message(data_parsed[objectid_key]),
            )
        ]

    return []


@staticmethod
def handle_getobject(data_parsed, sender_address):
    """This is called when a getobject message is received"""
    object_id = data_parsed[objectid_key]
    # get the object
    object = ObjectHandler.get_object(object_id)
    # always send the object independent of it's validaty!
    return [(sender_address, MessageGenerator.generate_object_message(object))]


@staticmethod
def handle_object(data_parsed, sender_address):
    """This is called when an object message is received"""
    object_json = data_parsed[object_key]
    try:
        object = ObjectCreator.create_object(object_json)
    except Exception as e:
        LogPlus.error(f"| ERROR | inputHandling | handle_object | {object_json} | {e}")
        return [
            (sender_address, MessageGenerator.generate_error_message("Invalid object"))
        ]

    # check if the object is valid
    if not object.verify():
        LogPlus.info(f"| INFO | inputHandling | Invalid object | {object.get_id()}")
        return [
            (sender_address, MessageGenerator.generate_error_message("Invalid object"))
        ]

    object_id = object.get_id()

    if ObjectHandler.is_object_known(object_id):
        LogPlus.info(f"| INFO | inputHandling | Object already known | {object_id}")
        return []

    # add the object to the database
    ObjectHandler.add_object(
        object.get_json(), "received", object.get_type(), sender_address
    )

    # validate the object
    responses = revalidate_pending_objects(sender_address)

    LogPlus.info(f"| INFO | inputHandling | Object received | {object_id}")

    return responses


@staticmethod
def handle_getchaintip(data_parsed, sender_address):
    """This is called when a getchaintip message is received"""
    # get the chaintip block
    chaintip = ObjectHandler.get_chaintip()
    # send the chaintip message
    return [(sender_address, MessageGenerator.generate_chaintip_message(chaintip))]


@staticmethod
def handle_chaintip(data_parsed, sender_address):
    """This is called when a chaintip message is received"""
    # get the chaintip
    chaintip = data_parsed[blockid_key]
    # check if the chaintip is known, if so, do nothing
    if ObjectHandler.is_object_known(chaintip):
        return []
    # request the chaintip
    message = MessageGenerator.generate_getobject_message(chaintip)
    return [(sender_address, message)]


@staticmethod
def handle_getmempool(data_parsed, sender_address):
    """This is called when a getmempool message is received"""
    LogPlus.debug(f"| DEBUG | inputHandling.handle_getmempool | { sender_address}")
    return Mempool.get_mempool()


@staticmethod
def handle_mempool(data_parsed, sender_address):
    """This is called when a mempool message is received"""
    LogPlus.debug(
        f"| DEBUG | inputHandling.handle_mempool | {data_parsed[txids_key]} | {sender_address}"
    )
    txids = data_parsed[txids_key]
    responses = []
    for txid in txids:
        if not ObjectHandler.is_object_known(txid):
            responses.append((None, MessageGenerator.generate_getobject_message(txid)))
    return []


@staticmethod
def revalidate_pending_objects(sender_address=None):
    """Revalidates all pending objects and returns a list of responses"""
    try:
        TimeTracker.start("revalidate_pending_objects")
        revalidate = True
        responses = []
        while revalidate:
            revalidate = False
            pending_objects = ObjectHandler.get_verifiable_objects()
            TimeTracker.checkpoint(
                "revalidate_pending_objects", "got all pending objects"
            )
            for pending_object in pending_objects:
                obj = ObjectCreator.create_object(pending_object, False)
                TimeTracker.checkpoint(
                    "revalidate_pending_objects", "created one pending object"
                )
                verification_results = verify_object(obj, sender_address)
                TimeTracker.checkpoint(
                    "revalidate_pending_objects", "verified one pending object"
                )
                responses += verification_results[responses_key]
                if not revalidate:
                    revalidate = verification_results[revalidation_key]
            TimeTracker.checkpoint(
                "revalidate_pending_objects", "looped through all pending objects"
            )
        TimeTracker.end("revalidate_pending_objects")
        return responses
    except Exception as e:
        LogPlus.error(f"| ERROR | inputHandling.revalidate_pending_objects | {e}")
        return []


@staticmethod
def verify_object(object: Object, sender_address=None):
    """Verifies an object (given as Object type)
    returns a list of responses and a boolean if the object has to be revalidated"""

    TimeTracker.start("verify_object")
    verification_result = None

    object_id = object.get_id()
    object_type = object.get_type()

    responses = []
    revalidation = False

    # LogPlus.debug(f"| DEBUG | inputHandling | verify_object | {object_id[:10]}... | {object_type}")

    # validate object and add it to the database - first add the object to the database and then validate it!!
    try:
        # add the object to the database if it is not known
        if not ObjectHandler.is_object_known(object_id):
            ObjectHandler.add_object(
                object.get_json(), "received", object_type, sender_address
            )
            LogPlus.info(
                f"| INFO | inputHandling | verify_object | {object_id[:10]}... | Object added to database"
            )
            revalidation = True

        TimeTracker.checkpoint("verify_object", "add_object")

        # valid and invalid are final states, we dont need to revalidate them
        if ObjectHandler.get_status(object_id) in ["valid", "invalid"]:
            LogPlus.info(
                f"| INFO | inputHandling | verify_object | {object_id[:10]}... | Object already validated"
            )
            return {"responses": [], "revalidation": False}

        TimeTracker.checkpoint("verify_object", "check_status")

        # result will be a dictionary {"result": ..., "missing": [...], "pending": [...]}
        verification_result = object.verify()

        TimeTracker.checkpoint("verify_object", "object verified")

        status = verification_result[result_key]

        # LogPlus.debug(f"| DEBUG | inputHandling | verify_object | {object_id[:10]}... | Object verification result | {verification_result}")

        missing = (
            []
            if not "missing" in verification_result
            else verification_result[missing_key]
        )
        pending = (
            []
            if not "pending" in verification_result
            else verification_result[pending_key]
        )

        TimeTracker.checkpoint("verify_object", "get missing and pending")

        ObjectHandler.update_object_status(object_id, status, missing, pending)

        TimeTracker.checkpoint("verify_object", "update_object_status")

    except Exception as e:
        LogPlus.error(
            f"| ERROR | inputHandling | verify_object | {object_id[:10]}...| Object verification failed | {e}"
        )
        return {"responses": [], "revalidation": False}

    LogPlus.info(
        f"| INFO | inputHandling | {object_id[:10]}... | Object verification result | {verification_result}"
    )

    try:
        if status == "valid":
            # gossip the object (send ihaveobeject to all known nodes)
            message = MessageGenerator.generate_ihaveobject_message(object_id)
            responses.append((None, message))
            revalidation = True
            # if it's a block, check if we have a new longest chain
            if object_type == "block":
                LogPlus.info(
                    f"| INFO | inputHandling | verify_object | {object_id[:10]}... | Block verified | Checking for new longest chain"
                )
                if ObjectHandler.get_chaintip() == object_id:
                    # Redo the mempool validation
                    LogPlus.debug(f"Redo the mempool for the longest chain")
                    UTXO.get_utxo(
                        object_id
                    )  # this updated the longest chain utxo in UTXO
                    Mempool.apply_block(object.get_json())
            if object_type == Transaction.TYPE:
                # Check if it's in the mempool or might be added
                if object_id in Mempool.mempool_txids:
                    LogPlus.info(
                        f"| INFO | inputHandling | Object already in mempool | {object_id}"
                    )

                # Check if the transaction can be added to the mempool
                elif not Mempool.add_transaction(object.get_json()):
                    LogPlus.info(
                        f"| INFO | inputHandling | Object can't be added to mempool | {object_id}"
                    )
                    responses.append(
                        (
                            sender_address,
                            MessageGenerator.generate_error_message(
                                "Object can't be added to mempool"
                            ),
                        )
                    )

        elif status == "invalid":
            original_sender = ObjectHandler.get_orginal_sender(object_id)
            if original_sender is not None:
                responses.append(
                    (
                        original_sender,
                        MessageGenerator.generate_error_message(
                            "Object verification failed!"
                        ),
                    )
                )
            revalidation = True

        elif status == "pending":
            if "missing" in verification_result:
                for txid in verification_result[missing_key]:
                    message = MessageGenerator.generate_getobject_message(txid)
                    responses.append((None, message))
                    if sender_address is not None:
                        responses.append((sender_address, message))

        TimeTracker.checkpoint("verify_object", "result handling")

    except Exception as e:
        LogPlus.error(
            f"| ERROR | inputHandling | verify_object | Result handling | {object_id[:10]}... | {e}"
        )
        return {"responses": [], "revalidation": False}
    finally:
        TimeTracker.end("verify_object")

    # LogPlus.debug(f"| DEBUG | inputHandling | verify_object | {object_id} | Revalidation | {revalidation}")
    return {"responses": responses, "revalidation": revalidation}
