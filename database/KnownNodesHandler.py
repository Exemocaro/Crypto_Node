import logging

from utility.credentials_utility import *
from utility.logplus import *

from config import *


# handles the known nodes database
# let's us add and remove nodes
# handles saving to file
class KnownNodesHandler:
    
    known_nodes = []
    known_nodes_file = ADDRESSES_FILE


    # load known nodes from file
    @staticmethod
    def load_known_nodes():
        try:
            with open(KnownNodesHandler.known_nodes_file, "r") as f:
                for line in f:
                    KnownNodesHandler.known_nodes.append(line.strip())
        except Exception as e:
            LogPlus.error(f"| ERROR | Couldn't load nodes | {e} | {e.args}")

    # add a node to the known nodes list and save it to file
    @staticmethod
    def add_node(node):
        if is_credentials_format(node) and not KnownNodesHandler.is_node_known(node):
            KnownNodesHandler.known_nodes.append(node)
            KnownNodesHandler.save_known_nodes()

    # save known nodes to file
    @staticmethod
    def save_known_nodes():
        with open(KnownNodesHandler.known_nodes_file, "w") as f:
            # clear file first
            f.truncate(0)

            for node in KnownNodesHandler.known_nodes:
                try:
                    f.write(f"{node}\n")
                except Exception as e:
                    LogPlus.error(f"| ERROR | Nodes couldn't be saved | {e} | {e.args}")

    # determines which nodes from our known nodes are active
    def set_active_nodes():
        KnownNodesHandler.active_nodes = KnownNodesHandler.known_nodes

    # Making handling ip and port easier

    # check if the ip of the credentials is known
    @staticmethod
    def is_node_known(node):
        # it's sufficient to check if the ip is known
        ip = get_ip(node)
        return KnownNodesHandler.is_ip_known(ip)

    # check if the ip is known
    @staticmethod
    def is_ip_known(ip):
        known_ips = []
        for node in KnownNodesHandler.known_nodes:
            known_ips.append(node.split(":")[0])
        if ip in KnownNodesHandler.known_nodes:
            return True
        else:
            return False

    # if the ip is known, return the full credentials
    @staticmethod
    def get_full_credentials(ip):
        if KnownNodesHandler.is_ip_known(ip):
            for credentials in KnownNodesHandler.known_nodes:
                if ip == credentials.split(":")[0]:
                    return credentials
        return None

    # if the ip is known, change the port accordingly
    @staticmethod
    def clean_credentials(credentials):
        if KnownNodesHandler.is_ip_known(credentials.split(":")[0]):
            return KnownNodesHandler.get_full_credentials(credentials.split(":")[0])
        else:
            return credentials


KnownNodesHandler.load_known_nodes()
KnownNodesHandler.set_active_nodes()