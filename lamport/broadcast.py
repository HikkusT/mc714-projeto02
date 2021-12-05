from xmlrpc.server import SimpleXMLRPCServer
import xmlrpc.client
import sys
import time
import threading
import random

my_id = int(sys.argv[1])
peer_addresses = sys.argv[2].split(',')
number_of_peers = len(peer_addresses)
my_port = int(sys.argv[3]) if len(sys.argv) > 3 else 8000

# Constants
number_of_iterations = 4
min_sleep_time = 5
max_sleep_time = 15

# Local state
current_time = 0
events = []

def log_event(time, id):
    events.append((time, id))

# Listeners
def receive_event(time, id):
    global current_time
    current_time = max(time, current_time) + 1

    log_event(time, id)
    print("Received from " + str(id) + " with timestamp " + str(time))

def health_check():
    return True


# Senders
def broadcast_event(peers):
    global current_time
    current_time += 1

    log_event(current_time, my_id)
    print("Broadcasting at " + str(current_time))

    for peer in peers:
        peer.receive_event(current_time, my_id)

def wait_all_peers_ready(peers):
    non_ready_peers = peers.copy()
    while len(non_ready_peers) != 0:
        for non_ready_peer in non_ready_peers:
            try:
                non_ready_peer.health_check()
                non_ready_peers.remove(non_ready_peer)
            except:
                pass
    

# Server stuff
server = SimpleXMLRPCServer(("", my_port), allow_none=True, logRequests=False) 
server.register_function(receive_event)
server.register_function(health_check)
server_thread = threading.Thread(target=server.serve_forever)
server_thread.start()

# Client stuff
peers = [xmlrpc.client.ServerProxy(peer_address) for peer_address in peer_addresses]

print("Going to wait")
wait_all_peers_ready(peers)
print("All peers ready")

for iteration in range(number_of_iterations):
    time_to_sleep = random.randint(min_sleep_time, max_sleep_time)
    print("Sleeping for " + str(time_to_sleep))
    time.sleep(time_to_sleep)

    broadcast_event(peers)

time.sleep(max_sleep_time)
print("Order: ")
events.sort(key= lambda event: event[0])
for event in events:
    print(event)
