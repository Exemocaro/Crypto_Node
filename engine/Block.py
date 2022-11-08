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

    def from_json(block_json):
        block = Block(
            block_json["txids"],
            block_json["nonce"],
            block_json["miner"],
            block_json["note"],
            block_json["previd"],
            block_json["created"],
            block_json["T"]
        )
        return block
