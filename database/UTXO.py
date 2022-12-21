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
#   blockid: { 
#       txid: [indexes],
#       txid: [indexes],
#       ...
#   }
#
# }

class UTXO:

    sets = {
        "00000000a420b7cefa2b7730243316921ed59ffe836e111ca3801f82a4f5360e": {} # genesis block
    }

    @staticmethod
    def clear():
        """ Clears the UTXO set, only the genesis block is left"""
        UTXO.sets = {
            "00000000a420b7cefa2b7730243316921ed59ffe836e111ca3801f82a4f5360e": {} # genesis block
        }

    @staticmethod
    def load_from_file():
        """ Loads the UTXO set from the UTXO file"""
        try:
            with open(UTXO_FILE, "r") as f:
                UTXO.sets = json.load(f)
        except Exception as e:
            LogPlus.error(f"| ERROR | Couldn't load UTXO set | {e} ")
    
    @staticmethod
    def save_to_file():
        """ Saves the UTXO set to the UTXO file"""
        try:
            with open(UTXO_FILE, "w") as f:
                json.dump(UTXO.sets, f, indent=4)
        except Exception as e:
            LogPlus.error(f"| ERROR | Couldn't save UTXO set | {e} ")


    @staticmethod
    def get_utxo(blockid, calulate_if_not_exist=True):
        """ Returns the UTXO set for the given block id, calculates it if it doesn't exist yet
        Returns None if the block doesn't exist or the set couldn't be calculated """
        # Try calculating the set if it doesn't exist yet
        if blockid not in UTXO.sets.keys() and calulate_if_not_exist:
            UTXO.calculate_set(ObjectHandler.get_object(blockid))
        # If it still doesn't exist, return None
        if blockid in UTXO.sets.keys():
            return UTXO.sets[blockid]
        else:
            return None
    
    @staticmethod
    def calculate_set(block):
        """ Calculates the UTXO set for the given block and adds it to the UTXO.sets dictionary
        Block has to be a dictionary"""
        try:
            # get the previous block
            prev_id = block[previd_key]
            if prev_id not in UTXO.sets.keys():
                return 
            prev_set = UTXO.sets[prev_id]
            LogPlus.debug(f"| DEBUG | UTXO | Prev id | {prev_id}")

            # get the id of the coinbase transaction
            txs = block[txids_key]
            coinbase_txid = txs[0]
            LogPlus.debug(f"| DEBUG | UTXO | Coinbase | {coinbase_txid}")

            # add the coinbase transaction to the set
            new_set = prev_set.copy()
            new_set[coinbase_txid] = [0]
            LogPlus.debug(f"| DEBUG | UTXO | New set | {new_set}")

            # add the other transactions to the set
            # remove used outputs
            for new_txid in txs[1:]:

                tx = ObjectHandler.get_object(new_txid)
                for input in tx[inputs_key]:
                    # get the outpoint
                    outpoint = input[outpoint_key]
                    txid_to_check = outpoint[txid_key]
                    out_index = outpoint[index_key]
                    # remove the output from the set
                    if txid_to_check in new_set.keys():
                        LogPlus.debug(f"| DEBUG | UTXO | Last | Checking {txid_to_check} in set")
                        new_set[txid_to_check].remove(out_index)
                        LogPlus.debug(f"| DEBUG | UTXO | Last | Removed {out_index} from {txid_to_check}")
                        if len(new_set[txid_to_check]) == 0:
                            new_set.pop(txid_to_check)
                            LogPlus.debug(f"| DEBUG | UTXO | Last | Removed {txid_to_check} from set")
                        break
                    else :
                        LogPlus.error(f"| ERROR | UTXO | Last | Couldn't find txid {txid_to_check} in utxo set")
                        LogPlus.debug(f"| DEBUG | UTXO | Last | Block: {Object.get_id_from_json(block)}")
                        return

                num_outputs = len(tx[outputs_key])

                # add the new outputs to the set
                new_set[new_txid] = [i for i in range(num_outputs)]

            # save the set
            block_id = Object.get_id_from_json(block)
            UTXO.sets[block_id] = new_set
            UTXO.save_to_file()
        except Exception as e:
            LogPlus.error(f"| ERROR | UTXO | Last | Error calculating set for block {block}: {e}")
