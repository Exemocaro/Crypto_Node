from network.NewServer import *
from database.KnownNodesHandler import *


def main():
    peers_db = KnownNodesHandler("database/known_credentials.txt")
    networking = NodeNetworking(peers_db)
    networking.start_server()


if __name__ == "__main__":
    main()
