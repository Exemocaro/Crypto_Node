import jsonschema

from json_keys import *

# In this file, we will define the schema for all the messages and objects that we will use in the network
# We will use the jsonschema library to validate the messages and objects
# The format and the types will be tested, so all work afterwards can rely on valid data
# (no need to check if a key exists anymore)

# MESSAGE SCHEMAS

message_schema = {
    "$schema": "https://json-schema.org/draft/2020-12/schema",
    "$id": "message",
    "title": "Message",
    "description": "The schema for all messages",
    type_key: object_key,
    "properties": {
        type_key: {
            "description": "The type of the message",
            type_key: "string",
            "enum": message_keys
        },
    },
    "required": [type_key],
}

# The schema for the hello message
hello_message_schema = {
    "$schema": "https://json-schema.org/draft/2020-12/schema",
    "$id": "hello message",
    "title": "Hello message",
    "description": "The schema for the hello message",
    type_key: object_key,
    "properties": {
        type_key: {
            "description": "The type of the message",
            type_key: "string",
        },
        version_key: {
            "description": "The version that the node is using",
            type_key: "string",
            "pattern": "^0\\.8\\.\\d+$"
        },
        agent_key: {
            "description": "The name of the node",
            type_key: "string",
        },
    },
    "required": [type_key, version_key, agent_key],
}

# the schema for the peers message
peers_message_schema = {
    "$schema": "https://json-schema.org/draft/2020-12/schema",
    "$id": "peers message",
    "title": "Peers message",
    "description": "The schema for the peers message",
    type_key: object_key,
    "properties": {
        type_key: {
            "description": "The type of the message",
            type_key: "string",
        },
        peers_key: {
            "description": "The list of peers",
            type_key: "array",
            "items": {
                type_key: "string",
            },
        },
    },
    "required": [type_key, peers_key],
}

# the schema for the getpeers message
getpeers_message_schema = {
    "$schema": "https://json-schema.org/draft/2020-12/schema",
    "$id": "getpeers message",
    "title": "Getpeers message",
    "description": "The schema for the getpeers message",
    type_key: object_key,
    "properties": {
        type_key: {
            "description": "The type of the message",
            type_key: "string",
        },
    },
    "required": [type_key],
}

# error mesage schema

error_message_schema = {
    "$schema": "https://json-schema.org/draft/2020-12/schema",
    "$id": "error message",
    "title": "Error message",
    "description": "The schema for the error message",
    type_key: object_key,
    "properties": {
        type_key: {
            "description": "The type of the message",
            type_key: "string",
            "enum": ["error"]
        },
        error_key: {
            "description": "The error message",
            type_key: "string",
        },
    },
    "required": [type_key, error_key],
}

# ihavebject message schema

ihaveobject_message_schema = {
    "$schema": "https://json-schema.org/draft/2020-12/schema",
    "$id": "ihaveobject message",
    "title": "Ihaveobject message",
    "description": "The schema for the ihaveobject message",
    type_key: object_key,
    "properties": {
        type_key: {
            "description": "The type of the message",
            type_key: "string",
            "enum": ["ihaveobject"]
        },
        objectid_key: {
            "description": "The object that the node has",
            type_key: "string",
        },
    },
    "required": [type_key, objectid_key],
}

# getobject message schema
getobject_message_schema = {
    "$schema": "https://json-schema.org/draft/2020-12/schema",
    "$id": "getobject message",
    "title": "Getobject message",
    "description": "The schema for the getobject message",
    type_key: object_key,
    "properties": {
        type_key: {
            "description": "The type of the message",
            type_key: "string",
            "enum": ["getobject"]
        },
        objectid_key: {
            "description": "The object that the node wants",
            type_key: "string",
        },
    },
    "required": [type_key, objectid_key],
}

# object message schema

object_message_schema = {
    "$schema": "https://json-schema.org/draft/2020-12/schema",
    "$id": "object message",
    "title": "Object message",
    "description": "The schema for the object message",
    type_key: object_key,
    "properties": {
        type_key: {
            "description": "The type of the message",
            type_key: "string",
            "enum": ["object"]
        },
        object_key: {
            "description": "The object",
            type_key: object_key,
            "properties": {
                type_key: {
                    "description": "The type of the object",
                    type_key: "string",
                    "enum": ["block", "transaction"]
                }
            },
            "required": [type_key],
        },
    },
    "required": [type_key, object_key],
}


chaintip_message_schema = {
    "$schema": "https://json-schema.org/draft/2020-12/schema",
    "$id": "chaintip message",
    "title": "Chaintip message",
    "description": "The schema for a chaintip message",
    type_key: object_key,
    "properties": {
        type_key: {
            "description": "The type of the chaintip",
            type_key: "string",
            "enum": ["chaintip"]
        },
        blockid_key: {
            "description": "The chaintip",
            type_key: "string",
        },
    },
    "required": [type_key, blockid_key],
}

getchaintip_message_schema = {
    "$schema": "https://json-schema.org/draft/2020-12/schema",
    "$id": "getchaintip message",
    "title": "Getchaintip message",
    "description": "The schema for the getchaintip message",
    type_key: object_key,
    "properties": {
        type_key: {
            "description": "The type of the getchaintip",
            type_key: "string",
            "enum": ["getchaintip"]
        },
    },
    "required": [type_key],
}

mempool_message_schema = {
    "$schema": "https://json-schema.org/draft/2020-12/schema",
    "$id": "mempool message",
    "title": "Mempool message",
    "description": "The schema for the mempool message",
    type_key: object_key,
    "properties": {
        type_key: { 
            "description": "The type of the mempool",
            type_key: "string",
            "enum": ["mempool"]
        },
        txids_key: {
            "description": "The mempool",
            type_key: "array",
            "items": {
                type_key: "string",
            },
        },
    },
    "required": [type_key, txids_key],
}

getmempool_message_schema = {
    "$schema": "https://json-schema.org/draft/2020-12/schema",
    "$id": "getmempool message",
    "title": "Getmempool message",
    "description": "The schema for the getmempool message",
    type_key: object_key,
    "properties": {
        type_key: {
            "description": "The type of the getmempool",
            type_key: "string",
            "enum": ["getmempool"]
        },
    },
    "required": [type_key],
}


# OBJECT SCHEMAS


# The schema for a list of outputs (used in the transaction message)
outputs_schema = {
    "description": "The outputs of a transaction",
    type_key: "array",
    "items": {
        type_key: object_key,
        "properties": {
            "pubkey": {
                "description": "The public key of the recipient",
                type_key: "string",
            },
            "value": {
                "description": "The amount of coins in picaker",
                type_key: "integer",
                "minimum": 0,
            }
        },
        "required": ["pubkey", "value"],
    },
    "uniqueItems": True,
}

regular_transaction_schema = {
    "$schema": "https://json-schema.org/draft/2020-12/schema",
    "$id": "regular transaction",
    "title": "Regular transaction",
    "description": "A regular transaction",
    type_key: object_key,
    "properties": {
        type_key: {
            "description": "The type of the transaction",
            type_key: "string",
            "enum": ["transaction"]
        },
        "inputs": {
            "description": "The inputs of the transaction",
            type_key: "array",
            "items": {
                type_key: object_key,
                "properties": {
                    "outpoint": {
                        "description": "The outpoint of the input",
                        type_key: object_key,
                        "properties": {
                            "txid": {
                                "description": "The transaction id of the previous transaction",
                                type_key: "string",
                            },
                            "index": {
                                "description": "The index of the output in the previous transaction",
                                type_key: "integer",
                                "minimum": 0,
                            }
                        },
                        "required": ["txid", "index"],
                    },
                    "sig": {
                        "description": "The signature of the input",
                        type_key: "string",
                    }
                },
                "required": ["outpoint", "sig"],
            },
            "minItems": 1,
            "uniqueItems": True,
        },
        "outputs": outputs_schema,
    },
    "required": [type_key, "inputs", "outputs"],
}


# The schema for a coinbase transaction
coinbase_transaction_schema = {
    "$schema": "https://json-schema.org/draft/2020-12/schema",
    "$id": "coinbase transaction",
    "title": "Coinbase transaction",
    "description": "A coinbase transaction",
    type_key: object_key,
    "properties": {
        type_key: {
            "description": "The type of the transaction",
            type_key: "string",
            "enum": ["transaction"]
        },
        "outputs": outputs_schema
    },
    "required": [type_key, "outputs"],
}

block_schema = {
    "$schema": "https://json-schema.org/draft/2020-12/schema",
    "$id": "block",
    "title": "Block",
    "description": "The schema for a block",
    type_key: object_key,
    "properties": {
        type_key: {
            "description": "The type of the block",
            type_key: "string",
            "enum": ["block"]
        },
        "txids": {
            "description": "The transaction ids of the transactions in the block",
            type_key: "array",
            "items": {
                "description": "The transaction id",
                type_key: "string",
            },
            "minItems": 1,
            "uniqueItems": True,
        },
        "previd": {
            "description": "The hash of the previous block",
            type_key: "string",
        },
        "nonce": {
            "description": "The nonce of the block",
            type_key: "string",
        },
        "created": {
            "description": "The timestamp of the block",
            type_key: "integer",
            "minimum": 0,
        },
        "miner": {
            "description": "The name of the miner (not technically needed)",
            type_key: "string",
        },
        "note": {
            "description": "The note of the block (not technically needed)",
            type_key: "string",
        },
        "T": {
            "description": "The target of the block",
            type_key: "string",
        },
    },
    "required": [type_key, "txids", "previd", "nonce", "created", "T"],
}









