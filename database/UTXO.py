import json
import json_canonical
import hashlib
from colorama import Fore, Style

from utility.logplus import LogPlus

from object.Object import Object

from database.ObjectHandler import ObjectHandler

from config import *

class UTXO:

    sets = {
        "00000000a420b7cefa2b7730243316921ed59ffe836e111ca3801f82a4f5360e": [] # genesis block
    }
    
    # dict that stores every valid output of valid stored tansactions in json format
    # {block: [(txid, [indexes])]}

    # loads the set from the database files
    @staticmethod
    def load_set():
        # recalculate the set from the database for each block
        for block in ObjectHandler.get_blocks():
            UTXO.sets[block.get_id()] = UTXO.calculate_set(block)


    @staticmethod
    def clear():
        UTXO.sets = {}

    @staticmethod
    def get_utxo(blockid):
        if blockid in UTXO.sets:
            return UTXO.sets[blockid]
        else:
            return None



    """# removes an output from the set
    @staticmethod
    def remove_from_set(txid, index):
        try:
          UTXO.set[txid].remove(index)
        except:
          pass"""

    # adds an output in the set
    @staticmethod
    def add_new_set(blockid, set):
        UTXO.set[blockid] = set

    # get a set for a block
    @staticmethod
    def get_set(blockid):
        return UTXO.set[blockid]

    """
    # checks if a given transaction is valid in the context of the UTXO set
    @staticmethod       
    def is_available(inputs):
        valid_tx = True

        # we first store the input outpoints of the given transaction
        outpoints = [] # stores a list of tuples (txid, index)
        for input in inputs:
            outpoints.append((input["outpoint"]["txid"], input["outpoint"]["index"]))
        for tx_txid, tx_index in outpoints:
            if tx_txid not in UTXO.set:
                valid_tx = False
            else:
                if tx_index not in UTXO.set[tx_txid]:
                    valid_tx = False

        return valid_tx"""
