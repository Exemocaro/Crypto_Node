import json


def generate_hello_message():
    return b'{"type": "hello", "version": "0.8.0", "agent": "Kerma-Core Client 0.8"}\n'


def generate_getpeers_message():
    return b'{"type": "getpeers"}\n'


def generate_peers_message(peers):
    return str.encode(str(json.dumps({"type": "peers", "peers": peers}) + "\n"))


def generate_error_message(error):
    return str.encode(str(json.dumps({"type": "error", "error": error}) + "\n"))
