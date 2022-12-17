from network.NodeNetworking import *
from database.KnownNodesHandler import *
from config import *

from object.Block import *

from Miner import Miner

from utility.other_utilities import *

def main():
    reset_objects_file() # makes it easier to debug fetching the chaintip

    KnownNodesHandler.load_known_nodes()
    KnownNodesHandler.set_active_nodes()

    ObjectHandler.load_objects()
    ObjectHandler.update_id_to_index()

    NodeNetworking.start_server()


if __name__ == "__main__":
    main()
