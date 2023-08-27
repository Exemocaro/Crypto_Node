import json
import json_canonical
import hashlib
import copy
import time
import typing

from queue import Queue
from threading import Thread, Timer
from colorama import Fore, Style

from utility.logplus import LogPlus
from utility.TimeTracker import TimeTracker

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
    GENESIS_BLOCK_UTXO = {}
    longest_chain_stored_id = None
    longest_chain_utxo = None

    @staticmethod
    def get_utxo(blockid):
        """Returns the UTXO set for the given block id by calculating it
        Returns None if the block doesn't exist or the set couldn't be calculated"""

        if blockid == GENESIS_BLOCK_ID:
            return UTXO.GENESIS_BLOCK_UTXO

        try:
            # Calculating the set
            # Check if previous block utxo set exists
            # Otherwise use fake recursive call to calculate the set

            prev_id = ObjectHandler.get_object(blockid)[previd_key]
            todo = [blockid]
            while prev_id != GENESIS_BLOCK_ID and prev_id is not None:
                todo.append(prev_id)
                try:
                    block = ObjectHandler.get_object(prev_id)
                    prev_id = block[previd_key]
                except Exception as e:
                    # TODO: Maybe we should request the block from the network
                    LogPlus.error(
                        f"| ERROR | UTXO | Couldn't find previous block for {blockid} | {e}"
                    )
                    return None

            if prev_id is None:
                # We would have caught the genesis block id in the while loop
                LogPlus.error(
                    f"| ERROR | UTXO | Couldn't find previous block for {blockid}"
                )
                return None

            current_utxo = copy.deepcopy(UTXO.GENESIS_BLOCK_UTXO)

            # calculate the todo from end to start
            for blockid in reversed(todo):
                block = ObjectHandler.get_object(blockid)
                txids = block[txids_key]
                transactions = [ObjectHandler.get_object(txid) for txid in txids]
                current_utxo = UTXO.apply_multiple_transactions_to_UTXO(
                    current_utxo, transactions
                )

            if blockid == ObjectHandler.get_chaintip():
                UTXO.longest_chain_stored_id = blockid
                UTXO.longest_chain_utxo = current_utxo

            return current_utxo

        except Exception as e:
            LogPlus.error(
                f"| WARNING | UTXO | Couldn't get UTXO set for {blockid} | {e}"
            )
            LogPlus.error(f"Previous utxo set: {current_utxo}")
            return None

    @staticmethod
    def apply_transaction_to_UTXO(
        utxo: typing.Dict, transaction: typing.Dict
    ) -> typing.Dict:
        """Applies the given transaction to the given UTXO set
        Returns the modified UTXO set"""
        try:
            utxo = copy.deepcopy(utxo)
            # remove used outputs
            if inputs_key in transaction:  # if it's not a coinbase transaction
                for input in transaction[inputs_key]:
                    # get the outpoint
                    outpoint = input[outpoint_key]
                    txid_to_check = outpoint[txid_key]
                    out_index = outpoint[index_key]
                    # raise error if invalid outpoint
                    if (
                        txid_to_check not in utxo
                        or out_index not in utxo[txid_to_check]
                    ):
                        raise TransactionsInvalidException(
                            f"Invalid outpoint {txid_to_check}:{out_index}"
                        )

                    # remove the outpoint
                    utxo[txid_to_check].remove(out_index)
                    # remove the txid if it doesn't have any outputs left
                    if len(utxo[txid_to_check]) == 0:
                        del utxo[txid_to_check]
            # get the id of the transaction
            txid = Object.get_id_from_json(transaction)
            # create a list of indexes for the outputs
            indexes = [i for i in range(len(transaction[outputs_key]))]
            utxo[txid] = indexes
            return utxo
        except TransactionsInvalidException as e:
            LogPlus.warning(f"| WARNING | UTXO | Invalid transaction | {e}")
            raise e
        except Exception as e:
            LogPlus.error(f"| ERROR | UTXO | Couldn't apply transaction to UTXO | {e}")
            return {}

    @staticmethod
    def apply_multiple_transactions_to_UTXO(
        utxo: typing.Dict, transactions: typing.List
    ) -> typing.Dict:
        """Applies the given transactions to the given UTXO set
        Returns the modified UTXO set"""
        for transaction in transactions:
            utxo = UTXO.apply_transaction_to_UTXO(utxo, transaction)
        return utxo

    @staticmethod
    def check_validity(utxo: typing.Dict, transaction: typing.Dict) -> bool:
        """Checks if the given transaction is valid for the given UTXO set
        Returns True if the transaction is valid, False otherwise"""
        # check if the transaction is valid
        try:
            LogPlus.debug(
                f"| DEBUG | UTXO |Verify transaction to UTXO | {type(transaction)}"
            )
            UTXO.apply_transaction_to_UTXO(utxo, transaction)
            return True
        except TransactionsInvalidException as e:
            return False

    @staticmethod
    def check_multiple_validities(utxo: typing.Dict, transactions: typing.List) -> bool:
        """Checks if the given transactions are valid for the given UTXO set
        Returns True if all transactions are valid, False otherwise"""
        try:
            UTXO.apply_multiple_transactions_to_UTXO(utxo, transactions)
            return True
        except TransactionsInvalidException as e:
            return False


class TransactionsInvalidException(Exception):
    pass
