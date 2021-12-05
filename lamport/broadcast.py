from collections import defaultdict
from typing import NamedTuple
from xmlrpc.server import SimpleXMLRPCServer
import xmlrpc.client
import sys
import time
import threading
from datetime import datetime
import queue

class Event(NamedTuple):
    id: int
    timestamp: int

    def __str__(self):
        return f'Event on timestamp {self.timestamp} from {self.id}'

    def __lt__(self, other):
        if self.timestamp != other.timestamp:
            return self.timestamp < other.timestamp
        else:
            return self.id < other.id

my_id = int(sys.argv[1])
peer_addresses = sys.argv[2].split(',')
number_of_peers = len(peer_addresses)
my_port = int(sys.argv[3]) if len(sys.argv) > 3 else 8000

# Constants
number_of_iterations = 5
logs_to_show = []

# Local state
lock = threading.Lock()
current_time = 0
event_queue = []
event_acks = defaultdict(int)
acks_to_broadcast = queue.Queue()

def process_event(event):
    print(f'Processing {event}')

def consume_event_queue():
    event_queue.sort()
    for event in event_queue.copy():
        if event_acks[event] == len(peers):
            process_event(event)
            event_queue.remove(event)
        else:
            break

# Listeners
def receive_event(id, timestamp):
    global current_time
    current_time = max(timestamp, current_time) + 1

    event = Event(id, timestamp)
    if 'receive' in logs_to_show:
        print(f'[Receive] Received {event}')
    event_queue.append(event)
    acks_to_broadcast.put(event)

def receive_ack(sender_id, id_of_event, timestamp_of_event):
    event = Event(id_of_event, timestamp_of_event)
    if 'ack' in logs_to_show:
        print(f'[Ack] Received ack from {sender_id} about {event}')

    event_acks[event] += 1
    consume_event_queue()

def health_check():
    return True

# Senders
def broadcast_event():
    global current_time
    current_time += 1

    event = Event(my_id, current_time)
    if 'send' in logs_to_show:
        print(f'[Send] Broadcasting {event}')
    for peer in peers:
        with lock:
            peer.receive_event(event.id, event.timestamp)

def broadcast_ack(event):
    for peer in peers:
        with lock:
            peer.receive_ack(my_id, event.id, event.timestamp)

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
server.register_function(receive_ack)
server.register_function(health_check)
server_thread = threading.Thread(target=server.serve_forever)
server_thread.start()

# Background stuff so we can broadcast acks
def ack_sender():
    while True:
        if not acks_to_broadcast.empty():
            event = acks_to_broadcast.get()
            broadcast_ack(event)

ack_thread = threading.Thread(target = ack_sender)
ack_thread.start()

# Client stuff
peers = [xmlrpc.client.ServerProxy(peer_address) for peer_address in ([f'http://localhost:{my_port}/'] + peer_addresses)]
wait_all_peers_ready()
print("All peers ready. Waiting for sync...")
while (datetime.now().second % 10 != 0):
    pass
print("Start!")


for iteration in range(number_of_iterations):
    broadcast_event()
    time.sleep(0.001)
