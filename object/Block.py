import json
import hashlib
import time

from json_canonical import canonicalize

import jsonschema

from utility.json_validation import *
from utility.logplus import LogPlus
from utility.credentials_utility import *

from object.CoinbaseTransaction import CoinbaseTransaction
from object.Transaction import Transaction

from engine.MessageGenerator import MessageGenerator

from config import *
from json_keys import *

from database.ObjectHandler import *
from database.UTXO import *

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
            type_key: "block",
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
    
    def get_type(self):
        return "block" 

    @staticmethod
    def from_json(block_json):
        #jsonschema.validate(block_json, block_schema)
        try:
            jsonschema.validate(block_json, block_schema)
        except jsonschema.exceptions.ValidationError as e:
            LogPlus.error("| ERROR | Block.from_json | " + str(e))
            return None
        block = Block(
            block_json[txids_key],
            block_json[nonce_key],
            block_json[miner_key],
            block_json[note_key],
            block_json[previd_key],
            block_json[created_key],
            block_json[T_key]
        )
        return block

    def verify(self):
        """
        - ✅ Create logic to represent a block ✅ 2022-11-24
        - ✅ Check that the block contains all required fields and that they are of the format specified
        - ✅ Ensure the target is the one required, i.e. `00000002af000000000000000000000000000000000000000000000000000000`
        - ✅ Check the proof-of-work.
        - ✅ Check that for all the txids in the block, you have the corresponding transaction in your local object database. If not, then send a `getobject` message to your peers in order to get the transaction.
        - ✅ For each transaction in the block, check that the transaction is valid, and update your UTXO set based on the transaction. More details on this in Exercise B:. If any transaction is invalid, the whole block will be considered invalid.
        - ✅ Check for coinbase transactions. There can be at most one coinbase transaction in a block. If present, then the txid of the coinbase transaction must be at index 0 in txids. The coinbase transaction cannot be spent in another transaction in the same block.
        - ✅ Validate the coinbase transaction if there is one.
        - ✅ Check that the coinbase transaction has no inputs, exactly one output and a height. Check that the height and the public key are of the valid format.
        - ✅ Verify the law of conservation for the coinbase transaction. The output of the coinbase transaction can be at most the sum of transaction fees in the block plus the block reward. In our protocol, the block reward is a constant 50 × 1012 picaker. The fee of a transaction is the sum of its input values minus the sum of its output values.
        - ✅ When you receive a block object from the network, validate it. If valid, then store the block in your local database and gossip the block.
        """

        missing_data = []

        try:
            # Ensure the target is the one required
            if self.t != "00000002af000000000000000000000000000000000000000000000000000000":
                LogPlus.info("| INFO | Block.verify | Target is not the one required")
                return {"result": "False"}
            
            # Check the proof-of-work: blockid < target
            blockid = self.get_id()
            if int(blockid, 16) >= int(self.t, 16):
                LogPlus.info("| INFO | Block.verify | Proof-of-work is not valid")
                return {"result": "False"}

        except Exception as e:
            LogPlus.error(f"| ERROR | Block.verify | A |  Exception: " + str(e))
            return {"result": "False"}

        # Check for previous block
        # If it doesn't exist, then send a getobject message to your peers in order to get the previous block.
        # and store current block for later verification
        try:
            # check if its valid, pending or invalid
            if ObjectHandler.get_status(self.previd) == "invalid":
                LogPlus.info("| INFO | Block.verify | Previous block is invalid")
                return {"result": "False"}
            elif ObjectHandler.get_status(self.previd) == "pending":
                LogPlus.info("| INFO | Block.verify | Previous block is pending")
                return {"result": "data missing", "ids": [self.previd]}
            elif ObjectHandler.get_status(self.previd) == "valid":
                LogPlus.info("| INFO | Block.verify | Previous block is valid")
            else:
                LogPlus.info("| INFO | Block.verify | Previous block is not found")
                missing_data.append(self.previd)
        except Exception as e:
            LogPlus.info("| INFO | Block.verify | B | Exception: " + str(e))
            return {"result": "False"}

        # in case it passes the block validation
        try:
            unknown_txids = []

            for txid in self.txids:
                if ObjectHandler.get_object(txid) is None:
                    unknown_txids.append(txid)

            if len(unknown_txids) > 0:
                missing_data += unknown_txids
        except Exception as e:
            LogPlus.info("| INFO | Block.verify | C | Exception: " + str(e))
            return {"result": "False"}

        if len(missing_data) > 0:
            return {"result": "data missing", "ids": missing_data}

        try:
            # Load UTXO of previous block
            prev_utxo = UTXO.get_utxo(self.previd)
            #LogPlus.debug(f"| DEBUG | Block.verify | prev_utxo: {prev_utxo}")
            if prev_utxo is None:
                LogPlus.info("| Info | Block.verify | D | Previous UTXO is not found")
                return {"result": "data missing", "ids": []}
        except Exception as e:
            LogPlus.info("| INFO | Block.verify | Exception: " + str(e))

        # There can be at most one coinbase transaction in a block. If present, then the txid of the coinbase transaction must be at index 0 in txids.
        # Check if the first transaction is a coinbase transaction
        first_txid = self.txids[0]
        first_tx_json = ObjectHandler.get_object(first_txid)

        try:
            jsonschema.validate(first_tx_json, coinbase_transaction_schema)
            # validate the coinbase transaction
            coinbase_tx = CoinbaseTransaction.from_json(first_tx_json)
            validity = coinbase_tx.verify()
            if validity["result"] == "False":
                LogPlus.error(f"| ERROR | Block.verify | 1 | A transaction is not valid | {self.get_json()}")
                return {"result": "False"}
        except jsonschema.exceptions.ValidationError:
            LogPlus.error("| ERROR | Block.verify | E | The first transaction is not a coinbase transaction")
            return {"result": "False" }

        # verify height (should be equal to the height of the previous block + 1)
        prev_block = ObjectHandler.get_object(self.previd)
        if prev_block is None:
            LogPlus.error("| ERROR | Block.verify | F | Previous block is not found")
            return {"result": "False"}
        try:
            prev_coinbase_txid = prev_block[txids_key][0]
            prev_coinbase_tx = CoinbaseTransaction.from_json(ObjectHandler.get_object(prev_coinbase_txid))
            if prev_coinbase_tx.height + 1 != coinbase_tx.height:
                LogPlus.error("| ERROR | Block.verify | G | Height is not valid")
                return {"result": "False"}
        except Exception as e:
            LogPlus.info(f"| INFO | Block.verify | F2 | Previous block coinbase is not found, it's most likely the genesis block | {prev_block}")

        # verify the timestamp (should be greater than the timestamp of the previous block and less than the current time)
        if prev_block[created_key] >= self.created or self.created > time.time():
            LogPlus.error("| ERROR | Block.verify | H | Timestamp is not valid")
            return {"result": "False"}

        LogPlus.info("| INFO | Block.verify | Check 1H")
        
        # verify remaining transactions
        try:
            inputs = []
            for txid in self.txids[1:]:
                tx_json = ObjectHandler.get_object(txid)
                try:
                    jsonschema.validate(tx_json, regular_transaction_schema)
                    validity = Transaction.from_json(tx_json).verify()
                    if validity["result"] == "False":
                        LogPlus.error(f"| ERROR | Block.verify | 2 | A transaction is not valid | {self.get_json()}")
                        return {"result": "False"}

                    # check if the inputs of the transaction are in the prev UTXO set
                    for input in tx_json[inputs_key]:
                        LogPlus.debug(f"| DEBUG | Block.verify | input: {input}")
                        # prev_utxo is an array of dicts, where the key is the txid and the value is an array of outputs
                        if input[outpoint_key][txid_key] not in prev_utxo.keys():
                            LogPlus.error(f"| ERROR | Block.verify | 3 | A transaction is not valid | txid not available | {self.get_json()} | {prev_utxo}")
                            return {"result": "False"}
                        else:
                            # check if the output index is valid
                            if not input[outpoint_key][index_key] in prev_utxo[input[outpoint_key][txid_key]]:
                                LogPlus.error(f"| ERROR | Block.verify | 4 | A transaction is not valid | index not available | {self.get_json()}")
                                return {"result": "False"}

                    # check if any input is used twice
                    tx_json = ObjectHandler.get_object(txid)
                    for input in tx_json[inputs_key]:
                        if input in inputs:
                            LogPlus.error(f"| ERROR | Block.verify | An input is used twice")
                            return {"result": "False"}
                        inputs.append(input)
                    
                except jsonschema.exceptions.ValidationError:
                    # This should not happen, coinbase transactions have to be at the beginning of the block
                    return { "result": "False" }

            # Check is the value of the coinbase transaction is valid
            # The output of the coinbase transaction can be at most the sum of transaction fees in the block plus the block reward.
            # In our protocol, the block reward is a constant 50 × 1012 picaker.
            # The fee of a transaction is the sum of its input values minus the sum of its output values.
        except Exception as e:
            LogPlus.info("| ERROR | Block.verify | I | Exception: " + str(e))

        try:
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
            if tx_fees + (BLOCK_REWARD) < first_tx_json[outputs_key][0][value_key]:
                LogPlus.error(f"| ERROR | Block.verify | The coinbase transaction value is not valid")
                #LogPlus.info(f"| INFO | Block.verify | The coinbase transaction value is invalid |{self.get_id()}")
                return { "result": "False" }

            # The block is valid

        except Exception as e:
            LogPlus.info("| INFO | Block.verify | J | Exception: " + str(e))

        try:

            new_utxo = prev_utxo # we'll update this as we go along
            # it's a list of dicts
            # each dict has a key "txid" and an array of indexes "indexes" that are still unspent

            # Loop through all transactions in the block
            # First loop to add all new outputs to the UTXO
            # Second loop to remove all inputs from the UTXO
            for txid in self.txids:
                tx_json = ObjectHandler.get_object(txid)
                # get an array containing the indexes (0, 1, 2, ...) of the outputs that are still unspent
                indexes = [i for i in range(len(tx_json[outputs_key]))]
                new_utxo.append({txid: indexes})

            for txid in self.txids:
                tx_json = ObjectHandler.get_object(txid)
                if tx_json[inputs_key] is not None:
                    for input in tx_json[inputs_key]:
                        # remove the input from the UTXO
                        for outputs in new_utxo:
                            if input[txid_key] in outputs:
                                outputs[input[txid_key]].remove(input[index_key])
                                # remove the dict if there are no more unspent outputs
                                if len(outputs[input[txid_key]]) == 0:
                                    new_utxo.remove(outputs)
                                break
        except Exception as e:
            LogPlus.info("| INFO | Block.verify | K | Exception: " + str(e))

        # save the new UTXO set
        # UTXO.sets[self.get_id()] = new_utxo
        # UTXO.save()

        return { "result": "True" }
