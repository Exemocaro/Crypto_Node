import json

from config import *
from json_keys import *


class MessageGenerator:
    agent_name = AGENT_NAME

    @staticmethod
    def generate_hello_message():
        """ Generates a hello message as bytes """
        message_json = {type_key: hello_key, version_key: "0.8.0", agent_key: AGENT_NAME}
        return MessageGenerator.get_bytes_from_json(message_json)

    @staticmethod
    def generate_getpeers_message():
        """ Generates a getpeers message as bytes """
        message_json = {type_key: getpeers_key}
        return MessageGenerator.get_bytes_from_json(message_json)

    @staticmethod
    def generate_peers_message(peers):
        """ Generates a peers message as bytes with the given peers """
        message_json = {type_key: peers_key, peers_key: peers}
        return MessageGenerator.get_bytes_from_json(message_json)

    @staticmethod
    def generate_error_message(error):
        """ Generates an error message as bytes with the given error """
        message_json = {type_key: error_key, error_key: error}
        return MessageGenerator.get_bytes_from_json(message_json)

    @staticmethod
    def get_bytes_from_json(message_json):
        """ Converts a json object to bytes """
        return str.encode(json.dumps(message_json) + "\n")

    @staticmethod
    def generate_ihaveobject_message(object_id):
        """ Generates an ihaveobject message as bytes with the given object id """
        message_json = {type_key: ihaveobject_key, objectid_key: object_id}
        return MessageGenerator.get_bytes_from_json(message_json)

    @staticmethod
    def generate_getobject_message(object_id):
        """ Generates a getobject message as bytes with the given object id """
        message_json = {type_key: getobject_key, objectid_key: object_id}
        return MessageGenerator.get_bytes_from_json(message_json)

    @staticmethod
    def generate_object_message(object_data):
        """ Generates an object message as bytes with the given object data """
        message_json = {type_key: object_key, object_key: object_data}
        return MessageGenerator.get_bytes_from_json(message_json)

    @staticmethod
    def generate_getchaintip_message():
        """ Generates a getchaintip message as bytes """
        message_json = {type_key: getchaintip_key}
        return MessageGenerator.get_bytes_from_json(message_json)

    @staticmethod
    def generate_chaintip_message(block_id):
        """ Generates a chaintip message as bytes with the given block id """
        message_json = {type_key: chaintip_key , blockid_key: block_id}
        return MessageGenerator.get_bytes_from_json(message_json)
        
    @staticmethod
    def generate_getmempool_message():
        """ Generates a getmempool message as bytes """
        message_json = {type_key: getmempool_key}
        return MessageGenerator.get_bytes_from_json(message_json)

    @staticmethod
    def generate_mempool_message(txids):
        """ Generates a mempool message as bytes with the given mempool / list of txids """
        message_json = {type_key: mempool_key, txids_key: txids}
        return MessageGenerator.get_bytes_from_json(message_json)

