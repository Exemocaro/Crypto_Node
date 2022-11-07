import json
import json_canonical
import hashlib

from abc import ABC, abstractmethod
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

    @staticmethod
    def from_json(tx_json):
        # create a transaction from a json representation
        tx_height = tx_json["height"]
        tx_outputs = tx_json["outputs"]
        return CoinbaseTransaction(tx_height, tx_outputs)

    def get_json(self):
        # return a json representation of the transaction
        return {
            "type": "transaction",
            "height": self.height,
            "outputs": self.outputs
        }


