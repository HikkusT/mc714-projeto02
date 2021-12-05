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
    with lock:
        print("\nPeer", local_peer_index, "is starting an election.")
        for i in range(local_peer_index + 1, len(all_peers_list)):
            try:
                print("About to send receive election request")
                all_peers_list[i].receive_election_request()
                print("sent receive election request")
                return
            except Exception as e:
                print(e)
                print("Peer", i, "is down.")
        
        print()
        announce_as_leader()

def receive_election_request():
    try:
        return True
    finally:
        start_election()

def announce_as_leader():
    print("Annoucing me as the leader.")
    global leader_index
    leader_index = local_peer_index
    for i in range(len(all_peers_list)):
        if i != local_peer_index:
            try:
                print("About to send leader announcement request")
                
                all_peers_list[i].receive_leader_announcement(local_peer_index)
                print("Peer", i, "acknowledge your power.")
            except:
                print("Peer", i, "is not alive to acknowledge your leadership.")

def receive_leader_announcement(new_leader_index):
    global leader_index
    leader_index = new_leader_index
    print("\nPeer", leader_index, "is the new leader.")

def receive_status_request():
    return True

def print_all_peers_ordered_list():
    print("All peers ordered list from less to more powerfull:")
    for i in range(len(all_peers_address_list)):
        print(i, " -> ", all_peers_address_list[i])

external_address = urllib.request.urlopen('https://api.ipify.org').read().decode('utf8')
external_address = "http://" + external_address + ":8000/"
print(external_address)
print()
others_peers_address_list = sys.argv[1].split(',')

others_peers_address_list.append(external_address)
all_peers_address_list = sorted(others_peers_address_list)
local_peer_index = all_peers_address_list.index(external_address)

#Startin local server
local_server = SimpleXMLRPCServer(("", 8000), allow_none=True, logRequests=False)
local_server.register_function(receive_leader_announcement)
local_server.register_function(receive_election_request)
local_server.register_function(receive_status_request)

server_thread = threading.Thread(target=local_server.serve_forever)
server_thread.start()

# with xmlrpc.client.ServerProxy(hosts) as proxy:
all_peers_list = [xmlrpc.client.ServerProxy(address) for address in all_peers_address_list]

print("I'm peer number", local_peer_index, ".")
print_all_peers_ordered_list()
leader_index = len(all_peers_list) - 1

lock = threading.Lock()

time.sleep(5)

start_election()


while True:
    time.sleep(5)
    if (leader_index != local_peer_index):
        try:
            print("About to send status request.")
            with lock:
                all_peers_list[leader_index].receive_status_request()
            print("\nPeer", leader_index, "is ok.")
        except:
            print("\nPeer", leader_index, "found dead at the scene.\n")
            start_election()
    else:
        print("\nI'm the leader, everything is alright.")

