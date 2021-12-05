from xmlrpc import server
from xmlrpc.server import SimpleXMLRPCServer
import xmlrpc.client
import sys
import threading
import urllib.request
import time
# Program parameters
# 0 -> program name
# 1 -> peer adress list

def start_election():
    print("Peer ", local_peer_index, " is starting an election.")
    anyone_more_powerfull_answered = False
    for i in range(local_peer_index, len(all_peers_list)):
        try:
            anyone_more_powerfull_answered = all_peers_list[i].receive_election_request()
            return
        #Tried to communicate with a down peer.
        except:
            print("Peer ", i, "is down.")
    
    announce_as_coordinator()

def receive_election_request():
    try:
        return True
    finally:
        start_election()

def announce_as_coordinator():
    for peer in all_peers_list:
        peer.receive_coordinator_announcement(local_peer_index)

def receive_coordinator_announcement(coordinator_index):
    global coordinator
    coordinator = all_peers_list[coordinator_index]
    print("Peer ", coordinator_index, " is the new coordinator.")

def receive_status_request():
    return True

def print_all_peers_ordered_list():
    print("All peers ordered list from less to more powerfull:")
    for i in range(len(all_peers_address_list)):
        print(i, " -> ", all_peers_address_list[i])


local_server = SimpleXMLRPCServer(("", 8000), allow_none=True, logRequests=False)
local_server.register_function(receive_coordinator_announcement)
local_server.register_function(receive_election_request)

server_thread = threading.Thread(target=local_server.serve_forever)
server_thread.start()

# with xmlrpc.client.ServerProxy(hosts) as proxy:
external_address = urllib.request.urlopen('https://api.ipify.org').read().decode('utf8')
external_address = "http://" + external_address + ":8000/"

others_peers_address_list = sys.argv[1].split(',')
others_peers_address_list.append(external_address)
all_peers_address_list = others_peers_address_list.sorted()

local_peer_index = all_peers_address_list.index(external_address)

all_peers_list = [xmlrpc.client.ServerProxy(address) for address in all_peers_address_list]


print("I'm peer number ", local_peer_index, ".")
print_all_peers_ordered_list()
coordinator_index = len(all_peers_list) - 1

time.sleep(5)

start_election()

time.sleep(5)

try: 
    all_peers_list[coordinator_index].receive_status_request()
    print("Peer ", coordinator_index, "is ok.")
except:
    print("Peer ", coordinator_index, "found dead at the scene.")
    start_election()