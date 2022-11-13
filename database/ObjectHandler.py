import json
import json_canonical
import hashlib

from utility.logplus import LogPlus
from engine.Object import Object

from colorama import Fore, Style

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
        try:
            ObjectHandler.objects.append(obj)
            print(Fore.GREEN + "Object appended" + Style.RESET_ALL)
            ObjectHandler.id_to_index[Object.get_id_from_json(obj)] = len(ObjectHandler.objects) - 1
            print(Fore.GREEN + "Object indexed" + Style.RESET_ALL)
            ObjectHandler.save_objects()
            print(Fore.GREEN + "Objects saved" + Style.RESET_ALL)
        except Exception as e:
            LogPlus.error("| ERROR | ObjectHandler.add_object | " + str(e))


    @staticmethod
    def get_object(id):
        if id in ObjectHandler.id_to_index:
            return ObjectHandler.objects[ObjectHandler.id_to_index[id]]
        else:
            # refresh id_to_index and try again (just in case)
            ObjectHandler.update_id_to_index()
            if id in ObjectHandler.id_to_index:
                return ObjectHandler.objects[ObjectHandler.id_to_index[id]]
            else:
                return None

    @staticmethod
    def is_object_known(object_id):
        return object_id in ObjectHandler.id_to_index.keys()

    @staticmethod
    def validate_object(obj):
        print(obj)
        try:
            if obj["type"] == "transaction":
                return ObjectHandler.validate_transaction(obj)
            elif obj["type"] == "block":
                return ObjectHandler.validate_block(obj)
            else:
                LogPlus.warning(f"| WARNING | ObjectHandler.validate_object | Unknown object type: " + obj["type"])
                return False
        except Exception as e:
            LogPlus.error(f"| ERROR | ObjectHandler.validate_object | {e} | {obj}")
            return False

    @staticmethod
    def validate_transaction(tx):
        # check if its a coinbase transaction
        print(Fore.CYAN + "Validating transaction" + Style.RESET_ALL)
        if "height" in tx:
            print(Fore.CYAN + "Validating coinbase transaction" + Style.RESET_ALL)
            return ObjectHandler.validate_coinbase_transaction(tx)

        # otherwise its a regular transaction
        try:
            # check if inputs and outputs are valid
            if not ObjectHandler.validate_inputs(tx["inputs"]):
                return False
            if not ObjectHandler.validate_outputs(tx["outputs"]):
                return False
            # check if there are no duplicate inputs
            if len(tx["inputs"]) != len(set([json.dumps(i, sort_keys=True) for i in tx["inputs"]])):
                return False
            # check if there are no duplicate outputs
            if len(tx["outputs"]) != len(set([json.dumps(o, sort_keys=True) for o in tx["outputs"]])):
                return False
            # check if the transaction is valid
            if not ObjectHandler.validate_transaction_signature(tx):
                return False
            return True
        except Exception as e:
            LogPlus().error(f"| ERROR | ObjectHandler | validate_transaction | {e}")
            return False

    @staticmethod
    def validate_coinbase_transaction(tx):
        try:
            # TODO: This will be part of a future assignment. For Task 2 it's fine like this.
            # return ObjectHandler.validate_outputs(tx["outputs"])
            return True
        except Exception as e:
            LogPlus().error(f"| ERROR | ObjectHandler | validate_coinbase_transaction | {e}")
            return False

    @staticmethod
    def validate_block(block):
        # TODO: This will be part of a future assignment. For Task 2 it's fine like this.
        return True

    @staticmethod
    def validate_inputs(inputs):
        # check if there is at least one input
        if len(inputs) < 1:
            return False
        # check if all inputs are valid
        for input in inputs:
            if not ObjectHandler.validate_input(input):
                return False
        # if all checks passed, return True
        return True

    @staticmethod
    def validate_input(input):
        # check if the input outpoint is valid
        if not ObjectHandler.validate_outpoint(input["outpoint"]):
            return False
        # check if the input signature is valid
        if not ObjectHandler.validate_signature(input["sig"]):
            return False
        # if all checks passed, return True
        return True

    @staticmethod
    def validate_outpoint(outpoint):
        # check if the outpoint txid is valid
        if not ObjectHandler.validate_txid(outpoint["txid"]):
            return False
        # check if the outpoint index is valid
        if not ObjectHandler.validate_index(outpoint["index"]):
            return False
        # if all checks passed, return True
        return True

    @staticmethod
    def validate_txid(txid):
        # check if the txid is a valid sha256 hash
        try:
            hashlib.sha256(bytes.fromhex(txid)).hexdigest()
        except Exception as e:
            return False
        # check if the txid is in the object list
        if not ObjectHandler.get_object(txid):
            return False
        # if all checks passed, return True
        return True

    @staticmethod
    def validate_index(index, txid):
        # check if the index is an integer
        if not isinstance(index, int):
            return False
        # check if the index is valid
        if index < 0 or index >= len(ObjectHandler.get_object(txid)["outputs"]):
            return False
        # if all checks passed, return True
        return True

    # This is just format validation, not signature validation (therefore all static)

    @staticmethod
    def validate_outputs(outputs):
        for output in outputs:
            if not ObjectHandler.validate_output(output):
                return False
        return True

    @staticmethod
    def validate_output(output):
        # check if the output value is valid (positive integer)
        if output["value"] < 0:
            return False
        # check if the output pubkey is valid
        if not ObjectHandler.validate_pubkey(output["pubkey"]):
            return False
        # if all checks passed, return True
        return True

    @staticmethod
    def validate_pubkey(pubkey):
        # check if the pubkey is valid
        if len(pubkey) != 64:
            return False
        # also check if the pubkey is a valid hex string
        try:
            int(pubkey, 16)
        except ValueError:
            return False

        # if all checks passed, return True
        return True

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


ObjectHandler.load_objects()
ObjectHandler.update_id_to_index()

