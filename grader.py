import socket
import json
import random
from utility.credentials_utility import *
import colorama
from colorama import Fore

jans_ip = "4.231.16.23"
mateus_ip = "143.244.205.206"
simaos_ip = "139.59.205.101"
localhost = "127.0.0.1"

ip_names = {
    "4.231.16.23": "Jan",
    "143.244.205.206": "Mateus",
    "139.59.205.101": "Simao",
    "127.0.0.1": "Localhost",
    "128.130.122.101": "Bootstrapping node",
    "51.137.60.68": "Petr",
}

MESSAGE_SIZE = 1024
TIMEOUT_SECONDS = 2

random_other_peers = ["104.248.100.76", "51.137.60.68"]

ips_to_check = random_other_peers



def check_host(graded_ip):
    if graded_ip in ip_names:
        print(Fore.RESET + "Running grader on " + ip_names[graded_ip])
    else:
        print(Fore.RESET + "Running Grader on " + graded_ip + "...\n")

    buffer = ""
    message_stack = []

    # create socket, check if it can connect
    try:
        client_socket = socket.socket()
        client_socket.connect((graded_ip, 18018))
        client_socket.settimeout(TIMEOUT_SECONDS)
        print(Fore.RESET + "Connected to " + graded_ip + ":18018")
    except socket.error as e:
        print(Fore.RED + "FAILED: Couldn't connect to " + graded_ip + ":18018")
        return False

    # we should receive a hello message from the node first
    try:
        while "\n" not in buffer:
            buffer += client_socket.recv(MESSAGE_SIZE).decode("utf-8")
    except socket.error as e:
        print(Fore.RED + "FAILED: Couldn't receive hello message from " + graded_ip + ":18018 in time (" + str(TIMEOUT_SECONDS) + "s)")

    message_stack = buffer.split("\n")[0:-1]
    buffer = buffer.split("\n")[-1]

    if len(message_stack) != 0:
        data_string = message_stack.pop(0)

        # check if the hello message is valid
        try:
            data_json = json.loads(data_string)

            all_success = True

            # see if type is included
            if "type" not in data_json:
                print(Fore.RED + "FAILED: Hello message doesn't contain type")
                print(Fore.RED + "Received: " + data_string)
                all_success = False
            elif data_json["type"] != "hello":
                print(Fore.RED + "FAILED: First message isn't a hello message")
                print(Fore.RED + "Received: " + data_string)
                all_success = False
            else:
                if "version" not in data_json:
                    print(Fore.RED + "FAILED: Hello message doesn't contain version")
                    print(Fore.RED + "Received: " + data_string)
                    all_success = False
                elif data_json["version"][:4] != "0.8.":
                    print(Fore.RED + "FAILED: Hello message doesn't start with 0.8")
                    print(Fore.RED + "Received: " + data_string)
                    all_success = False

                if "agent" not in data_json:
                    print(Fore.RED + "FAILED: Hello message doesn't contain agent")
                    print(Fore.RED + "Received: " + data_string)
                    all_success = False
                elif data_json["agent"] == "Kerma−Core Client 0.8":
                    print(Fore.RED + "FAILED: Agent in hello message not changed")
                    print(Fore.RED + "Received: " + data_string)
                    all_success = False

            if all_success:
                print(Fore.GREEN + "SUCCESS: First message is a valid hello message")

        except Exception as e:
            print(Fore.RED + "FAILED: Couldn't decode first message")
            print(Fore.RED + "Received: " + data_string)

    if len(message_stack) == 0:
        # then we should receive a getpeers message
        try:
            while "\n" not in buffer:
                buffer += client_socket.recv(MESSAGE_SIZE).decode("utf-8")
        except socket.error as e:
                print(Fore.RED + "FAILED: Couldn't receive getpeers message from " + graded_ip + ":18018 in time (" + str(TIMEOUT_SECONDS) + "s)")

        message_stack = buffer.split("\n")[0:-1]
        buffer = buffer.split("\n")[-1]

    if len(message_stack) != 0:

        data_string = message_stack.pop(0)
        # check if the getpeers message is valid
        try:
            data_json = json.loads(data_string)
            if "type" not in data_json:
                print(Fore.RED + "FAILED: Getpeers message doesn't contain type")
                print(Fore.RED + "Received: " + data_string)
            elif data_json["type"] != "getpeers":
                print(Fore.RED + "FAILED: Second message isn't a getpeers message")
                print(Fore.RED + "Received: " + data_string)
            else:
                print(Fore.GREEN + "SUCCESS: Second message is a valid getpeers message")

        except Exception as e:
            print(Fore.RED + "FAILED: Couldn't decode getpeers message")
            print(Fore.RED + "Received: " + data_string)

        # we should send a hello message, otherwise the node will disconnect
        try:
            client_socket.sendall(b'{"type":"hello","version":"0.8.0","agent":"Fake Grader"}\n')
            print(Fore.RESET + "INFO: Sent hello message")
        except socket.error as e:
            print(Fore.RED + "FAILED: Couldn't send hello message")

    # there might be a hello message from the node, but we don't care about it
    clear_incoming_messages(client_socket)

    # we should send a getpeers message
    try:
        client_socket.sendall(b'{"type": "getpeers"}\n')
    except socket.error as e:
        print(Fore.RED + "FAILED: Couldn't send getpeers message")

    # we should receive a peers message
    buffer = ""
    try:
        while "\n" not in buffer:
            buffer += client_socket.recv(MESSAGE_SIZE).decode("utf-8")
    except socket.error as e:
        print(Fore.RED + "FAILED: Couldn't receive peers message in time (" + str(TIMEOUT_SECONDS) + "s)")

    message_stack = buffer.split("\n")[0:-1]
    buffer = buffer.split("\n")[-1]

    if len(message_stack) != 0:
        # check if the peers message is valid
        data_string = message_stack.pop(0)
        try:
            data_json = json.loads(data_string)
            if "type" not in data_json:
                print(Fore.RED + "FAILED: Peers message doesn't contain type")
                print(Fore.RED + "Received: " + data_string)
            elif data_json["type"] != "peers":
                print(Fore.RED + "FAILED: Peers message isn't a peers message")
                print(Fore.RED + "Received: " + data_string)
            else:
                print(Fore.GREEN + "SUCCESS: Peers message is a valid peers message")

        except Exception as e:
            print(Fore.RED + "FAILED: Couldn't decode peers message")
            print(Fore.RED + "Received: " + data_string)

    # Checkpoint: We have tested the basic functionality of the node

    # quickly empty out all incoming messages
    clear_incoming_messages(client_socket)

    # lets send invalid messages
    try:
        client_socket.sendall(b'{"te": "get\n')
        print(Fore.RESET + "INFO: Sent invalid message")
    except socket.error as e:
        print(Fore.RED + "FAILED: Couldn't send invalid message")

    # we should receive an error message
    data = ""
    try:
        while "\n" not in data:
            data += client_socket.recv(MESSAGE_SIZE).decode("utf-8")
    except socket.error as e:
        print(Fore.RED + "FAILED: Couldn't receive error message in time (" + str(TIMEOUT_SECONDS) + "s)")

    if data is not None:
        # check if the error message is valid
        data_string = data.split("\n")[0]
        try:
            items = data_string.split("\n")
            for item in items:
                data_json = json.loads(item)
                if "type" not in data_json:
                    print(Fore.RED + "FAILED: Error message doesn't contain type")
                    print(Fore.RED + "Received: " + item)
                elif data_json["type"] != "error":
                    print(Fore.RED + "FAILED: Error message isn't a error message")
                    print(Fore.RED + "Received: " + item)
                else:
                    print(Fore.GREEN + "SUCCESS: Error message is a valid error message")

        except Exception as e:
            print(Fore.RED + "FAILED: Couldn't decode error message")

    # Now test the peers and storing of peers
    # 1. Generate a random peer
    # 2. Send it to the node
    # 3. Check if the node sends it back

    fake_peer = generate_random_peer()

    # clear out all incoming messages
    clear_incoming_messages(client_socket)

    # send the peer to the node
    try:
        message = "{\"type\": \"peers\", \"peers\": [\"" + fake_peer + "\"]}"
        client_socket.sendall(str.encode(message))
        print(Fore.RESET + "INFO: Sent peers message with fake peer " + fake_peer)
    except socket.error as e:
        print(Fore.RED + "FAILED: Couldn't send peer to node")

    # clear out all incoming messages
    clear_incoming_messages(client_socket)

    # send a getpeers message
    try:
        client_socket.sendall(b'{"type": "getpeers"}\n')
        print(Fore.RESET + "INFO: Sent getpeers message")
    except socket.error as e:
        print(Fore.RED + "FAILED: Couldn't send getpeers message")

    # we should receive a peers message
    data = ""
    try:
        while "\n" not in data:
            new_data = client_socket.recv(MESSAGE_SIZE).decode("utf-8")
            if new_data in [None, "", b'']:
                break
            data += new_data
    except socket.error as e:
        print(Fore.RED + "FAILED: Couldn't receive peers message in time (" + str(TIMEOUT_SECONDS) + "s)")

    for line in data.split("\n"):
        if line == "":
            continue
        try:
            data_json = json.loads(line)
            if "type" not in data_json:
                print(Fore.RED + "FAILED: Peers message doesn't contain type")
                print(Fore.RED + "Received: " + line)
            elif data_json["type"] != "peers":
                print(Fore.RED + "FAILED: Expected peers message")
                print(Fore.RED + "Received: " + line)
            else:
                # check if the peer is in the message
                if fake_peer not in data_json["peers"]:
                    print(Fore.RED + "FAILED: The peer is not in the peers message")
                else:
                    print(Fore.GREEN + "SUCCESS: The peer is in the peers message")
                    break

        except Exception as e:
            print(Fore.RED + "FAILED: Couldn't decode peers message")
            print(Fore.RED + "Received: " + data_string)

    # Last check: Multimessages and split messages
    # 1. Send a message that is split in two

    # TODO

    print(Fore.RESET + "Test finished\n\n")


def generate_random_peer():
    # generate a random ip
    peer_ip = ".".join([str(random.randint(0, 255)) for _ in range(4)])
    # generate a random port
    port = random.randint(0, 65535)
    return peer_ip + ":" + str(port)


def clear_incoming_messages(client_socket):
    try:
        data = True
        client_socket.setblocking(False)
        while data not in [None, False, "", b'']:
            data = client_socket.recv(MESSAGE_SIZE)
    except socket.error as e:
        pass
    finally:
        client_socket.setblocking(True)


for ip in ips_to_check:
    check_host(ip)
