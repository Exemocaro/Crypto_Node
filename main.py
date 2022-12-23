from network.NodeNetworking import NodeNetworking
from database.KnownNodesHandler import KnownNodesHandler
from engine.MessageGenerator import MessageGenerator
from config import *

from object.Block import *

from Miner import Miner

from utility.other_utilities import *

from database.UTXO import UTXO

def main():
    reset_objects_file() # makes it easier to debug fetching the chaintip

    UTXO.clear()
    UTXO.start_auto_save()
    UTXO.save()
    ObjectHandler.start_auto_save()
    

    # Let user change agent_name if it is the default
    if MessageGenerator.agent_name == "THIS COULD BE YOUR NODE":
        MessageGenerator.agent_name = input("Enter a name for your node: ")
    #    agent_name = input("Enter a name for your node: ")

    KnownNodesHandler.clear_known_nodes()
    #KnownNodesHandler.load_known_nodes()
    KnownNodesHandler.set_active_nodes()

    ObjectHandler.load_objects()
    ObjectHandler.update_id_to_index()

    NodeNetworking.start_server()


if __name__ == "__main__":
    main()
