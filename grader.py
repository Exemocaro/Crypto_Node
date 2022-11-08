import socket
import json
from random import randint

from nacl.encoding import Base64Encoder

from utility.credentials_utility import *
import colorama
from colorama import Fore
import time
import binascii

from engine.Transaction import *
from engine.CoinbaseTransaction import *
from engine.generateMessage import *
from engine.Object import *

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

random_other_peers = [jans_ip, mateus_ip, simaos_ip, localhost, "51.137.60.68"]

ips_to_check = random_other_peers



def check_host(graded_ip):
    if graded_ip in ip_names:
        print(Fore.RESET + "Running grader on " + ip_names[graded_ip])
    else:
        print(Fore.RESET + "Running Grader on " + graded_ip + "...\n")
        
    result = 0
    result_json = {
        "ip": graded_ip,
        "results": []
    }

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
        result_json["results"].append({"name": "connect", "result": 0})
        return result_json

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
                print(Fore.RED + " -> received: " + data_string)
                all_success = False
            elif data_json["type"] != "hello":
                print(Fore.RED + "FAILED: First message isn't a hello message")
                print(Fore.RED + " -> received: " + data_string)
                all_success = False
            else:
                if "version" not in data_json:
                    print(Fore.RED + "FAILED: Hello message doesn't contain version")
                    print(Fore.RED + " -> received: " + data_string)
                    all_success = False
                elif data_json["version"][:4] != "0.8.":
                    print(Fore.RED + "FAILED: Hello message doesn't start with 0.8")
                    print(Fore.RED + " -> received: " + data_string)
                    all_success = False

                if "agent" not in data_json:
                    print(Fore.RED + "FAILED: Hello message doesn't contain agent")
                    print(Fore.RED + " -> received: " + data_string)
                    all_success = False
                elif data_json["agent"] == "Kerma−Core Client 0.8":
                    print(Fore.RED + "FAILED: Agent in hello message not changed")
                    print(Fore.RED + " -> received: " + data_string)
                    all_success = False

            if all_success:
                print(Fore.GREEN + "SUCCESS: First message is a valid hello message")
                result += 1

        except Exception as e:
            print(Fore.RED + "FAILED: Couldn't decode first message")
            print(Fore.RED + " -> received: " + data_string)

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
                print(Fore.RED + " -> received: " + data_string)
            elif data_json["type"] != "getpeers":
                print(Fore.RED + "FAILED: Second message isn't a getpeers message")
                print(Fore.RED + " -> received: " + data_string)
            else:
                print(Fore.GREEN + "SUCCESS: Second message is a valid getpeers message")
                result += 1

        except Exception as e:
            print(Fore.RED + "FAILED: Couldn't decode getpeers message")
            print(Fore.RED + " -> received: " + data_string)

        # we should send a hello message, otherwise the node will disconnect
        try:
            client_socket.sendall(b'{"type":"hello","version":"0.8.0","agent":"Fake Grader"}\n')
            print(Fore.RESET + "INFO: Sent hello message")
        except socket.error as e:
            print(Fore.RED + "FAILED: Couldn't send hello message")

    # there might be a hello message from the node, but we don't care about it
    # so first wait, then clear message stack
    time.sleep(1)
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
                print(Fore.RED + " -> received: " + data_string)
            elif data_json["type"] != "peers":
                print(Fore.RED + "FAILED: Peers message isn't a peers message")
                print(Fore.RED + " -> received: " + data_string)
            else:
                print(Fore.GREEN + "SUCCESS: Peers message is a valid peers message")
                result += 1

        except Exception as e:
            print(Fore.RED + "FAILED: Couldn't decode peers message")
            print(Fore.RED + " -> received: " + data_string)

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
                    print(Fore.RED + " -> received: " + item)
                elif data_json["type"] != "error":
                    print(Fore.RED + "FAILED: Error message isn't a error message")
                    print(Fore.RED + " -> received: " + item)
                else:
                    print(Fore.GREEN + "SUCCESS: Error message is a valid error message")
                    result += 1

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
        message = "{\"type\": \"peers\", \"peers\": [\"" + fake_peer + "\"]}\n"
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
                print(Fore.RED + " -> received: " + line)
            elif data_json["type"] != "peers":
                print(Fore.RED + "FAILED: Expected peers message")
                print(Fore.RED + " -> received: " + line)
            else:
                # check if the peer is in the message
                if fake_peer not in data_json["peers"]:
                    print(Fore.RED + "FAILED: The peer is not in the peers message")
                else:
                    print(Fore.GREEN + "SUCCESS: The peer is in the peers message")
                    result += 1
                    break

        except Exception as e:
            print(Fore.RED + "FAILED: Couldn't decode peers message")
            print(Fore.RED + " -> received: " + data_string)

    # Last check: Multimessages and split messages
    # 1. Send a message that is split in two

    # TODO for Task 1:
    #  - Send a message that is split in two
    #  - Send multiple messages in one sendall call
    #  - Check how node handles disconnection

    result_text = "[" + str(result) + "/" + str(5) + "]"

    result_json["results"].append({"name": "Task 1", "points": result, "total": 5})

    print(Fore.RESET + "Task 1 test finished: " + result_text + "\n\n")

    # TASK 2

    result = 0

    # if we send a new object with ihaveobject, the node should send us the object when we ask for it
    # 1. Generate a new keypair
    # 2. Generate a new coinbase transaction with the public key
    # 3. Send the ihaveobject message to the node
    # 4. Node should ask for the object
    # 5. Send the object to the node
    # 6. Send getobject message
    # 7. Node should send the transaction from before

    # 1. generate a new keypair
    private_key = SigningKey.generate()
    public_key = private_key.verify_key

    # 2. generate a new coinbase transaction
    coinbase_tx_json = {
        "height": 0,
        "outputs": [
            {
                "pubkey": public_key.encode(encoder=Base64Encoder).decode("utf-8"),
                "value": 1000
            }
        ],
    }
    print(public_key.encode(encoder=Base64Encoder).decode("utf-8"))
    coinbase_tx = CoinbaseTransaction.from_json(coinbase_tx_json)
    coinbase_txid = coinbase_tx.get_id()

    message = "{\"type\": \"ihaveobject\", \"object_id\": \"" + coinbase_txid + "\"}\n"

    # clear out all incoming messages
    time.sleep(1)
    clear_incoming_messages(client_socket)

    # 3. send the ihaveobject message
    try:
        client_socket.sendall(str.encode(message))
        print(Fore.RESET + "INFO: Sent ihaveobject message with txid " + coinbase_txid[:10] + "...")
    except socket.error as e:
        print(Fore.RED + "FAILED: Couldn't send ihaveobject message")

    # 4. see if the node asks for the object
    data = ""
    try:
        while "\n" not in data:
            new_data = client_socket.recv(MESSAGE_SIZE).decode("utf-8")
            if new_data in [None, "", b'']:
                break
            data += new_data
    except socket.error as e:
        print(Fore.RED + "FAILED: Couldn't receive getobject message in time (" + str(TIMEOUT_SECONDS) + "s)")

    for line in data.split("\n"):
        if line == "":
            continue
        try:
            data_json = json.loads(line)
            if "type" not in data_json:
                print(Fore.RED + "FAILED: Getobject message doesn't contain type")
                print(Fore.RED + " -> received: " + line)
            elif data_json["type"] != "getobject":
                print(Fore.RED + "FAILED: Expected getobject message")
                print(Fore.RED + " -> received: " + line)
            else:
                # check if the object_id is in the message
                if coinbase_txid not in data_json["object_id"]:
                    print(Fore.RED + "FAILED: The object_id is not in the getobject message")
                else:
                    print(Fore.GREEN + "SUCCESS: The object_id is in the getobject message")
                    result += 1
                    break
        except Exception as e:
            print(Fore.RED + "FAILED: Couldn't decode getobject message")
            print(Fore.RED + " -> received: " + line)

    # 5. send the object to the node
    try:
        message = "{\"type\": \"object\", \"object\": " + json.dumps(coinbase_tx.get_json()) + "}\n"
        client_socket.sendall(str.encode(message))
        print(Fore.RESET + "INFO: Sent coinbase transaction")
    except socket.error as e:
        print(Fore.RED + "FAILED: Couldn't send object message")

    # 6. send the getobject message
    message = "{\"type\": \"getobject\", \"object_id\": \"" + coinbase_txid + "\"}\n"
    try:
        client_socket.sendall(str.encode(message))
        print(Fore.RESET + "INFO: Sent getobject message with txid " + coinbase_txid[:10] + "...")
    except socket.error as e:
        print(Fore.RED + "FAILED: Couldn't send getobject message")

    # 7. see if the node sends the transaction
    data = ""
    try:
        while "\n" not in data:
            new_data = client_socket.recv(MESSAGE_SIZE).decode("utf-8")
            if new_data in [None, "", b'']:
                break
            data += new_data
    except socket.error as e:
        print(Fore.RED + "FAILED: Couldn't receive transaction in time (" + str(TIMEOUT_SECONDS) + "s)")

    for line in data.split("\n"):
        if line == "":
            continue
        try:
            data_json = json.loads(line)
            if "type" not in data_json:
                print(Fore.RED + "FAILED: Transaction message doesn't contain type")
                print(Fore.RED + " -> received: " + line)
            elif data_json["type"] != "object":
                print(Fore.RED + "FAILED: Expected transaction message")
                print(Fore.RED + " -> received: " + line)
            else:
                # calculate the transaction id
                tx = data_json["object"]
                txid = Object.get_id_from_json(tx)

                # check if the transaction id matches the one we sent
                if txid != coinbase_txid:
                    print(Fore.RED + "FAILED: The transaction id doesn't match / Wrong transaction")
                    print(Fore.RED + " -> received: " + data_json + " with id " + txid[:10] + "...")
                else:
                    print(Fore.GREEN + "SUCCESS: The transaction id matches")
                    result += 1
                    break
        except Exception as e:
            print(Fore.RED + "FAILED: Couldn't decode transaction message")
            print(Fore.RED + " -> received: " + line)

    # Print the result
    total_points = 2
    result_text = "[" + str(result) + "/" + str(total_points) + "]"
    result_json["results"].append({"name": "Task 2", "points": result, "total": total_points})

    return result_json


def generate_random_peer():
    # generate a random ip
    peer_ip = ".".join([str(randint(0, 255)) for _ in range(4)])
    # generate a random port
    port = randint(0, 65535)
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


results = []

for ip in ips_to_check:
    res = check_host(ip)
    results.append(res)

print(Fore.RESET + "\n\nAll tests finished\n")
print(Fore.RESET + "==================")
print(Fore.RESET + "\nResults:\n")

for res in results:
    ip = res["ip"]
    if ip in ip_names:
        ip = ip_names[ip]
    print(Fore.RESET + "Results for " + ip + ":")

    if res["results"][0]["name"] == "connect":
        print(Fore.RED + "  FAILED: Couldn't connect to node\n")
        continue
    for result in res["results"]:
        task_name = result["name"]
        points = result["points"]
        total = result["total"]
        if points == total:
            print(Fore.GREEN + "  " + task_name + ": " + str(points) + "/" + str(total))
        else:
            print(Fore.RED + "  " + task_name + ": " + str(points) + "/" + str(total))
    print("")

print("\n")


