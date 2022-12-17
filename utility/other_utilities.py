import json

from config import *

# Reset the known_objects.json file to only contain the genesis block
def reset_objects_file():
    with open('known_objects.json', 'w') as f:
        f.write(json.dumps(GENESIS_BLOCK))
    print('known_objects.json file reset')
