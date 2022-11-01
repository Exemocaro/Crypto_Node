import logging


class KnownNodesHandler:
    def __init__(self, known_nodes_file):
        self.known_nodes = []
        self.known_nodes_file = known_nodes_file
        self.load_known_people()
        pass

    def load_known_people(self):
        try:
            with open(self.known_nodes_file, "r") as f:
                for line in f:
                    self.known_nodes.append(line.strip())
        except Exception as e:
            print(f"\nError on loadKnownNodes! {e} | {e.args}\n")
            logging.error(f"| ERROR | {e} | {e.args}")
            pass
        finally:
            pass

    def add_node(self, node):
        if node not in self.known_nodes:
            self.known_nodes.append(node)
            self.save_known_nodes()
        else:
            pass

    def save_known_nodes(self):
        with open(self.known_nodes_file, "w") as f:
            # clear file first
            f.truncate(0)

            for node in self.known_nodes:
                try:
                    f.write(f"{node}\n")
                except Exception as e:
                    print(f"\nError on saveKnownNodes! {e} | {e.args}\n")
                    logging.error(f"| ERROR | {e} | {e.args}")
                    pass
        pass

    def get_known_nodes(self):
        return self.known_nodes

    # Making handling ip and port easier

    def is_ip_known(self, ip):
        known_ips = []
        for node in self.known_nodes:
            known_ips.append(node.split(":")[0])
        if ip in self.known_ips:
            return True
        else:
            return False

    def get_full_credentials(self, ip):
        if self.is_ip_known(ip):
            for credentials in self.known_nodes:
                if ip == credentials.split(":")[0]:
                    return credentials
        return None
