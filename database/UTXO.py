import json
import json_canonical
import hashlib

from utility.logplus import LogPlus
from object.Object import Object
from database.ObjectHandler import *

from colorama import Fore, Style

from config import *

# we will work with tuples on the from (txid, outputs)
class UTXO:

    set = {} # dict that stores every valid output of valid stored tansactions in json format
    # {txid: [indexes]}

    # loads the set from the database files
    @staticmethod
    def load_set():
        # load all transactions from the database into the set
        for tx in ObjectHandler.getTransactions():
            UTXO.set[tx["txid"]] = [i for i in range(len(tx.outputs) - 1)]

        # remove the outputs that are spent
        for tx in ObjectHandler.getTransactions():
            for input in tx["inputs"]:
                # remove the index from the set
                UTXO.set[input["outpoint"]["txid"]].remove(input["outpoint"]["index"])

    # removes an output from the set
    @staticmethod
    def remove_from_set(txid, index):
        try:
          UTXO.set[txid].remove(index)
        except:
          pass

    # adds an output in the set
    @staticmethod
    def add_to_set(txid, num_outputs):
        UTXO.set[txid] = [i for i in range(num_outputs)]

    # checks if a given transaction is valid in the context of the UTXO set
    @staticmethod       
    def is_available(inputs):
        valid_tx = True

        # we first store the input outpoints of the given transaction
        outpoints = [] # stores a list of tuples (txid, index)
        for input in inputs:
            outpoints.append((input["outpoint"]["txid"], input["outpoint"]["index"]))
        for tx_txid, tx_index in outpoints:
            pass
        """ if set_txid != tx_txid: # there's no txid in the set to confirm the transaction
            valid_tx = False """
            #if UTXO.set[]
        
        """ for set_txid, set_outputs in UTXO.set:
            # check if the tx inputs match the ones stored in our set
            for tx_txid, tx_index in outpoints:
                if set_txid != tx_txid: # there's no txid in the set to confirm the transaction
                    valid_tx = False """

        return valid_tx
        
        
