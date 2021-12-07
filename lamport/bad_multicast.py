from collections import defaultdict
from typing import NamedTuple
from xmlrpc.server import SimpleXMLRPCServer
import xmlrpc.client
import sys
import time
import threading
import random
from datetime import datetime

class Event(NamedTuple):
    message: str

    def __str__(self):
        return f'Event {self.message}'


my_id = int(sys.argv[1])
peer_addresses = sys.argv[2].split(',')
number_of_peers = len(peer_addresses)
my_port = int(sys.argv[3]) if len(sys.argv) > 3 else 8000

# Constants
number_of_iterations = 5
logs_to_show = []
list_of_words= ['price', 'effect', 'friendly', 'soup', 'compact', 'buy', 'valid', 'celebration', 'cigarette', 'purpose', 'brake', 'panic', 'chart', 'abridge', 'ambiguity', 'division', 'dismissal', 'nose', 'battle', 'extent', 'height', 'village', 'childish', 'chord', 'packet', 'clearance', 'blind', 'frequency', 'job', 'determine', 'low', 'sport', 'exaggerate', 'knot', 'vacuum', 'company', 'invite', 'south', 'chip', 'monarch', 'compose', 'deck', 'hardware', 'senior', 'slump', 'leaflet', 'counter', 'recycle', 'arise', 'dividend']

def process_event(event):
    print(f'Processing {event}')

# Listeners
def receive_event(message):
    event = Event(message)
    if 'receive' in logs_to_show:
        print(f'[Receive] Received {event}')
    process_event(event)

def health_check():
    return True

# Senders
def broadcast_event(message):
    event = Event(message)
    if 'send' in logs_to_show:
        print(f'[Send] Broadcasting {event}')
    for peer in peers:
        peer.receive_event(message)

def wait_all_peers_ready():
    non_ready_peers = peers.copy()
    while len(non_ready_peers) != 0:
        for non_ready_peer in non_ready_peers.copy():
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
peers = [xmlrpc.client.ServerProxy(peer_address) for peer_address in ([f'http://localhost:{my_port}/'] + peer_addresses)]
wait_all_peers_ready()
print("All peers ready. Waiting for sync...")
while (datetime.now().second % 10 != 0):
    pass
print("Start!")


for iteration in range(number_of_iterations):
    broadcast_event(random.choice(list_of_words))
    time.sleep(0.001)
