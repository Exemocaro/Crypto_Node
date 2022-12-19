import json
import json_canonical
import hashlib
from colorama import Fore, Style

from utility.logplus import LogPlus

from object.Object import Object

from database.ObjectHandler import ObjectHandler

from config import *
from json_keys import *

# UTXO structure
# {
#   blockid: [
#       {txid, [indexes]}
#   ] 
# }

class UTXO:

    sets = {
        "00000000a420b7cefa2b7730243316921ed59ffe836e111ca3801f82a4f5360e": {} # genesis block
    }
    
    # dict that stores every valid output of valid stored tansactions in json format
    # {block: {txid, [indexes]}}

    # loads the set from the database files
    @staticmethod
    def load_sets():
        # recalculate the set from the database for each block
        #for block in ObjectHandler.get_blocks():
        #    if block.get_id() not in UTXO.sets:
        #        UTXO.sets[block.get_id()] = UTXO.calculate_set(block)
        pass

    @staticmethod
    def clear():
        UTXO.sets = {
            "00000000a420b7cefa2b7730243316921ed59ffe836e111ca3801f82a4f5360e": {} # genesis block
        }

    @staticmethod
    def get_utxo(blockid):
        keys = UTXO.sets.keys()
        if blockid in keys:
            return UTXO.sets[blockid]
        else:
            UTXO.calculate_set(ObjectHandler.get_object(blockid))
            keys = UTXO.sets.keys()
            if blockid in keys:
                return UTXO.sets[blockid]
            else:
                return None

    @staticmethod
    def save():
        # TODO save to file
        pass

    # calculates the set for a given block
    @staticmethod
    def calculate_set(block):

        try:
            # check if its a json object
            if isinstance(block, Object):
                block = block.get_json()
            block_id = Object.get_id_from_json(block)
            # get the previous block
            prev_id = block[previd_key]
            prev_block = ObjectHandler.get_object(prev_id)
            if ObjectHandler.get_status(prev_id) != "valid":
                return
            if prev_block is None:
                prev_set = []
            elif prev_id in UTXO.sets.keys():
                prev_set = UTXO.sets[prev_id]
            else:
                return

            # get the transactions of the block
            txs = block[txids_key]

            # get the coinbase transaction
            coinbase_txid = txs[0]

            new_set = prev_set.copy()

            # add the coinbase transaction to the set
            new_set[coinbase_txid] = [0]

        except Exception as e:
            LogPlus.error(f"| ERROR | UTXO | First | Error calculating set for block {block}: {e}")
            return

        try:

            # add the other transactions to the set
            # remove used outputs
            if len(txs) == 1:
                UTXO.sets[block_id] = new_set
                return 

            for txid in txs[1:]:

                tx = ObjectHandler.get_object(txid)
                for input in tx[inputs_key]:
                    # get the outpoint
                    outpoint = input[outpoint_key]
                    txid = outpoint[txid_key]
                    out_index = outpoint[index_key]
                    # remove the output from the set
                    if txid in new_set.keys():
                        new_set[txid].remove(out_index)
                        if len(new_set[txid]) == 0:
                            new_set.pop(txid)
                        break

                num_outputs = len(tx[outputs_key])

                # add the new outputs to the set
                new_set[txid] = [i for i in range(num_outputs)]

            # save the set
            UTXO.sets[block_id] = new_set
        except Exception as e:
            LogPlus.error(f"| ERROR | UTXO | Last | Error calculating set for block {block}: {e}")
        

    """# removes an output from the set
    @staticmethod
    def remove_from_set(txid, index):
        try:
          UTXO.set[txid].remove(index)
        except:
          pass"""

    """# adds an output in the set
    @staticmethod
    def add_new_set(blockid, set):
        UTXO.sets[blockid] = set"""

    # get a set for a block
    @staticmethod
    def get_set(blockid):
        return UTXO.sets[blockid]

    """
    # checks if a given transaction is valid in the context of the UTXO set
    @staticmethod       
    def is_available(inputs):
        valid_tx = True

        # we first store the input outpoints of the given transaction
        outpoints = [] # stores a list of tuples (txid, index)
        for input in inputs:
            outpoints.append((input[outpoint_key][txid_key], input[outpoint_key][index_key]))
        for tx_txid, tx_index in outpoints:
            if tx_txid not in UTXO.set:
                valid_tx = False
            else:
                if tx_index not in UTXO.set[tx_txid]:
                    valid_tx = False

        return valid_tx"""
