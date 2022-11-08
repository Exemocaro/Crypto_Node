import nacl.encoding
from nacl.signing import *
import json
from engine.Transaction import *
from engine.CoinbaseTransaction import *
from engine.Object import *

# import base64encoder
import base64

from colorama import Fore, Back, Style


# Let's use ed25519 to sign a transaction
# First, we need to generate a new random signing key
signing_key = SigningKey.generate()
print("Signing key: ", signing_key.encode(encoder=nacl.encoding.HexEncoder).decode("utf-8"))
print()

# Then, we need to generate a new random verify key
verify_key = signing_key.verify_key
print("Verify key: ", verify_key.encode(encoder=nacl.encoding.HexEncoder).decode("utf-8"))
print()

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

message = json_canonical.canonicalize(tx)
print("Message: ", message)
print()

# Use ed25519 now
signed = signing_key.sign(message)
#print("Signed transaction: ", signed)

# get the signature
sig = signed.signature
print("Signature: ", sig.hex())
print()

# Verify the signature, only on the signature, not the whole transaction
combined = sig + str(json.dumps(tx)).encode("utf-8")
print("Combined: ", combined)
print()
print("Signed transaction: ", signed)
print()
try:
    verify_key.verify(combined)
    print("The signature is valid!")
except Exception as e:
    print("The signature is invalid!")

