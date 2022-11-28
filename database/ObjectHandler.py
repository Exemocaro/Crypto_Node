import json
import json_canonical
import hashlib

from colorama import Fore, Style

from utility.logplus import LogPlus

from object.Object import Object
#from object.ObjectCreator import ObjectCreator

from config import *

GENESIS_BLOCK = {
    "T": "00000002af000000000000000000000000000000000000000000000000000000",
    "created": 1624219079,
    "miner": "dionyziz",
    "nonce": "0000000000000000000000000000000000000000000000000000002634878840",
    "note": "The Economist 2021−06−20: Crypto−miners are probably to blame for the graphics−chip shortage",
    "previd": None,
    "txids ": [],
    "type": "block"
}


# This class handles all objects
# Objects can be either transactions or blocks
# The type of the object is stored in the object itself in the "type" field
# structure of a regular transaction:
# {
#     "type": "transaction",
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
#     "type": "transaction",
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
#     "type": "block",
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
            object_id = Object.get_id_from_json(ObjectHandler.objects[i])
            ObjectHandler.id_to_index[object_id] = i

    @staticmethod
    def add_object(obj):
        """# check if the obj is a json
        if type(obj) is dict:
            try:
                # check if the object can be initialized -> valid json
                obj = Object.from_json(obj)
            except Exception as e:
                LogPlus.error("| ERROR | ObjectHandler.add_object | " + str(e))
                return False

        try:
            # check if the object is valid
            obj.verify()
        except Exception as e:
            LogPlus.error("| ERROR | ObjectHandler.add_object | Verification failed | " + str(e))
            return False
        """
        try:
            ObjectHandler.objects.append(obj.get_json())
            ObjectHandler.id_to_index[obj.get_id()] = len(ObjectHandler.objects) - 1
            ObjectHandler.save_objects()
        except Exception as e:
            LogPlus.error("| ERROR | ObjectHandler.add_object | " + str(e))
            return False

    @staticmethod
    def get_object(object_id):
        if object_id in ObjectHandler.id_to_index:
            return ObjectHandler.objects[ObjectHandler.id_to_index[object_id]]
        else:
            # refresh id_to_index and try again (just in case)
            ObjectHandler.update_id_to_index()
            if object_id in ObjectHandler.id_to_index:
                return ObjectHandler.objects[ObjectHandler.id_to_index[object_id]]
            else:
                return None

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
