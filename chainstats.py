from database.ObjectHandler import ObjectHandler
from json_keys import *
# Just some stats for the chain / known blocks

ObjectHandler.load_objects()

chaintip = ObjectHandler.get_chaintip()
print(f"Chaintip: {chaintip}")
current_block = ObjectHandler.get_object(chaintip)
print(f"Current block: {current_block}")
chaintip_coinbase_txid = current_block[txids_key][0]
chaintip_coinbase = ObjectHandler.get_object(chaintip_coinbase_txid)
chaintip_height = chaintip_coinbase[height_key]

print(f"Chaintip: {chaintip}")

# get average block time
diff_sum = 0
while current_block["previd"] is not None:
    next_block = ObjectHandler.get_object(current_block["previd"])
    time_diff = current_block["created"] - next_block["created"]
    diff_sum += time_diff
    current_block = next_block

print(f"Difference sum: {diff_sum}")
print(f"Average block time: {diff_sum / chaintip_height} seconds")

current_block = ObjectHandler.get_object(chaintip)
# get average block time of latest 50 blocks
diff_sum = 0
for i in range(50):
    next_block = ObjectHandler.get_object(current_block["previd"])
    time_diff = current_block["created"] - next_block["created"]
    diff_sum += time_diff
    current_block = next_block
    if current_block["previd"] is not None:
        break

print(f"Difference sum: {diff_sum}")
print(f"Average block time: {diff_sum / 50} seconds")
