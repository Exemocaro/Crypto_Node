import json
import json_canonical
import hashlib
import jsonschema

from abc import ABC, abstractmethod

from colorama import Fore, Style

from json_keys import *

from utility.json_validation import coinbase_transaction_schema

from object.Object import Object

from database.ObjectHandler import ObjectHandler

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


class CoinbaseTransaction(Object):

    def __init__(self, height, outputs):
        self.height = height
        self.outputs = outputs

    # create a transaction from a json representation
    @staticmethod
    def from_json(tx_json):
        # this will raise an exception if the json is invalid
        jsonschema.validate(instance=tx_json, schema=coinbase_transaction_schema)
        tx_height = tx_json[height_key]
        tx_outputs = tx_json[outputs_key]
        coinbase_tx = CoinbaseTransaction(tx_height, tx_outputs)
        return coinbase_tx

    def get_type(self):
        return "coinbase"

    def get_json(self):
        # return a json representation of the transaction
        return {
            type_key: "transaction",
            "height": self.height,
            "outputs": self.outputs
        }

    def verify(self):
        return {"result": "True"}
        """# we can only verify them, if they are in a block
        block = ObjectHandler.get_block_containing_object(self)
        if block is None:
            return {"result": "data missing"}
        # verify the value of the coinbase transaction
        # the value of the coinbase transaction is the block reward"""
        
    def __str__(self):
        return "CoinbaseTransaction(height={}, outputs={})".format(self.height, self.outputs)
