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

    @staticmethod
    def generate_ihaveobject_message(object_id):
        message_json = {"type": "ihaveobject", "object_id": object_id}
        return MessageGenerator.get_bytes_from_json(message_json)

    @staticmethod
    def generate_getobject_message(object_id):
        message_json = {"type": "getobject", "object_id": object_id}
        return MessageGenerator.get_bytes_from_json(message_json)

    @staticmethod
    def generate_object_message(object_data):
        message_json = {"type": "object", "object": object_data}
        return MessageGenerator.get_bytes_from_json(message_json)

