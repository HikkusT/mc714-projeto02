from xmlrpc.server import SimpleXMLRPCServer
import xmlrpc.client
import sys
import time
import threading
import random

id = sys.argv[1]
current_time = 0
events = []

def log_event(time, id):
    events.append((time, id))

def receive_event(time, id):
    global current_time
    current_time = max(time, current_time) + 1

    log_event(time, id)
    print("Received from " + str(id) + " with timestamp " + str(time))

def send_event(hosts):
    global current_time, id
    current_time += 1

    log_event(current_time, id)
    print("Broadcasting at " + str(current_time))

    for host in hosts:
        host.receive_event(current_time, id)
    

server = SimpleXMLRPCServer(("", int(sys.argv[3])), allow_none=True, logRequests=False) 
server.register_function(receive_event)
server_thread = threading.Thread(target=server.serve_forever)
server_thread.start()

hostsAddresses = sys.argv[2].split(',')
hosts = []
print("Starting client...")
# with xmlrpc.client.ServerProxy(hosts) as proxy:
for hostAddress in hostsAddresses:
    hosts.append(xmlrpc.client.ServerProxy(hostAddress))

for i in range(4):
    time_to_sleep = random.randint(5, 15)
    print("Sleeping for " + str(time_to_sleep))
    time.sleep(time_to_sleep)

    send_event(hosts)

time.sleep(15)
print("Order: ")
events.sort(key= lambda event: event[0])
for event in events:
    print(event)
