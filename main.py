from network.NodeNetworking import *
from database.KnownNodesHandler import *
from config import *


def main():
    #NETWORKING = NodeNetworking(KnownNodesHandler)

    KnownNodesHandler.load_known_nodes()
    KnownNodesHandler.set_active_nodes()

    ObjectHandler.load_objects()
    ObjectHandler.update_id_to_index()

    NodeNetworking.start_server()


if __name__ == "__main__":
    # clear the two files
    with open(ADDRESSES_FILE, "w") as f:
        f.truncate(0)
        f.close()
    with open(OBJECTS_FILE, "w") as f:
        f.truncate(0)
        f.close()
    main()
