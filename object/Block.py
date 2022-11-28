import json
import hashlib
from json_canonical import canonicalize

import jsonschema

from utility.json_validation import *
from utility.logplus import LogPlus
from utility.credentials_utility import *

from object.CoinbaseTransaction import CoinbaseTransaction
from object.Transaction import Transaction

from engine.MessageGenerator import MessageGenerator

from config import *

from database.ObjectHandler import *

from network.NodeNetworking import *

class Block:

    def __init__(self, txids, nonce, miner, note, previd, created, t):
        self.txids = txids
        self.nonce = nonce
        self.miner = miner
        self.note = note
        self.previd = previd
        self.created = created
        self.t = t

    def get_json(self):
        block_json = {
            "type": "block",
            "txids": self.txids,
            "nonce": self.nonce,
            "miner": self.miner,
            "note": self.note,
            "previd": self.previd,
            "created": self.created,
            "T": self.t
        }
        return block_json

    def get_id(self):
        block_json = self.get_json()
        canonical_block_json = canonicalize(block_json)
        blockid = hashlib.sha256(canonical_block_json).hexdigest()
        return blockid

    @staticmethod
    def from_json(block_json):
        jsonschema.validate(block_json, block_schema)
        block = Block(
            block_json["txids"],
            block_json["nonce"],
            block_json["miner"],
            block_json["note"],
            block_json["previd"],
            block_json["created"],
            block_json["T"]
        )
        return block

    def verify(self):
        """
        - [x] Create logic to represent a block ✅ 2022-11-24
        - [x] Check that the block contains all required fields and that they are of the format specified
        - [x] Ensure the target is the one required, i.e. `00000002af000000000000000000000000000000000000000000000000000000`
        - [x] Check the proof-of-work.
        - [~] Check that for all the txids in the block, you have the corresponding transaction in your local object database. If not, then send a `getobject` message to your peers in order to get the transaction.
        - [ ] For each transaction in the block, check that the transaction is valid, and update your UTXO set based on the transaction. More details on this in Exercise B:. If any transaction is invalid, the whole block will be considered invalid.
        - [x] Check for coinbase transactions. There can be at most one coinbase transaction in a block. If present, then the txid of the coinbase transaction must be at index 0 in txids. The coinbase transaction cannot be spent in another transaction in the same block.
        - [x] Validate the coinbase transaction if there is one.
        - [x] Check that the coinbase transaction has no inputs, exactly one output and a height. Check that the height and the public key are of the valid format.
        - [x] Verify the law of conservation for the coinbase transaction. The output of the coinbase transaction can be at most the sum of transaction fees in the block plus the block reward. In our protocol, the block reward is a constant 50 × 1012 picaker. The fee of a transaction is the sum of its input values minus the sum of its output values.
        - [x] When you receive a block object from the network, validate it. If valid, then store the block in your local database and gossip the block.

        """

        # Ensure the target is the one required
        if self.t != "00000002af000000000000000000000000000000000000000000000000000000":
            LogPlus.info("| INFO | Block.verify | Target is not the one required")
            return {"result": "False"}
        
        # Check the proof-of-work: blockid < target
        blockid = self.get_id()
        if int(blockid, 16) >= int(self.t, 16):
            LogPlus.info("| INFO | Block.verify | Proof-of-work is not valid")
            return {"result": "False"}

        unknown_txids = []

        for txid in self.txids:
            if ObjectHandler.get_object(txid) is None:
                unknown_txids.append(txid)

        if len(unknown_txids) > 0:
            return {
                "result": "Information missing",
                "txids": unknown_txids
            }

        # There can be at most one coinbase transaction in a block. If present, then the txid of the coinbase transaction must be at index 0 in txids.
        # Check if the first transaction is a coinbase transaction
        coinbase_txid = self.txids[0]
        coinbase_tx_json = ObjectHandler.get_object(coinbase_txid)

        try:
            jsonschema.validate(coinbase_tx_json, coinbase_transaction_schema)
            # validat the coinbase transaction
            coinbase_tx = CoinbaseTransaction.from_json(coinbase_tx_json)
            coinbase_tx.verify()
        except jsonschema.exceptions.ValidationError:
            # This can happen, just means that the first transaction is not a coinbase transaction
            # But it should be a regular transaction then
            try: 
                jsonschema.validate(coinbase_tx_json, regular_transaction_schema)
            except:
                LogPlus.error("| ERROR | Block.verify | The first transaction is not a coinbase transaction and not a regular transaction either")
                return {"result": "False" }
            pass

        for txid in self.txids[1:]:
            tx_json = ObjectHandler.get_object(txid)
            try:
                jsonschema.validate(tx_json, regular_transaction_schema)
                
            except jsonschema.exceptions.ValidationError:
                # This should not happen, coinbase transactions have to be at the beginning of the block
                return { "result": "False" }

        # TODO: Make sure coinbase transaction wasn't spent in another transaction in the same block

        # Check is the value of the coinbase transaction is valid
        # The output of the coinbase transaction can be at most the sum of transaction fees in the block plus the block reward.
        # In our protocol, the block reward is a constant 50 × 1012 picaker.
        # The fee of a transaction is the sum of its input values minus the sum of its output values.

        # sum up tx fees
        tx_fees = 0
        for txid in self.txids:
            tx_json = ObjectHandler.get_object(txid)
            try:
                tx = Transaction.from_json(tx_json)
                tx_fees += tx.get_fee()
            except Exception as e:
                # this can happen, when the first tx is a coinbase transaction
                pass

        # tx fees + block reward >= coinbase transaction value
        if tx_fees + (50 * 1012) < coinbase_tx_json["outputs"][0]["value"]:
            LogPlus.info(f"| INFO | Block.verify | The coinbase transaction value is invalid |{self.get_id()}")
            return { "result": "False" }

        # The block is valid

        # Since it's valid, before sending back the result we should check if we have all txids with us, and if not ask for them
        for object in ObjectHandler.objects: # fetch our known transactions
            if object["type"] == "transaction":
                for input in object.inputs:
                    outpoint = input["outpoint"]
                    transaction_txid = outpoint["txid"]
                    if transaction_txid not in self.txids:
                        # then this means that we have some transactions in the block which are not present in our database
                        # so we have to request them to other people

                        # TODO: implement sending the data to every node
                        # I think it's working, but I'm not sure
                        res = MessageGenerator.generate_getobject_message()
                        if res is None:
                            continue
                        NodeNetworking.send_to_all_nodes(res)

        return { "result": "True" }
