import xmlrpc.client
import sys
import time
import random

server_address = sys.argv[1]
print("Start client...")
with xmlrpc.client.ServerProxy(server_address) as server:
    while True:
        update_timestamp = server.update_doc()

        time_to_sleep = random.randint(0, 10)
        print("Sleeping for " + time_to_sleep)
        time.sleep(time_to_sleep)

        last_modified = server.get_last_modified()
        if (update_timestamp == last_modified):
            print("There were no new modifications.")
        else:
            print("There is a new modification!")