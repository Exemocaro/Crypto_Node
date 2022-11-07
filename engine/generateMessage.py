import json

from config import *


class MessageGenerator:

    @staticmethod
    def generate_hello_message():
        message_json = {"type": "hello", "version": "0.8.0", "agent": AGENT_NAME}
        return MessageGenerator.get_bytes_from_json(message_json)

    @staticmethod
    def generate_getpeers_message():
        message_json = {"type": "getpeers"}
        return MessageGenerator.get_bytes_from_json(message_json)

    @staticmethod
    def generate_peers_message(peers):
        message_json = {"type": "peers", "peers": peers}
        return MessageGenerator.get_bytes_from_json(message_json)

    @staticmethod
    def generate_error_message(error):
        message_json = {"type": "error", "error": error}
        return MessageGenerator.get_bytes_from_json(message_json)

    @staticmethod
    def get_bytes_from_json(message_json):
        return str.encode(json.dumps(message_json) + "\n")
