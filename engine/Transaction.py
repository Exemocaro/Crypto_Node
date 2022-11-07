import copy
import hashlib
import json
from nacl.signing import *
from json_canonical import canonicalize

from config import *
from engine.Object import Object


# Format of a regular transaction:
# {
#     "type": "transaction",
#     "inputs": [
#         {
#             "txid": sha256 hash of previous transaction,
#             "index": index of output in previous transaction
#         },
#         "sig": signature of the input, created with the private key of the owner of the outpoint
#     ],
#     "outputs": [
#         {
#             "pubkey": public key of the owner of the recipient,
#             "value": amount of coins, in picaker (1 ker = 10^12 picaker)
#         }
#     ]
# }

class Transaction(Object):

    def __init__(self, inputs, outputs):
        self.inputs = inputs
        self.outputs = outputs

    @staticmethod
    def from_json(tx_json):
        # create a transaction from a json representation
        tx_inputs = tx_json["inputs"]
        tx_outputs = tx_json["outputs"]
        return Transaction(tx_inputs, tx_outputs)

    def check_signature(self, ):
        # check if the signature is valid
        # we need to check if the signature is valid for each tx_input
        cleared_copy = self.remove_signatures()
        for tx_input in self.inputs:
            # get the public key of the owner of the outpoint
            outpoint = tx_input["outpoint"]
            txid = outpoint["txid"]
            index = outpoint["index"]
            # get the transaction with id txid
            previous_tx = OBJECT_HANDLER.get_transaction(txid)
            if previous_tx is None:
                return False
            # get the output at index index
            output = previous_tx.outputs[index]
            # get the public key of the owner of the output
            pubkey = output["pubkey"]
            # get the signature of the tx_input
            sig = tx_input["sig"]
            # check if the signature is valid
            if not self.verify_signature(cleared_copy, pubkey, sig):
                return False

        return True

    def verify_signature(self, pubkey, sig):
        # verify the signature
        no_sig_tx_json = self.remove_signatures().get_json()
        print("no_sig_tx_json: ", no_sig_tx_json)
        # make signature bytes if it is not already
        if type(sig) is str:
            sig = sig.encode()
        combined = canonicalize(no_sig_tx_json) + sig
        print("combined: ", combined)
        try:
            VerifyKey(pubkey).verify(combined)
            return True
        except Exception as e:
            return False

    # To check if a signature is valid, we need to remove the signature from the input
    def remove_signatures(self):
        # remove the signatures from the transaction
        tx_copy = copy.deepcopy(self)
        for tx_input in tx_copy.inputs:
            tx_input["sig"] = None
        return tx_copy

    def get_json(self):
        # get the json representation of the transaction
        tx_json = {
            "type": "object",
            "object": {
                "type": "transaction",
                "inputs": self.inputs,
                "outputs": self.outputs
            }
        }
        return tx_json

