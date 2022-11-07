import logging

from utility.credentials_utility import *
from utility.logplus import *


# handles the known nodes database
# let's us add and remove nodes
# handles saving to file
class KnownNodesHandler:
    def __init__(self, known_nodes_file="known_credentials.txt"):
        self.known_nodes = []
        self.known_nodes_file = known_nodes_file
        self.load_known_nodes()
        self.load_known_nodes()

    # load known nodes from file
    def load_known_nodes(self):
        try:
            with open(self.known_nodes_file, "r") as f:
                for line in f:
                    self.known_nodes.append(line.strip())
        except Exception as e:
            LogPlus.error(f"| ERROR | Couldn't load nodes | {e} | {e.args}")

    # add a node to the known nodes list and save it to file
    def add_node(self, node):
        if is_credentials_format(node) and not self.is_node_known(node):
            self.known_nodes.append(node)
            self.save_known_nodes()

    # save known nodes to file
    def save_known_nodes(self):
        with open(self.known_nodes_file, "w") as f:
            # clear file first
            f.truncate(0)

            for node in self.known_nodes:
                try:
                    f.write(f"{node}\n")
                except Exception as e:
                    LogPlus.error(f"| ERROR | Nodes couldn't be saved | {e} | {e.args}")

    # Making handling ip and port easier

    # check if the ip of the credentials is known
    def is_node_known(self, node):
        # it's sufficient to check if the ip is known
        ip = get_ip(node)
        return self.is_ip_known(ip)

    # check if the ip is known
    def is_ip_known(self, ip):
        known_ips = []
        for node in self.known_nodes:
            known_ips.append(node.split(":")[0])
        if ip in self.known_nodes:
            return True
        else:
            return False

    # if the ip is known, return the full credentials
    def get_full_credentials(self, ip):
        if self.is_ip_known(ip):
            for credentials in self.known_nodes:
                if ip == credentials.split(":")[0]:
                    return credentials
        return None

    # if the ip is known, change the port accordingly
    def clean_credentials(self, credentials):
        if self.is_ip_known(credentials.split(":")[0]):
            return self.get_full_credentials(credentials.split(":")[0])
        else:
            return credentials
