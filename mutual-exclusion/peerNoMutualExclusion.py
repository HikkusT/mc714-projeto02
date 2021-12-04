from xmlrpc import server
from xmlrpc.server import SimpleXMLRPCServer
import xmlrpc.client
import sys
import threading
import urllib.request


# Program parameters
# 0 -> program name
# 1 -> server adress
# 2 -> next peer adress

server_address = sys.argv[1]
next_peer_address = sys.argv[2]
external_address = urllib.request.urlopen('https://api.ipify.org').read().decode('utf8')
external_address = "http://" + external_address + ":8000/"

hasKey = True if (external_address > next_peer_address) else False
print(hasKey)

def receive_key():
    global hasKey
    hasKey = True

def pass_key():
    global hasKey
    if (hasKey):
        hasKey = False
        next_peer.receive_key()

def sum_1_variable():
    common_variable = server.get_common_variable()
    server.set_common_variable(common_variable + 1)

local_server = SimpleXMLRPCServer(("", 8000), allow_none=True, logRequests=False)
local_server.register_function(receive_key)
server_thread = threading.Thread(target=local_server.serve_forever)
server_thread.start()

print("Starting client...")
# with xmlrpc.client.ServerProxy(hosts) as proxy:
next_peer = xmlrpc.client.ServerProxy(next_peer_address)
server =  xmlrpc.client.ServerProxy(server_address)

i = 0

while i < 500:
    sum_1_variable()
    i += 1

# while i < 500:
#     if (hasKey):
#         sum_1_variable()
#         i+= 1
#         pass_key()