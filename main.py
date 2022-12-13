from network.NodeNetworking import *
from database.KnownNodesHandler import *
from config import *

from object.Block import *

from Miner import Miner

def main():
    #NETWORKING = NodeNetworking(KnownNodesHandler)

    KnownNodesHandler.load_known_nodes()
    KnownNodesHandler.set_active_nodes()

    ObjectHandler.load_objects()
    ObjectHandler.update_id_to_index()

    NodeNetworking.start_server()


if __name__ == "__main__":
    main()
    #mined_block = Miner.mine(SAMPLE_BLOCK)
