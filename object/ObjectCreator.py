from object.Transaction import Transaction
from object.CoinbaseTransaction import CoinbaseTransaction
from object.Block import Block

from json_keys import *

from utility.TimeTracker import TimeTracker


# apparently this is the way to do it, to avoid circular imports

# This is the object creator, it creates objects from JSON
class ObjectCreator:
    @staticmethod
    def create_object(json_object, validate_json=True):
        TimeTracker.start("create_object")
        if json_object[type_key] == "transaction":
            if "height" in json_object: # check if it's a coinbase transaction
                try:
                    coinbase = CoinbaseTransaction.from_json(json_object, validate_json)
                    TimeTracker.checkpoint("create_object", "coinbase transaction created")
                    TimeTracker.end("create_object")
                    return coinbase
                except Exception as e:
                    raise Exception(f"Invalid coinbase transaction: {e}")
            else:
                try:
                    tx = Transaction.from_json(json_object, validate_json)
                    TimeTracker.checkpoint("create_object", "transaction created")
                    TimeTracker.end("create_object")
                    return tx
                except Exception as e:
                    raise Exception(f"Invalid regular transaction: {e}")
        elif json_object[type_key] == "block":
            try:
                block = Block.from_json(json_object, validate_json)
                TimeTracker.checkpoint("create_object", "block created")
                TimeTracker.end("create_object")
                return block
            except Exception as e:
                raise Exception(f"Invalid block: {e}")
        else:
            raise Exception("Invalid object type")
