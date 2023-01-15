import json
import copy

from config import *

from utility.logplus import LogPlus


class Mempool:

    mempool = []

    @staticmethod
    def clear():
        """ Clears the mempool """
        Mempool.mempool = []

    @staticmethod
    def load_from_file():
        """ Loads the mempool from a file """
        try:
            with open(MEMPOOL_FILE, "r") as f:
                Mempool.mempool = json.load(f)
        except Exception as e:
            LogPlus.error(f"| ERROR | Couldn't load mempool | {e} ")

    @staticmethod
    def get_mempool():
        """ Returns a copy of the current mempool """
        return copy.deepcopy(Mempool.mempool)

    @staticmethod
    def add_transaction(transaction):
        """ Adds a new transaction to the mempool """
        Mempool.mempool.append(transaction)

    @staticmethod
    def remove_transactions(block):
        """ Removes transactions that have been included in a mined block """
        for tx in block.transactions:
            if tx in Mempool.mempool:
                Mempool.mempool.remove(tx)

    @staticmethod
    def auto_save():
        """ Saves the mempool to a file """
        with open(MEMPOOL_FILE, "w") as f:
            json.dump(Mempool.mempool, f)

