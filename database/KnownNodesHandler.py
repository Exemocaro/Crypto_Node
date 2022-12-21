from utility.credentials_utility import *
from utility.logplus import *

from config import *


# handles the known nodes database\\
# let's us add and remove nodes
# handles saving to file
class KnownNodesHandler:
    
    known_nodes = []
    known_nodes_file = ADDRESSES_FILE

    @staticmethod
    def load_known_nodes():
        """ Loads the known nodes from the known nodes file"""
        try:
            with open(KnownNodesHandler.known_nodes_file, "r") as f:
                for line in f:
                    KnownNodesHandler.known_nodes.append(line.strip())
        except Exception as e:
            LogPlus.error(f"| ERROR | Couldn't load nodes | {e} | {e.args}")

    @staticmethod
    def add_node(node):
        """ Adds a node to the known nodes list and saves it to file"""
        if is_credentials_format(node) and not KnownNodesHandler.is_node_known(node):
            KnownNodesHandler.known_nodes.append(node)
            KnownNodesHandler.save_known_nodes()

    @staticmethod
    def save_known_nodes():
        """ Saves the known nodes to the known nodes file"""
        with open(KnownNodesHandler.known_nodes_file, "w") as f:
            # clear file first
            f.truncate(0)

            for node in KnownNodesHandler.known_nodes:
                try:
                    f.write(f"{node}\n")
                except Exception as e:
                    LogPlus.error(f"| ERROR | Nodes couldn't be saved | {e} | {e.args}")

    def set_active_nodes():
        """ Sets the active nodes to the known nodes"""
        KnownNodesHandler.active_nodes = KnownNodesHandler.known_nodes


    # Making handling ip and port easier

    @staticmethod
    def is_node_known(node):
        """ Checks if the node is known, only ip has to match"""
        # it's sufficient to check if the ip is known
        ip = get_ip(node)
        return KnownNodesHandler.is_ip_known(ip)

    @staticmethod
    def is_ip_known(ip):
        """ Checks if the ip is known"""
        known_ips = []
        for node in KnownNodesHandler.known_nodes:
            known_ips.append(node.split(":")[0])
        if ip in KnownNodesHandler.known_nodes:
            return True
        else:
            return False

    @staticmethod
    def get_full_credentials(ip):
        """ Returns the full credentials of the ip,
        in other words it returns the credentials with the correct port"""
        if KnownNodesHandler.is_ip_known(ip):
            for credentials in KnownNodesHandler.known_nodes:
                if ip == credentials.split(":")[0]:
                    return credentials
        return None

    @staticmethod
    def clean_credentials(credentials):
        """ If the ip is known, change the port accordingly
        otherwise return the credentials as they are"""
        if KnownNodesHandler.is_ip_known(credentials.split(":")[0]):
            return KnownNodesHandler.get_full_credentials(credentials.split(":")[0])
        else:
            return credentials

