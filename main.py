from network.NodeNetworking import NodeNetworking
from database.KnownNodesHandler import KnownNodesHandler
from engine.MessageGenerator import MessageGenerator
from config import *

from object.Block import *

from Miner import Miner

from utility.other_utilities import *

from database.UTXO import UTXO


def main():
    mode = "testing"  # "testing", "production" or "grading"

    ObjectHandler.start_auto_save()
    TimeTracker.regularly_print_stats()

    if mode == "grading":
        reset_objects_file()  # makes it easier to debug fetching the chaintip
        KnownNodesHandler.clear_known_nodes()

    if mode == "production":
        KnownNodesHandler.load_known_nodes()
        ObjectHandler.load_objects()
        ObjectHandler.update_id_to_index()

    if mode == "testing":
        reset_objects_file()
        KnownNodesHandler.add_node(BOOTSTRAP_NODE)

    # Let user change agent_name if it is the default
    if MessageGenerator.agent_name == "THIS COULD BE YOUR NODE":
        MessageGenerator.agent_name = input("Enter a name for your node: ")

    KnownNodesHandler.set_active_nodes()

    ObjectHandler.load_objects()
    ObjectHandler.update_id_to_index()

    NodeNetworking.start_server()


if __name__ == "__main__":
    main()
