import json
import json_canonical
import hashlib

from colorama import Fore, Style

from utility.logplus import LogPlus
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
    objects = []

    @staticmethod
    def update_id_to_index():
        ObjectHandler.id_to_index = {}
        for i in range(len(ObjectHandler.objects)):
            object_id = ObjectHandler.objects[i][txid_key]
            ObjectHandler.id_to_index[object_id] = i

    @staticmethod
    def add_object(obj, validity="valid", type="unknown", missing = [], pending = None):
        try:
            txid = Object.get_id_from_json(obj)
            ObjectHandler.objects.append({
                "txid": txid,
                "validity": validity,
                object_key: obj,
                type_key: type,
                "missing": missing,
                "pending": pending
            })
            ObjectHandler.id_to_index[txid] = len(ObjectHandler.objects) - 1
            ObjectHandler.save_objects()
            ObjectHandler.update_id_to_index()
            """if validity == "valid":
                if UTXO.is_available(self.inputs):
                UTXO.addToSet(self.outputs) # should we add it here?"""

            ObjectHandler.update_pending_objects(txid)

        except Exception as e:
            LogPlus.error("| ERROR | ObjectHandler.add_object | " + str(e))
            return False

    @staticmethod
    def get_object(object_id):
        if object_id in ObjectHandler.id_to_index:
            return ObjectHandler.objects[ObjectHandler.id_to_index[object_id]][object_key]
        else:
            return None
    
    @staticmethod
    def get_pending_objects():
        return [obj[object_key] for obj in ObjectHandler.objects if obj["validity"] == "pending"]

    @staticmethod
    def get_status(object_id):
        if object_id in ObjectHandler.id_to_index:
            return ObjectHandler.objects[ObjectHandler.id_to_index[object_id]]["validity"]
        else:
            return None

    @staticmethod
    def update_pending_objects(object_id = None):
        if object_id == None:
            object_ids = [obj[object_key] for obj in ObjectHandler.objects if obj["validity"] == "valid"]
        else:
            object_ids = [object_id]

        for object_id in object_ids:
            for pending in [obj for obj in ObjectHandler.objects if obj["validity"] == "pending"]:
                if object_id in pending["missing"]:
                    pending["missing"].remove(object_id)
                if object_id == pending["pending"]:
                    pending["pending"] = None


    @staticmethod
    def get_verifiable_objects():
        return [obj[object_key] for obj in ObjectHandler.objects if obj["validity"] == "pending" 
                                                                    and len(obj["missing"]) == 0 
                                                                    and obj["pending"] == None ]


    @staticmethod
    def update_object_status(object_id, validity):
        if object_id in ObjectHandler.id_to_index:
            ObjectHandler.objects[ObjectHandler.id_to_index[object_id]]["validity"] = validity
            ObjectHandler.save_objects()

    @staticmethod
    def set_requirements(object_id, missing, pending):
        if object_id in ObjectHandler.id_to_index:
            index = ObjectHandler.id_to_index[object_id]
            ObjectHandler.objects[index]["missing"] = missing
            ObjectHandler.objects[index]["pending"] = pending
            ObjectHandler.save_objects()

    @staticmethod
    def get_block_containing_object(object_id):
        # get all objects of type block
        blocks = [obj[object_key] for obj in ObjectHandler.objects if obj[type_key] == "block"]
        
        for block in blocks:
            # check if the object is in txids of the block
            if object_id in block[txids_key]:
                return Object.get_id_from_json(block)

    @staticmethod
    def get_chaintip():
        # get all objects of type block
        blocks = [obj[object_key] for obj in ObjectHandler.objects if obj[type_key] == "block" and obj["validity"] == "valid"]

        if len(blocks) <= 1:
            return Object.get_id_from_json(GENESIS_BLOCK)

        # check height in coinbase transaction, return the blockid with the highest height
        return max(blocks, key=lambda block: block[txids_key][0][height_key])[txid_key]
        #return max(blocks, key=lambda block: get_block_height(block))[txid_key]

    @staticmethod
    def get_block_height(object_id):
        try:
            # get block
            block = ObjectHandler.get_object(object_id)
            # get coinbase transaction
            coinbase = block[txids_key][0]
            # return height
            return coinbase[height_key]
        except:
            return -1
        

    @staticmethod
    def is_valid(object_id):
        if object_id in ObjectHandler.id_to_index:
            return ObjectHandler.objects[ObjectHandler.id_to_index[object_id]]["validity"] == "valid"
        else:
            return False

    @staticmethod
    def is_object_known(object_id):
        return object_id in ObjectHandler.id_to_index.keys()

    # Saving and loading objects from file
    @staticmethod
    def save_objects():
        try:
            with open(ObjectHandler.objects_file, "w") as f:
                json.dump(ObjectHandler.objects, f, indent=4)

            f.close()

        except Exception as e:
            LogPlus().error(f"| ERROR | ObjectHandler | save_objects failed | {e}")

    @staticmethod
    def load_objects():
        try:
            with open(ObjectHandler.objects_file, "r") as f:
                ObjectHandler.objects = json.load(f)
        except Exception as e:
            ObjectHandler.objects = []
            ObjectHandler.save_objects()
            LogPlus().error(f"| ERROR | ObjectHandler | load_objects failed | {e}")
