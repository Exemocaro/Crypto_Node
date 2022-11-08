from nacl.signing import *
import json
from engine.Transaction import *
from engine.CoinbaseTransaction import *
from engine.Object import *

from colorama import Fore, Back, Style

pubkey = "8dbcd2401c89c04d6e53c81c90aa0b551cc8fc47c0469217c8f5cfbae1e911f9"

tx = CoinbaseTransaction(height=0, outputs=[{"pubkey": pubkey, "value": 50000000000}])
tx_json = tx.get_json()
print("Transaction: ", tx_json)

tx_id = tx.get_id()
print("Transaction ID: ", tx_id)

signature = "1d0d7d774042607c69a87ac5f1cdf92bf474c25fafcc089fe667602bfefb0494726c519e92266957429ced875256e6915eb8cea2ea66366e739415efc47a6805"

# Test the verifaction process
tx_json = {
    "inputs": [
        {
            "outpoint": {
                "index": 0,
                "txid": tx_id
            },
            "sig": signature
        }
    ],
    "outputs": [
        {
            "pubkey": tx.outputs[0]["pubkey"],
            "value": 10
        }
    ],
    "type": "transaction"
}

print(Fore.CYAN + str(pubkey == tx.outputs[0]["pubkey"]))
print(Style.RESET_ALL)
tx = Transaction.from_json(tx_json)
key_test = VerifyKey(pubkey, encoder=nacl.encoding.HexEncoder)
print("Key: ", key_test)


if tx.verify_signature(pubkey, signature):
    print(Fore.GREEN + "The signature is valid!")
else:
    print(Fore.RED + "The signature is invalid!")

print("\n")
print(Fore.YELLOW + "Message: ", tx.remove_signatures().get_canonical_json_bytes())
print("Signature: ", signature)
print("Public Key: ", pubkey)
print(Style.RESET_ALL + "\n")
