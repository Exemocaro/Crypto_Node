from network.NodeNetworking import *
from database.KnownNodesHandler import *
from config import *


def main():
    #NETWORKING = NodeNetworking(KnownNodesHandler)
    NodeNetworking.start_server()

if __name__ == "__main__":
    main()
