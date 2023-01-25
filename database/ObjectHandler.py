import json
import json_canonical
import hashlib
import time
import copy
import typing

from colorama import Fore, Style

from threading import Thread, Timer
from queue import Queue

from utility.logplus import LogPlus
from utility.credentials_utility import *
#from UTXO import *
from object.Object import Object
#from object.ObjectCreator import ObjectCreator

from config import *

from json_keys import *


# This class handles all objects
# Objects can be either transactions or blocks
# The type of the object is stored in the object itself in the type_key field
# structure of a regular transaction:
# {
#     type_key: "transaction",
#     "inputs": [
#         {
#             "outpoint": {
#                 "txid": sha256-hash of previous transaction,
#                 "index": index of output within previous transaction
#             },
#             "sig": signature of the input, created with the private key of the owner of the outpoint
#         }
#     ],
#     "outputs": [
#         {
#             "pubkey": public key of the owner of the recipient,
#             "value": amount of coins, in picaker (1 ker = 10^12 picaker)
#         }
#     ]
# }
#
# structure of a coinbase transaction:
# {
#     type_key: "transaction",
#     "height": height of the block this transaction is in,
#     "outputs": [
#         {
#             "pubkey": public key of the owner of the recipient,
#             "value": amount of coins, in picaker (1 ker = 10^12 picaker)
#         }
#     ]
# }
#
# structure of a block:
# {
#     type_key: "block",
#     "txids": [sha256-hash of all transactions in the block],
#     "nonce": nonce of the block (sha256 format),
#     "previd": sha256-hash of the previous block,
#     "created": timestamp of the block creation,
#     "T": target of the block (sha256 format),
#     "miner": any string up to 128 characters
#     "note": any string up to 128 characters
# }

# The object handler also needs a mapping from id to index in object list / object

class ObjectHandler:
  
    id_to_index = {}
    objects_file = OBJECTS_FILE
    objects = DEFAULT_OBJECTS

    longest_chain_blockid = GENESIS_BLOCK_ID

    auto_save_queue = Queue()

    @staticmethod
    def update_id_to_index():
        """ Updates the id_to_index mapping """
        ObjectHandler.id_to_index = {}
        for i in range(len(ObjectHandler.objects)):
            object_id = ObjectHandler.objects[i][txid_key]
            ObjectHandler.id_to_index[object_id] = i

    @staticmethod
    def add_object(obj: typing.Dict, validity="valid", object_type="unknown", sender_address=None):
        """ Adds an object to the object list and saves it to the objects file 
            obj: the object to add
            validity: the validity of the object (valid, invalid, pending)
            object_type: the type of the object (transaction, block, unknown)
            sender_address: the address of the sender of the object """
        try:
            # if sender is tuple, convert to string
            if type(sender_address) == tuple:
                sender_address = convert_tuple_to_string(sender_address)
            txid = Object.get_id_from_json(obj)
            ObjectHandler.objects.append({
                "txid": txid,
                "validity": validity,
                object_key: obj,
                type_key: object_type,
                "missing": [],
                "pending": [],
                sender_key: sender_address
            })
            ObjectHandler.save()
            ObjectHandler.update_id_to_index()
            ObjectHandler.update_pending_objects(txid)

        except Exception as e:
            LogPlus.error("| ERROR | ObjectHandler.add_object | " + str(e))
            return False

    @staticmethod
    def get_object(object_id: str):
        """ Returns the object with the given id """
        if object_id in ObjectHandler.id_to_index:
            return ObjectHandler.objects[ObjectHandler.id_to_index[object_id]][object_key]
        else:
            return None
    
    @staticmethod
    def get_pending_objects():
        """ Returns all pending objects (objects with validity "pending") """
        return ObjectHandler.get_objects_with_status("pending")

    @staticmethod 
    def get_objects_with_status(status: str):
        """ Returns all objects with the given status """
        return [obj[object_key] for obj in ObjectHandler.objects if obj[validity_key] == status]

    @staticmethod
    def get_status(object_id):
        """ Returns the validity of the object with the given id
            If the object is not in the object list, returns "missing" """
        if object_id in ObjectHandler.id_to_index:
            return ObjectHandler.objects[ObjectHandler.id_to_index[object_id]][validity_key]
        else:
            return "missing"

    @staticmethod
    def update_pending_objects(object_id):
        """ Updates all pending objects that depend on the given object, takes the id of the object as input """
        try:
            # get status of object
            status = ObjectHandler.get_status(object_id)
            pending_objects = [obj for obj in ObjectHandler.objects if obj[validity_key] == "pending"]
            # check if object is in missing objects and remove the dependency
            for pending in pending_objects:
                # Add keys to pending object if they don't exist
                if not pending_key in pending or pending[pending_key] == None:
                    pending[pending_key] = []
                if not missing_key in pending or pending[missing_key] == None:
                    pending[missing_key] = []

                # Remove object from missing objects
                if object_id in pending[missing_key]:
                    pending[missing_key].remove(object_id)

                # check if object is in pending objects and remove the dependency if we have a result
                if object_id in pending[pending_key]:
                    pending[pending_key].remove(object_id)
                    # in case this object is invalid, set the pending object to invalid too, safes time
                    if status == "invalid":
                        pending[pending_key] = []
                        pending[validity_key] = "invalid"
                        pending[missing_key] = []
            ObjectHandler.save()
        except Exception as e:
            LogPlus.error(f"| ERROR | ObjectHandler.update_pending_objects | {e}")

    @staticmethod
    def update_all_pending_objects():
        """ Updates all pending objects """
        for obj in ObjectHandler.get_pending_objects():
            ObjectHandler.update_pending_objects(Object.get_id_from_json(obj))


    @staticmethod
    def get_verifiable_objects():
        """ Returns all objects that can be verified (objects with validity "pending" or "received") """
        try:
            pending_objects = [obj for obj in ObjectHandler.objects if obj[validity_key] == "pending"] 
            for obj in pending_objects:
                if not missing_key in obj or obj[missing_key] == None:
                    obj[missing_key] = []
                if not pending_key in obj or obj[pending_key] == None:
                    obj[pending_key] = []
            pending_objects = [obj for obj in pending_objects if len(obj[missing_key]) == 0]
            pending_objects = [obj for obj in pending_objects if len(obj[pending_key]) == 0]
            pending_objects = [obj[object_key] for obj in pending_objects]
            recevied_objects = ObjectHandler.get_objects_with_status("received")
            return pending_objects + recevied_objects
        except Exception as e:
            LogPlus.error(f"| ERROR | ObjectHandler.get_verifiable_objects | {e}")
            return []


    @staticmethod
    def update_object_status(object_id, validity, missing=[], pending=[]):
        """ Updates the status (and missing & pending) of the object with the given id """
        if object_id in ObjectHandler.id_to_index:
            index = ObjectHandler.id_to_index[object_id]
            ObjectHandler.objects[index][validity_key] = validity
            ObjectHandler.objects[index][missing_key] = missing
            ObjectHandler.objects[index][pending_key] = pending
            ObjectHandler.save()
            if validity in ["valid", "invalid"]:
                ObjectHandler.update_pending_objects(object_id)  

    @staticmethod
    def get_block_containing_object(object_id):
        """ Returns the id of the block containing the object with the given id
            None if the object is not in a block """
        # get all objects of type block
        blocks = [obj[object_key] for obj in ObjectHandler.objects if obj[type_key] == "block"]
        for block in blocks:
            if object_id in block[txids_key]:
                return Object.get_id_from_json(block)
        return None

    @staticmethod
    def get_chaintip():
        """ Returns the id of the chaintip """
        # get all objects of type block
        blocks = [obj[txid_key] for obj in ObjectHandler.objects if obj[type_key] == "block" and obj[validity_key] == "valid"]
        if len(blocks) <= 1:
            return GENESIS_BLOCK_ID
        
        # sort out genesis block
        blocks = [blockid for blockid in blocks if blockid != GENESIS_BLOCK_ID]

        # check height in coinbase transaction, return the blockid with the highest height
        chaintip_id = max(blocks, key=lambda block: ObjectHandler.get_height(block))
        return chaintip_id
        #return max(blocks, key=lambda block: get_block_height(block))[txid_key]    

    @staticmethod
    def is_valid(object_id):
        """ Takes an object id and returns True if the object is valid, False otherwise (might still be pending)"""
        if object_id in ObjectHandler.id_to_index:
            return ObjectHandler.get_status(object_id) == "valid"
        else:
            return False

    @staticmethod
    def is_object_known(object_id):
        """ Takes an object id and returns True if the object is known, False otherwise"""
        return object_id in ObjectHandler.id_to_index

    # Saving and loading objects from file
    @staticmethod
    def save_objects():
        """ Saves the objects to the file """
        try:
            with open(ObjectHandler.objects_file, "w") as f:
                json.dump(ObjectHandler.objects, f, indent=4)
            f.close()
        except Exception as e:
            LogPlus().error(f"| ERROR | ObjectHandler | save_objects failed | {e}")

    @staticmethod
    def load_objects():
        """ Loads the objects from the file and updates the id_to_index dictionary """
        try:
            with open(ObjectHandler.objects_file, "r") as f:
                ObjectHandler.objects = json.load(f)
            ObjectHandler.update_id_to_index()
        except Exception as e:
            ObjectHandler.objects = DEFAULT_OBJECTS
            ObjectHandler.save()
            LogPlus.error(f"| ERROR | ObjectHandler | load_objects failed | {e}")

    @staticmethod
    def get_height(block_id):
        """ Returns the height of the block with the given id """
        try:
            block_json = ObjectHandler.get_object(block_id)
            coinbase_txid = block_json[txids_key][0]
            coinbase_tx_json = ObjectHandler.get_object(coinbase_txid)
            return coinbase_tx_json[height_key]
        except Exception as e:
            LogPlus.error(f"| ERROR | ObjectHandler | get_height failed | {e}")
            return -1

    @staticmethod
    def get_orginal_sender(txid):
        """ Returns the original sender address of the transaction with the given id """
        try:
            tx_json = ObjectHandler.get_object(txid)
            if tx_json is not None and sender_key in tx_json:
                return tx_json[sender_key]
            else:
                return None
        except Exception as e:
            LogPlus.error(f"| ERROR | ObjectHandler | get_orginal_sender failed | {e}")
            return None

    # Multithreaded auto save

    @staticmethod
    def save():
        """ Saves the objects by adding them to the auto save queue """
        try:
            ObjectHandler.auto_save_queue.put(ObjectHandler.objects)
        except Exception as e:
            LogPlus.error(f"| ERROR | ObjectHandler | save failed | {e}")

    @staticmethod
    def start_auto_save():
        """ Starts the auto save thread """
        save_thread = Thread(target=ObjectHandler.auto_save)
        save_thread.start()

    @staticmethod
    def auto_save():
        """ Auto saves the objects every 5 seconds """
        while True:
            if not ObjectHandler.auto_save_queue.empty():
                # get last object from queue
                while not ObjectHandler.auto_save_queue.empty():
                    item = ObjectHandler.auto_save_queue.get()
                # save object
                ObjectHandler.save_to_file(copy.deepcopy(item))
            # sleep for 5 seconds
            time.sleep(AUTO_SAVE_INTERVAL)

    @staticmethod
    def save_to_file(object_list):
        """ Saves the given object_list set to the object_list file"""
        try:
            with open(OBJECTS_FILE, "w") as f:
                json.dump(object_list, f, indent=4)
        except Exception as e:
            LogPlus.error(f"| ERROR | Couldn't save objects | {e} ")


