import json

def generateHelloMessage():
    return "{'type': 'hello', 'version': '0.8.0', 'agent': 'Kerma-Core Client 0.8'}\n"

def generateGetPeersMessage():
    return "{'type': 'getPeers'}\n"

def generatePeersMessage(peers):
    return str(json.dumps({"type": "peers", "peers": peers}) + "\n")

def generateErrorMessage(error):
    return str(json.dumps({"type": "error", "error": error}) + "\n")