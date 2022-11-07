from network.NewServer import *
from database.KnownNodesHandler import *
from config import *


def main():
    networking = NodeNetworking(NODE_HANDLER)
    networking.start_server()


if __name__ == "__main__":
    main()
