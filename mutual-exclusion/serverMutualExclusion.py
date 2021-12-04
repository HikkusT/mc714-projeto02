from xmlrpc.server import SimpleXMLRPCServer
import xmlrpc.client
import sys
import time
import threading
import random

common_variable = 0
set_count = 0

def get_common_variable():
    return common_variable

def set_common_variable(value):
    global set_count, common_variable
    set_count += 1 
    common_variable = value

server = SimpleXMLRPCServer(("", 8000), allow_none=True, logRequests=False) 
server.register_function(get_common_variable)
server.register_function(set_common_variable)
server_thread = threading.Thread(target=server.serve_forever)
server_thread.start()

time.sleep(20)
print("Valor esperado: ", set_count, "Valor real: ", common_variable)
