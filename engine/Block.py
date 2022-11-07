import json
import hashlib
from json_canonical import canonicalize


class Block:

    def __init__(self, txids, nonce, miner, note, previd, created, t):
        self.txids = txids
        self.nonce = nonce
        self.miner = miner
        self.note = note
        self.previd = previd
        self.created = created
        self.t = t

    def __init__(self, block_json):
        self.txids = block_json["txids"]
        self.nonce = block_json["nonce"]
        self.miner = block_json["miner"]
        self.note = block_json["note"]
        self.previd = block_json["previd"]
        self.created = block_json["created"]
        self.t = block_json["T"]

    def get_json(self):
        block_json = {
            "type": "block",
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




