from object.Transaction import Transaction
from object.CoinbaseTransaction import CoinbaseTransaction
from object.Block import Block


# apparently this is the way to do it, to avoid circular imports

# This is the object creator, it creates objects from JSON
class ObjectCreator:
    @staticmethod
    def create_object(json_object):
        if json_object[type_key] == "transaction":
            if "height" in json_object: # check if it's a coinbase transaction
                try:
                    return CoinbaseTransaction.from_json(json_object)
                except Exception as e:
                    raise Exception(f"Invalid coinbase transaction: {e}")
            else:
                try:
                    return Transaction.from_json(json_object)
                except Exception as e:
                    raise Exception(f"Invalid regular transaction: {e}")
        elif json_object[type_key] == "block":
            try:
                return Block.from_json(json_object)
            except Exception as e:
                raise Exception(f"Invalid block: {e}")
        else:
            raise Exception("Invalid object type")
