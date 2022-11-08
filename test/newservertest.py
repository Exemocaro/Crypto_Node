
from network.NodeNetworking import *
from database.KnownNodesHandler import *

from config import *

#HOST = "192.168.56.1" # LOCAL
#HOST = "143.244.205.206"  # MATEUS
#HOST = "4.231.16.23" # JAN
#HOST = "128.130.122.101" # bootstrapping node
HOST = "127.0.0.1" # localhost

host = HOST
port = PORT

node_networking = NodeNetworking()


def main():
    node_networking.start_server()

    peer_db = KnownNodesHandler("../database/known_credentials.txt")
    peer_db.load_known_nodes()

    print(peer_db.known_nodes)

    node_networking.connect_to_node(HOST + ":" + str(PORT))

    message = json.dumps({"type": "hello", "version": "0.8.0", "agent": "New Test Client"})
    node_networking.send_to_node(HOST + ":" + str(PORT), message)


if __name__ == "__main__":
    main()