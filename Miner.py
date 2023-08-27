import jsonschema
from time import sleep
from threading import Thread
from queue import Queue

from utility.json_validation import block_schema

from object.Object import Object

NONCE_OFFSET = 10**18


class Miner:
    @staticmethod
    def mine(block_json, start_nonce=0, thread_num=4):
        try:
            jsonschema.validate(block_json, block_schema)
        except jsonschema.exceptions.ValidationError as e:
            return False

        # create a queue to receive results from each thread
        result_queue = Queue()

        # one queue to receive the nonce from each thread
        nonce_queues = [Queue() for _ in range(thread_num)]

        start_nonces = [start_nonce + i * NONCE_OFFSET for i in range(thread_num)]

        # create a list of threads
        threads = [
            Thread(
                target=Miner.mine_thread,
                args=(block_json, start_nonces[i], result_queue, nonce_queues[i]),
            )
            for i in range(thread_num)
        ]

        print("Start nonces are: ", start_nonces)

        print("Start mining...")
        # start all threads
        for thread in threads:
            thread.start()
            sleep(0.5)

        # print current nonce
        # get the nonce from each thread, print them in one line
        # make sure they are in the right order
        while True:
            # always just get the last nonce, clear the queue
            nonces = [int(nonce_queues[i].get()) for i in range(thread_num)]
            # sort nonces
            nonces.sort()
            # print(f"\x1b[KCurrent nonces: {nonces}", end="\n")
            if not result_queue.empty():
                break

        # wait for first thread to finish
        result = result_queue.get()

        # force stop all threads
        for thread in threads:
            thread.join()

        return result

    @staticmethod
    def mine_thread(block_json, start_nonce, result_queue, nonce_queue):
        block_json["nonce"] = str(start_nonce)
        hash = Object.get_id_from_json(block_json)
        print("Nonce shall be ", str(start_nonce))
        print("Start with nonce ", block_json["nonce"])
        sleep(1)
        while int(hash, 16) > int(block_json["T"], 16):
            block_json["nonce"] = str(int(block_json["nonce"]) + 1)
            hash = Object.get_id_from_json(block_json)
            print(block_json["nonce"], end="\n")
            nonce_queue.put(block_json["nonce"])
            sleep(0.1)

        print("Found nonce ", block_json["nonce"])

        result_queue.put(block_json)
