import jsonschema

# In this file, we will define the schema for all the messages and objects that we will use in the network
# We will use the jsonschema library to validate the messages and objects
# The format and the types will be tested, so all work afterwards can rely on valid data
# (no need to check if a key exists anymore)

# MESSAGE SCHEMAS

# The schema for the hello message
hello_message_schema = {
    "$schema": "https://json-schema.org/draft/2020-12/schema",
    "$id": "hello message",
    "title": "Hello message",
    "description": "The schema for the hello message",
    "type": "object",
    "properties": {
        "type": {
            "description": "The type of the message",
            "type": "string",
        },
        "version": {
            "description": "The version that the node is using",
            "type": "string",
            "pattern": "^0\\.8\\.\\d+$"
        },
        "agent": {
            "description": "The name of the node",
            "type": "string",
        },
    },
    "required": ["type", "version", "agent"],
}

# the schema for the peers message
peers_message_schema = {
    "$schema": "https://json-schema.org/draft/2020-12/schema",
    "$id": "peers message",
    "title": "Peers message",
    "description": "The schema for the peers message",
    "type": "object",
    "properties": {
        "type": {
            "description": "The type of the message",
            "type": "string",
        },
        "peers": {
            "description": "The list of peers",
            "type": "array",
            "items": {
                "type": "string",
            },
        },
    },
    "required": ["type", "peers"],
}

# the schema for the getpeers message
getpeers_message_schema = {
    "$schema": "https://json-schema.org/draft/2020-12/schema",
    "$id": "getpeers message",
    "title": "Getpeers message",
    "description": "The schema for the getpeers message",
    "type": "object",
    "properties": {
        "type": {
            "description": "The type of the message",
            "type": "string",
        },
    },
    "required": ["type"],
}

# error mesage schema

# ihavebject message schema

ihaveobject_schema = {
    "$schema": "https://json-schema.org/draft/2020-12/schema",
    "$id": "ihaveobject message",
    "title": "Ihaveobject message",
    "description": "The schema for the ihaveobject message",
    "type": "object",
    "properties": {
        "type": {
            "description": "The type of the message",
            "type": "string",
        },
        "objectid": {
            "description": "The object that the node has",
            "type": "string",
        },
    },
    "required": ["type", "objectid"],
}

# getobject message schema
getobject_schema = {
    "$schema": "https://json-schema.org/draft/2020-12/schema",
    "$id": "getobject message",
    "title": "Getobject message",
    "description": "The schema for the getobject message",
    "type": "object",
    "properties": {
        "type": {
            "description": "The type of the message",
            "type": "string",
        },
        "objectid": {
            "description": "The object that the node wants",
            "type": "string",
        },
    },
    "required": ["type", "objectid"],
}

# object message schema

object_schema = {
    "$schema": "https://json-schema.org/draft/2020-12/schema",
    "$id": "object message",
    "title": "Object message",
    "description": "The schema for the object message",
    "type": "object",
    "properties": {
        "type": {
            "description": "The type of the message",
            "type": "string",
        },
        "object": {
            "description": "The object",
            "type": "object",
        },
    },
    "required": ["type", "object"],
}


# OBJECT SCHEMAS


# The schema for a list of outputs (used in the transaction message)
outputs_schema = {
    "description": "The outputs of a transaction",
    "type": "array",
    "items": {
        "type": "object",
        "properties": {
            "pubkey": {
                "description": "The public key of the recipient",
                "type": "string",
            },
            "value": {
                "description": "The amount of coins in picaker",
                "type": "integer",
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
    "type": "object",
    "properties": {
        "type": {
            "description": "The type of the transaction",
            "type": "string",
        },
        "inputs": {
            "description": "The inputs of the transaction",
            "type": "array",
            "items": {
                "type": "object",
                "properties": {
                    "outpoint": {
                        "description": "The outpoint of the input",
                        "type": "object",
                        "properties": {
                            "txid": {
                                "description": "The transaction id of the previous transaction",
                                "type": "string",
                            },
                            "index": {
                                "description": "The index of the output in the previous transaction",
                                "type": "integer",
                                "minimum": 0,
                            }
                        },
                        "required": ["txid", "index"],
                    },
                    "sig": {
                        "description": "The signature of the input",
                        "type": "string",
                    }
                },
                "required": ["outpoint", "sig"],
            },
            "minItems": 1,
            "uniqueItems": True,
        },
        "outputs": outputs_schema,
    },
    "required": ["type", "inputs", "outputs"],
}


# The schema for a coinbase transaction
coinbase_transaction_schema = {
    "$schema": "https://json-schema.org/draft/2020-12/schema",
    "$id": "coinbase transaction",
    "title": "Coinbase transaction",
    "description": "A coinbase transaction",
    "type": "object",
    "properties": {
        "type": {
            "description": "The type of the transaction",
            "type": "string",
        },
        "outputs": outputs_schema
    },
    "required": ["type", "outputs"],
}

block_schema = {
    "$schema": "https://json-schema.org/draft/2020-12/schema",
    "$id": "block",
    "title": "Block",
    "description": "The schema for a block",
    "type": "object",
    "properties": {
        "type": {
            "description": "The type of the block",
            "type": "string",
        },
        "txids": {
            "description": "The transaction ids of the transactions in the block",
            "type": "array",
            "items": {
                "description": "The transaction id",
                "type": "string",
            },
            "minItems": 0, # TODO : Can most likely be 1
            "uniqueItems": True,
        },
        "previd": {
            "description": "The hash of the previous block",
            "type": "string",
        },
        "nonce": {
            "description": "The nonce of the block",
            "type": "string",
        },
        "created": {
            "description": "The timestamp of the block",
            "type": "integer",
            "minimum": 0,
        },
        "miner": {
            "description": "The name of the miner (not technically needed)",
            "type": "string",
        },
        "note": {
            "description": "The note of the block (not technically needed)",
            "type": "string",
        },
        "T": {
            "description": "The target of the block",
            "type": "string",
        },
    },
    "required": ["type", "txids", "previd", "nonce", "created", "T"],
}











