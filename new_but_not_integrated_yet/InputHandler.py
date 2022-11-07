from engine.inputHandling import *
from utility.credentials_utility import *

class InputHandler:

    def __init__(self, networking):
        self.networking

    # This is called when a message is received
    # It calls the appropriate function based on the type of the message
    # It returns the response (as byte-like data) to be sent back to the sender
    # If no response is needed, it returns None
    # If the message is not valid, it returns an error message
    def handle_input(self, data, sender_address):
        try:
            data_parsed = json.loads(str(data, encoding="utf-8"))
        except Exception as e:
            logging.error(f"| ERROR | {sender_address} | HANDLEINPUT | {data} | {e} | {e.args}")
            print(f"\nError on handleInput! {e} | {e.args}\n")
            return generate_error_message("Invalid json.")

        print("Data parsed: ", data_parsed)
        if "type" in data_parsed:
            if data_parsed["type"] == "hello":
                self.handle_hello(data_parsed, sender_address)
            elif data_parsed["type"] == "getpeers":
                self.handle_getpeers(data_parsed, sender_address)
            elif data_parsed["type"] == "peers":
                self.handle_peers(data_parsed, sender_address)
            elif data_parsed["type"] == "error":
                self.handle_error(data_parsed, sender_address)
            else:
                logging.error(f"| ERROR | {sender_address} | HANDLEINPUT | {data} | Unknown message type")
                print(f"\nUnknown message type!\n")
                self.networking.send_to_node(convert_string_to_tuple(sender_address), generate_error_message("Unknown message type!"))


    # This is called when a hello message is received
    def handle_hello(self, data_parsed, sender_address):
        if "version" in data_parsed:
            if data_parsed["version"][:4] == "0.8.":
                print("Just answering hello")
                return generate_hello_message()
            else:
                logging.warning(
                    f"| WARNING | {sender_address} | HELLO | {data_parsed} | Version not supported | {data_parsed['version'][:4]}")
                return generate_error_message("Wrong hello version!")
        else:
            logging.error(f"| ERROR | {sender_address} | HELLO | {data_parsed} | No version in data_parsed")
            return generate_error_message("No version in hello!")


    # This is called when a getpeers message is received
    def handle_getpeers(self, data_parsed, sender_address):
        response = generate_peers_message(KNOWN_CREDENTIALS)
        return response


    # This in called when a peers message is received
    def handle_peers(self, data_parsed, sender_address):
        if "peers" in data_parsed:
            for credential_string in data_parsed["peers"]:
                peer = (credential_string.split(":")[0], int(credential_string.split(":")[1]))
                # if not checkCredentials(peer): # This is to validate, that the address belongs to a valid node
                #    print(f"\nValidating {peer}\n")
                #    validateNode(peer)
                # else:
                #    print(f"\n{peer} already known!\n")
                if peer not in KNOWN_CREDENTIALS:
                    KNOWN_CREDENTIALS.append(peer)
                    print(f"\nAdded {peer} to known credentials!\n")
        else:
            logging.error(f"| ERROR | {sender_address} | PEERS | {data_parsed} | No peers in data_parsed")
            return generate_error_message("No peers in data_parsed!")


    # This is called when an error message is received
    def handle_error(self, data_parsed, sender_address):
        logging.error(f"| ERROR | {sender_address} | ERROR | {data_parsed} | Error message received")
        print(f"\nError message received!\n")
        return generate_error_message("Error message received")
