import copy
import hashlib
import json

from colorama import Fore, Style

import json_canonical
import jsonschema

from nacl.signing import VerifyKey, SigningKey

from config import *
from engine.Object import Object
from database.ObjectHandler import ObjectHandler
from utility.json_validation import regular_transaction_schema
from utility.logplus import LogPlus

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

    # create a transaction from a json representation
    @staticmethod
    def from_json(tx_json):
        # this will raise an exception if the json is invalid
        jsonschema.validate(instance=tx_json, schema=regular_transaction_schema)
        # without the validation, the inputs could contain invalid data and cause errors later
        tx_inputs = tx_json["inputs"]
        tx_outputs = tx_json["outputs"]
        return Transaction(tx_inputs, tx_outputs)

    def get_json(self):
        try:
            # get the json representation of the transaction
            tx_json = {
                "type": "transaction",
                "inputs": self.inputs,
                "outputs": self.outputs
            }
            return tx_json
        except Exception as e:
            LogPlus.error(f"| ERROR | Transaction.get_json | {e}")
            return None

    def copy_without_sig(self):
        try:
            # create a copy of the transaction without the signatures
            # this is used to verify the signatures
            tx_copy = copy.deepcopy(self)
            for input in tx_copy.inputs:
                input["sig"] = None
            return tx_copy
        except Exception as e:
            LogPlus.error(f"| ERROR | Transaction.copy_without_sig | {e}")
            return None

    def verify(self):
        # we know that the format is valid
        # Go step by step like in Task 2

        try:

            sum_input = 0

            for input in self.inputs:
                # 1. Check that each input is valid (txid exists, index is valid)
                # Check that the txid exists
                outpoint = input["outpoint"]
                txid = outpoint["txid"]
                tx = ObjectHandler.get_object(txid)
                if tx is None:
                    LogPlus.warning("| WARNING | Transaction.verify | input txid does not exist")
                    return False

                # Check that the index is valid
                index = outpoint["index"]
                if index >= len(tx["outputs"]):
                    LogPlus.warning("| WARNING | Transaction.verify | input index is invalid")
                    return False

                # 2. Check that each input is signed by the owner of the outpoint
                # Get the public key of the owner of the outpoint
                outpoint = tx["outputs"][index]
                pubkey = outpoint["pubkey"]

                # get the pubkey bytes
                pubkey_bytes = bytes.fromhex(pubkey)
            
                # Get the signature of the input
                sig = input["sig"]

                # Check that the signature is valid
                combined = bytes.fromhex(sig) + json_canonical.canonicalize(self.copy_without_sig().get_json())
                try:
                    print(Fore.LIGHTMAGENTA_EX + str(pubkey_bytes) + Style.RESET_ALL)
                    print(len(pubkey_bytes))
                    print(Fore.LIGHTMAGENTA_EX + str(combined) + Style.RESET_ALL)
                    VerifyKey(pubkey_bytes).verify(combined) # will raise an exception if the signature is invalid
                except Exception as e:
                    LogPlus.warning(f"| WARNING | Transaction.verify | input signature is invalid | {e}")
                    return False

                # get the sum already, will be checked in step 4
                sum_input += outpoint["value"]

            sum_output = 0

            # 3. Check that output pubkeys are valid (value is >= 0, already checked by jsonschema)
            for output in self.outputs:
                pubkey = output["pubkey"]
                # should be 64 hex characters
                try:
                    int(pubkey, 16)
                except ValueError:
                    LogPlus.warning("| WARNING | Transaction.verify | output pubkey is invalid")
                    return False

                # get the sum already, will be checked in step 4
                sum_output += output["value"]

            # 4. Check that the sum of the inputs is equal to the sum of the outputs. Output can be equal or smaller than input
            if sum_input < sum_output:
                LogPlus.warning("| WARNING | Transaction.verify | sum of inputs is smaller than sum of outputs")
                return False

            # 5. Check that the transaction is not a double spend
            # TODO : This is not mentioned in the task, but it's required to make sense
            # go through all saved transactions and check if the txid is already used as an input
            #print(Fore.LIGHTMAGENTA_EX + "I think the problem is here..." + Style.RESET_ALL)
            #used_inputs = [input["txid"] for input in tx.inputs]
            #print(Fore.LIGHTMAGENTA_EX + "... nah nevermind :)" + Style.RESET_ALL)
#
            #for tx in ObjectHandler.get_all_objects():
            #    try:
            #        tx = Transaction.from_json(tx)
            #    except jsonschema.exceptions.ValidationError:
            #        continue
            #    for input in tx.inputs:
            #        if input["txid"] in used_inputs:
            #            LogPlus.warning("| WARNING | Transaction.verify | double spend")
            #            return False
#
            return True
        except Exception as e:
            LogPlus.error(f"| ERROR | Transaction.verify | {e}")
            return False

    def __str__(self):
        return f"Transaction(inputs={self.inputs}, outputs={self.outputs})"


