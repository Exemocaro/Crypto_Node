import copy
import hashlib
import json

from colorama import Fore, Style

import json_canonical
import jsonschema

from nacl.signing import VerifyKey, SigningKey

from config import *
from json_keys import *

from object.Object import Object

from database.ObjectHandler import ObjectHandler
from database.UTXO import *

from utility.json_validation import regular_transaction_schema
from utility.logplus import LogPlus
from utility.Exceptions import ValidationException

# Format of a regular transaction:
"""
{
    "type " : " transaction " ,
    " inputs " : [
        {
            "outpoint ":{
                "txid" : " f71408bf847d7dd15824574a7cd4afdfaaa2866286910675cd3fc371507aa196" ,
                "index": 0
            },
            " sig":"3869a9ea9e7ed926a7c8b30fb71f6ed151a132b03fd5dae764f015c98271000e7da322dbcfc97af7931c23c0fae060e102446ccff0f54ec00f9978f3a69a6f0f"
        }
    ] ,
    "outputs " : [
        {
            "pubkey":"077a2683d776a71139fd4db4d00c16703ba0753fc8bdc4bd6fc56614e659cde3" ,
            "value":5100000000
        }
    ]
}
"""


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
        tx_inputs = tx_json[inputs_key]
        tx_outputs = tx_json[outputs_key]
        return Transaction(tx_inputs, tx_outputs)
    
    def get_type(self):
        return "transaction" 

    def get_json(self):
        try:
            # get the json representation of the transaction
            tx_json = {
                type_key: "transaction",
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
                input[sig_key] = None
            return tx_copy
        except Exception as e:
            LogPlus.error(f"| ERROR | Transaction.copy_without_sig | {e}")
            return None

    def verify(self):
        # we know that the format is valid
        # Go step by step like in Task 2

        try:
            for input in self.inputs:
                # 1. Check that each input is valid (txid exists, index is valid)
                # Check that the txid exists
                outpoint = input[outpoint_key]
                txid = outpoint[txid_key]
                tx = ObjectHandler.get_object(txid)
                if tx is None:
                    LogPlus.warning("| WARNING | Transaction.verify | input txid does not exist")
                    return {"result": "pending", "missing": [txid], "pending": []}

                # Check that the index is valid
                index = outpoint[index_key]
                if index >= len(tx[outputs_key]):
                    raise ValidationException(f"Index is invalid: {index}")

                # 2. Check that each input is signed by the owner of the outpoint
                # Get the public key of the owner of the outpoint
                output = tx[outputs_key][index]
                pubkey = output[pubkey_key]
                sig = input[sig_key]

                self.verify_signature(pubkey, sig)

            # 3. Check that output pubkeys are valid (value is >= 0, already checked by jsonschema)
            for output in self.outputs:
                pubkey = output[pubkey_key]
                Transaction.verify_pubkey_format(pubkey)

            # 4. Check that the sum of the inputs is equal to the sum of the outputs. Output can be equal or smaller than input
            self.verify_values()

            # 5. Check that the transaction doesn't contain any input twice
            self.verify_no_duplicate_inputs()

            return {"result": "valid"}
        except ValidationException as e:
            LogPlus.warning(f"| WARNING | Transaction.verify | {self.get_id()[:10]}... | {e}")
            return {"result": "invalid"}
        except Exception as e:
            LogPlus.error(f"| ERROR | Transaction.verify | {self.get_id()[:10]}... | {e}")
            return {"result": "invalid"}

    def get_fee(self):

        if not self.verify()["result"] == "valid":
            return 0

        # calculate the fee of the transaction
        sum_input = 0
        sum_output = 0

        for input in self.inputs:
            outpoint = input[outpoint_key]
            txid = outpoint[txid_key]
            index = outpoint[index_key]
            tx = ObjectHandler.get_object(txid)
            output = tx[outputs_key][index]
            sum_input += output[value_key]


        for output in self.outputs:
            sum_output += output[value_key]

        return sum_input - sum_output

    def verify_values(self):
        """ Check if the sum of the inputs is equal to the sum of the outputs. 
        Output can be equal or smaller than input"""
        if self.get_fee() < 0:
            raise ValidationException(f"Sum of inputs is smaller than sum of outputs")

    def verify_signature(self, pubkey, sig):
        """verify the signature of the transaction
        pubkey and sig are hex strings"""
        try:
            pubkey_bytes = bytes.fromhex(pubkey)
            sig_bytes = bytes.fromhex(sig)
            tx_bytes = json_canonical.canonicalize(self.copy_without_sig().get_json())
            combined = sig_bytes + tx_bytes
            VerifyKey(pubkey_bytes).verify(sig_bytes)
            return True
        except Exception:
            raise ValidationException(f"Invalid signature: {sig}")

    def verify_no_duplicate_inputs(self):
        """ Check if the transaction contains any input twice """
        # create a set of the inputs
        input_set = set()
        for input in self.inputs:
            input_str = json.dumps(input)
            if input_str in input_set:
                raise ValidationException("Transaction contains duplicate inputs")
            input_set.add(input_str)

    @staticmethod
    def verify_pubkey_format(pubkey):
        """ verify the format of the public key
        should be 64 hex characters """
        try:
            if len(pubkey) != 64:
                return False
            int(pubkey, 16)
        except Exception:
            raise ValidationException(f"Invalid pubkey format: {pubkey}")


    def __str__(self):
        return f"Transaction(inputs={self.inputs}, outputs={self.outputs})"


