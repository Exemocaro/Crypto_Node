import json
import json_canonical
import hashlib

from abc import ABC, abstractmethod


class Object(ABC):

    @abstractmethod
    def get_json(self):
        pass

    def get_canonical_json_bytes(self):
        return json_canonical.canonicalize(self.get_json())

    def get_id(self):
        return Object.get_id_from_json(self.get_json())

    @staticmethod
    def get_id_from_json(json):
        return hashlib.sha256(json_canonical.canonicalize(json)).digest().hex()

    @staticmethod
    @abstractmethod
    def from_json(json):
        pass

    def __copy__(self):
        return self.from_json(self.get_json())

