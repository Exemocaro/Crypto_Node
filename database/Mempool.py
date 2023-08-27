import json
import copy
import typing

from config import *

from utility.logplus import LogPlus

from database.ObjectHandler import ObjectHandler
from database.UTXO import UTXO, TransactionsInvalidException

from object.Object import Object


class Mempool:
    mempool_txids = []
    mempool_utxo = {}

    @staticmethod
    def clear():
        """Clears the mempool"""
        Mempool.mempool_txids = []
        Mempool.mempool_utxo = {}

    @staticmethod
    def get_mempool():
        """Returns a copy of the current mempool"""
        return copy.deepcopy(Mempool.mempool_txids)

    @staticmethod
    def add_transaction(transaction: typing.Dict) -> bool:
        """Adds a new transaction to the mempool"""
        try:
            UTXO.apply_transaction_to_UTXO(Mempool.mempool_utxo, transaction)
            txid = Object.get_id_from_json(transaction)
            Mempool.mempool_txids.append(txid)
            return True
        except TransactionsInvalidException as e:
            LogPlus.warning(
                f"| WARNING | Mempool | Invalid transaction | {Object.get_id_from_json(transaction)[:10]}..."
            )
            return False
        except Exception as e:
            LogPlus.error(
                f"| ERROR | Mempool | Couldn't add transaction to mempool | {e} | {Object.get_id_from_json(transaction)[:10]}..."
            )
            return False

    @staticmethod
    def apply_block(block: typing.Dict):
        """Removes transactions that have been included in a mined block"""
        for tx_id in block["txids"]:
            if tx_id in Mempool.mempool_txids:
                Mempool.mempool_txids.remove(tx_id)

        # Create a new UTXO set for the mempool
        # Check for the remaining transactions in the mempool if they are valid regarding the new UTXO set
        block_id = Object.get_id_from_json(block)
        Mempool.mempool_utxo = UTXO.get_utxo(block_id)
        for tx_id in Mempool.mempool_txids:
            tx = ObjectHandler.get_object(tx_id)
            if not Mempool.is_transaction_valid_for_mempool(tx):
                Mempool.mempool_txids.remove(tx_id)
            else:
                Mempool.mempool_utxo = UTXO.apply_transaction_to_UTXO(
                    Mempool.mempool_utxo, tx
                )

    @staticmethod
    def is_transaction_valid_for_mempool(transaction: typing.Dict) -> bool:
        """Checks if a transaction is valid regaring the latest UTXO set"""
        return UTXO.check_validity(Mempool.mempool_utxo, transaction)
