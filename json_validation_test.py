import jsonschema

from utility.json_validation import hello_message_schema, regular_transaction_schema

transaction_json = {
    "type": "transaction",
    "inputs": [
        {
            "outpoint": {
                "txid": "a" * 64,
                "index": 0,
            },
            "sig": "abc",
        }
    ],
    "outputs": [
        {
            "pubkey": "a" * 64,
            "value": 0,
        }
    ],
}

jsonschema.validate(instance=transaction_json, schema=regular_transaction_schema)