import json
import json_canonical
import hashlib
import copy
import time

from queue import Queue
from threading import Thread, Timer
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
        Object.get_id_from_json(GENESIS_BLOCK): {} # genesis block
    }

    auto_save_queue = Queue()

    @staticmethod
    def clear():
        """ Clears the UTXO set, only the genesis block is left"""
        UTXO.sets = {
            Object.get_id_from_json(GENESIS_BLOCK): {} # genesis block
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
    def get_utxo(blockid):
        """ Returns the UTXO set for the given block id, calculates it if it doesn't exist yet
        Returns None if the block doesn't exist or the set couldn't be calculated """
        try:
            # Try calculating the set if it doesn't exist yet
            if blockid in UTXO.sets:
                return copy.deepcopy(UTXO.sets[blockid])
            # Try calculating the set
            # Check if previous block utxo set exists
            # Otherwise use fake recursive call to calculate the set
            prev_id = ObjectHandler.get_object(blockid)[previd_key]
            todo = [blockid]
            while prev_id is not None and prev_id not in copy.deepcopy(UTXO.sets):
                todo.append(prev_id)
                prev_id = (ObjectHandler.get_object(prev_id))[previd_key]
            if prev_id is None:
                # check if it's the genesis block
                if blockid == Object.get_id_from_json(GENESIS_BLOCK):
                    UTXO.sets[blockid] = {}
                    return {}
                else:
                    LogPlus.error(f"| ERROR | UTXO | Couldn't find previous block for {blockid}")
                    return None

            # calculate the todo from end to start
            for blockid in reversed(todo):
                block = ObjectHandler.get_object(blockid)
                UTXO.calculate_set(block)
            return copy.deepcopy(UTXO.sets[blockid])
        except Exception as e:
            LogPlus.error(f"| ERROR | UTXO | Couldn't get UTXO set for {blockid} | {e}")
            return None
    
    @staticmethod
    def calculate_set(block):
        """ Calculates the UTXO set for the given block and adds it to the UTXO.sets dictionary
        Block has to be a dictionary"""
        try:
            # get the previous block
            prev_id = block[previd_key]
            if prev_id not in UTXO.sets:
                return 
            prev_set = copy.deepcopy(UTXO.sets[prev_id])

            # get the id of the coinbase transaction
            txs = block[txids_key]
            coinbase_txid = txs[0]

            # add the coinbase transaction to the set
            new_set = prev_set
            new_set[coinbase_txid] = [0]

            # add the other transactions to the set
            # remove used outputs
            for new_txid in txs[1:]:

                tx = ObjectHandler.get_object(new_txid)
                for input in tx[inputs_key]:
                    # get the outpoint
                    outpoint = input[outpoint_key]
                    txid_to_check = outpoint[txid_key]
                    out_index = outpoint[index_key]
                    # raise error if invalid outpoint
                    if txid_to_check not in new_set or out_index not in new_set[txid_to_check]:
                        raise TransactionsInvalidException(f"Invalid outpoint from {new_txid} to {txid_to_check}")
                    # remove the output from the set
                    new_set[txid_to_check] = new_set[txid_to_check]
                    new_set[txid_to_check].remove(out_index)
                    if len(new_set[txid_to_check]) == 0:
                        new_set.pop(txid_to_check)
                    break

                num_outputs = len(tx[outputs_key])

                # add the new outputs to the set
                out_indexes = [i for i in range(num_outputs)]
                new_set[new_txid] = out_indexes

            # save the set
            block_id = Object.get_id_from_json(block)
            UTXO.sets[block_id] = new_set
            UTXO.save()
        except TransactionsInvalidException as e:
            # pass the exception up
            raise e
        except Exception as e:
            LogPlus.error(f"| ERROR | UTXO | Last | Error calculating set for block {block}: {e}")

    # Multithreaded auto save

    @staticmethod
    def save():
        """ Saves the UTXO by adding it to the auto save queue"""
        UTXO.auto_save_queue.put(copy.deepcopy(UTXO.sets))

    @staticmethod
    def start_auto_save():
        """ Starts the auto save thread"""
        save_thread = Thread(target=UTXO.auto_save)
        save_thread.start()

    @staticmethod
    def auto_save():
        """Save function made for multithreading"""
        while True:
            if not UTXO.auto_save_queue.empty():
                # get last item from queue
                while not UTXO.auto_save_queue.empty():
                    item = UTXO.auto_save_queue.get()
                # save to file
                UTXO.save_to_file(copy.deepcopy(item))
            # wait for 5 seconds
            time.sleep(AUTO_SAVE_INTERVAL)

    @staticmethod
    def save_to_file(sets):
        """ Saves the given UTXO set to the UTXO file"""
        try:
            with open(UTXO_FILE, "w") as f:
                json.dump(sets, f, indent=4)
        except Exception as e:
            LogPlus.error(f"| ERROR | Couldn't save UTXO set | {e} ")

class TransactionsInvalidException(Exception):
    pass