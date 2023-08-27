from nacl.signing import VerifyKey, SigningKey
from nacl.encoding import HexEncoder

import json
import json_canonical

transact_tx = {
    "inputs": [
        {
            "outpoint": {
                "index": 0,
                "txid": "48c2ae2fbb4dead4bcc5801f6eaa9a350123a43750d22d05c53802b69c7cd9fb",
            },
            "sig": None,
        }
    ],
    "outputs": [
        {
            "pubkey": "228ee807767047682e9a556ad1ed78dff8d7edf4bc2a5f4fa02e4634cfcad7e0",
            "value": 49000000000000,
        }
    ],
    type_key: "transaction",
}
public_key = "62b7c521cd9211579cf70fd4099315643767b96711febaa5c76dc3daf27c281c"
signature = "d51e82d5c121c5db21c83404aaa3f591f2099bccf731208c4b0b676308be1f994882f9d991c0ebfd8fdecc90a4aec6165fc3440ade9c83b043cba95b2bba1d0a"

transact_tx_bytes = json_canonical.canonicalize(transact_tx)

print("Transaction: ", transact_tx_bytes)

# Verify the signature, only on the signature, not the whole transaction
combined = bytes.fromhex(signature) + transact_tx_bytes

print("Combined: ", combined)

new_verify_key = VerifyKey("a" * 64, encoder=HexEncoder)
print("Verify key: ", new_verify_key)

public_key_bytes = bytes.fromhex(public_key)

print("Public key: ", public_key_bytes)

verify_key = VerifyKey(public_key_bytes)
print("Verify key: ", verify_key)
verify_key.verify(combined)
