import json
import json_canonical
import hashlib

from utility.logplus import LogPlus
from engine.Object import Object

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

    def __init__(self, objects_file="objects.json"):
        self.id_to_index = {}
        self.objects_file = objects_file
        self.objects = []
        self.load_objects()
        self.update_id_to_index()

    def update_id_to_index(self):
        self.id_to_index = {}
        for i in range(len(self.objects)):
            object_id = Object.get_id_from_json(self.objects[i])
            self.id_to_index[object_id] = i

    def add_object(self, obj):
        self.objects.append(obj)
        self.id_to_index[Object.get_id_from_json(obj)] = len(self.objects) - 1
        self.save_objects()

    def get_object(self, id):
        if id in self.id_to_index:
            return self.objects[self.id_to_index[id]]
        else:
            # refresh id_to_index and try again (just in case)
            self.update_id_to_index()
            if id in self.id_to_index:
                return self.objects[self.id_to_index[id]]
            else:
                return None

    def is_object_known(self, object_id):
        return object_id in self.id_to_index.keys()

    def validate_object(self, obj):
        if obj["type"] == "transaction":
            return self.validate_transaction(obj)
        elif obj["type"] == "block":
            return self.validate_block(obj)
        else:
            return False

    def validate_transaction(self, tx):
        # check if its a coinbase transaction
        if "height" in tx:
            return self.validate_coinbase_transaction(tx)

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

    def validate_coinbase_transaction(self, tx):
        try:
            # TODO: This will be part of a future assignment. For Task 2 it's fine like this.
            return ObjectHandler.validate_outputs(tx["outputs"])
        except Exception as e:
            LogPlus().error(f"| ERROR | ObjectHandler | validate_coinbase_transaction | {e}")
            return False

    def validate_block(self, block):
        # TODO: This will be part of a future assignment. For Task 2 it's fine like this.
        return True

    def validate_inputs(self, inputs):
        # check if there is at least one input
        if len(inputs) < 1:
            return False
        # check if all inputs are valid
        for input in inputs:
            if not self.validate_input(input):
                return False
        # if all checks passed, return True
        return True

    def validate_input(self, input):
        # check if the input outpoint is valid
        if not self.validate_outpoint(input["outpoint"]):
            return False
        # check if the input signature is valid
        if not self.validate_signature(input["sig"]):
            return False
        # if all checks passed, return True
        return True

    def validate_outpoint(self, outpoint):
        # check if the outpoint txid is valid
        if not self.validate_txid(outpoint["txid"]):
            return False
        # check if the outpoint index is valid
        if not self.validate_index(outpoint["index"]):
            return False
        # if all checks passed, return True
        return True

    def validate_txid(self, txid):
        # check if the txid is a valid sha256 hash
        try:
            hashlib.sha256(bytes.fromhex(txid)).hexdigest()
        except Exception as e:
            return False
        # check if the txid is in the object list
        if not self.get_object(txid):
            return False
        # if all checks passed, return True
        return True

    def validate_index(self, index, txid):
        # check if the index is an integer
        if not isinstance(index, int):
            return False
        # check if the index is valid
        if index < 0 or index >= len(self.get_object(txid)["outputs"]):
            return False
        # if all checks passed, return True
        return True

    # This is just format validation, not signature validation (therefore all static)

    @staticmethod
    def validate_outputs(self, outputs):
        for output in outputs:
            if not self.validate_output(output):
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

    def save_objects(self):
        try:
            with open(self.objects_file, "w") as f:
                json.dump(self.objects, f)
        except Exception as e:
            LogPlus().error(f"| ERROR | ObjectHandler | save_objects failed | {e}")

    def load_objects(self):
        try:
            with open(self.objects_file, "r") as f:
                self.objects = json.load(f)
        except Exception as e:
            LogPlus().error(f"| ERROR | ObjectHandler | load_objects failed | {e}")







