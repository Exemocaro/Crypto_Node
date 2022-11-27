import json
import json_canonical
import hashlib

from abc import ABC, abstractmethod

import jsonschema
from colorama import Fore, Style

from utility.json_validation import coinbase_transaction_schema

from engine.Object import Object

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


class CoinbaseTransaction(Object):

    def __init__(self, height, outputs):
        self.height = height
        self.outputs = outputs

    # create a transaction from a json representation
    @staticmethod
    def from_json(tx_json):
        # this will raise an exception if the json is invalid
        jsonschema.validate(instance=tx_json, schema=coinbase_transaction_schema)
        tx_height = tx_json["height"]
        tx_outputs = tx_json["outputs"]
        coinbase_tx = CoinbaseTransaction(tx_height, tx_outputs)
        return coinbase_tx

    def get_json(self):
        # return a json representation of the transaction
        return {
            "type": "transaction",
            "height": self.height,
            "outputs": self.outputs
        }

    def verify(self):
        return {"result": "True"}

    def __str__(self):
        return "CoinbaseTransaction(height={}, outputs={})".format(self.height, self.outputs)

