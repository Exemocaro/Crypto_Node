from nacl.signing import *
import json
from engine.Transaction import *

# Generate a new random signing key
signing_key = SigningKey.generate()
print("Signing key: ", signing_key)

# Sign a message with the signing key
signed = signing_key.sign(b"Message")
print("Signed message: ", signed)

# Verify the signature with the verify key
verify_key = signing_key.verify_key
print("Verify key: ", verify_key)

try:
    verify_key.verify(signed)
    print("The signature is valid!")
except Exception as e:
    print("The signature is invalid!")

# Let's use ed25519 to sign a transaction
# First, we need to generate a new random signing key
signing_key = SigningKey.generate()
print("Signing key: ", signing_key)

# Then, we need to generate a new random verify key
verify_key = signing_key.verify_key
print("Verify key: ", verify_key)

# Now, we can sign a transaction
tx = {
    "type": "transaction",
    "inputs": [
        {
            "outpoint": {
                "txid": "a" * 64,
                "index": 0
            },
            "sig": None
        }
    ],
    "outputs": [
        {
            "pubkey": "abc",
            "value": 100
        }
    ]
}

# Use ed25519 now
signed = signing_key.sign(str(json.dumps(tx)).encode("utf-8"))
#print("Signed transaction: ", signed)

# get the signature
sig = signed.signature
#print("Signature: ", sig)

# Verify the signature, only on the signature, not the whole transaction
combined = sig + str(json.dumps(tx)).encode("utf-8")
print("Combined: ", combined)
print("Signed transaction: ", signed)
try:
    verify_key.verify(combined)
    print("The signature is valid!")
except Exception as e:
    print("The signature is invalid!")

# Create some transaction and get the signature
inputs = [
    {
        "outpoint": {
            "txid": "a" * 64,
            "index": 0
        },
        "sig": None
    }
]
outputs = [
    {
        "pubkey": "abc",
        "value": 100
    }
]
tx = Transaction(inputs=inputs, outputs=outputs)
tx_json = tx.get_json()
print("Transaction: ", tx_json)

tx_id = tx.get_txid()
print("Transaction ID: ", tx_id)


# Test the verifaction process
tx_json = {
    "inputs": [
        {
            "outpoint": {
                "index": 0,
                "txid": "1bb37b637d07100cd26fc063dfd4c39a7931cc88dae3417871219715a5e374af"
            },
            "sig": "1d0d7d774042607c69a87ac5f1cdf92bf474c25fafcc089fe667602bfefb0494726c519e92266957429ced875256e6915eb8cea2ea66366e739415efc47a6805"
        }
    ],
    "outputs": [
        {
            "pubkey": "8dbcd2401c89c04d6e53c81c90aa0b551cc8fc47c0469217c8f5cfbae1e911f9",
            "value": 10
        }
    ],
    "type": "transaction"
}

tx = Transaction.from_json(tx_json)
if tx.verify_signature("8dbcd2401c89c04d6e53c81c90aa0b551cc8fc47c0469217c8f5cfbae1e911f9", "1d0d7d774042607c69a87ac5f1cdf92bf474c25fafcc089fe667602bfefb0494726c519e92266957429ced875256e6915eb8cea2ea66366e739415efc47a6805"):
    print("The signature is valid!")
else:
    print("The signature is invalid!")


