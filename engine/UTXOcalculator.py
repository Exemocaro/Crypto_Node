
from object.Block import Block

from database.UTXO import UTXO
from database.ObjectHandler import ObjectHandler

def calculate_set(block):
    # create empty set for the genesis block
    sets = {"00000000a420b7cefa2b7730243316921ed59ffe836e111ca3801f82a4f5360e": []}
    # make an array of all blocks that are not the genesis block
    blocks = ObjectHandler.get_blocks()[1:]

    """
    # As an orientation, this is how we do it on the go:

    # Load UTXO of previous block
        prev_utxo = UTXO.get_utxo(self.previd)
        if prev_utxo is None:
            LogPlus.error("| ERROR | Block.verify | Previous UTXO is not found")
            return {"result": "False"}

        new_utxo = prev_utxo # we'll update this as we go along
        # it's a list of dicts
        # each dict has a key "txid" and an array of indexes "indexes" that are still unspent

        # Loop through all transactions in the block
        # First loop to add all new outputs to the UTXO
        # Second loop to remove all inputs from the UTXO
        for txid in self.txids:
            tx_json = ObjectHandler.get_object(txid)
            # get an array containing the indexes (0, 1, 2, ...) of the outputs that are still unspent
            indexes = [i for i in range(len(tx_json["outputs"]))]
            new_utxo.append({txid: indexes})

        for txid in self.txids:
            tx_json = ObjectHandler.get_object(txid)
            for input in tx_json["inputs"]:
                # remove the input from the UTXO
                for outputs in new_utxo:
                    if input["txid"] in outputs:
                        outputs[input["txid"]].remove(input["index"])
                        # remove the dict if there are no more unspent outputs
                        if len(outputs[input["txid"]]) == 0:
                            new_utxo.remove(outputs)
                        break

    """
    
    # repeat until all blocks are processed
    while len(blocks) > 0:
        for block_json in blocks:
            block = Block.from_json(block_json)
            blockid = block.get_id()
            previd = block.previd
            # if the previous block is in the set, we can calculate the set for this block
            if previd in sets:
                set = sets[previd]
                txs = block.txids

                # add all new outputs to the set
                for txid in txs:
                    tx_json = ObjectHandler.get_object(txid)
                    # get an array containing the indexes (0, 1, 2, ...) of the outputs that are still unspent
                    indexes = [i for i in range(len(tx_json["outputs"]))]
                    set.append({txid: indexes})

                # remove all inputs from the set
                for txid in txs:
                    tx_json = ObjectHandler.get_object(txid)
                    for input in tx_json["inputs"]:
                        # remove the input from the set
                        for outputs in set:
                            if input["txid"] in outputs:
                                outputs[input["txid"]].remove(input["index"])
                                # remove the dict if there are no more unspent outputs
                                if len(outputs[input["txid"]]) == 0:
                                    set.remove(outputs)
                                break

                # add the set to the sets dict
                sets[blockid] = set
                # remove the block from the blocks array
                blocks.remove(block_json)

    return sets
    


              
