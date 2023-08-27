import json

from config import *


# Reset the known_objects.json file to only contain the genesis block
def reset_objects_file():
    with open("database/known_objects.json", "w") as f:
        f.write(
            json.dumps(
                [
                    {
                        "type": "block",
                        "validity": "valid",
                        "txid": "00000000a420b7cefa2b7730243316921ed59ffe836e111ca3801f82a4f5360e",
                        "object": GENESIS_BLOCK,
                    }
                ],
                indent=4,
            )
        )
    print("known_objects.json file reset")
