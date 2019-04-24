import webapp_amazon_pb2 as webapp
import amazon_ups_pb2 as ups
import world_amazon_pb2 as world 

from message_handlers import handle_world_message, handle_ups_message, handle_webapp_message
import order_status
from db_operations import connect_db, execute_and_commit
from pb_communication import recv_response_on_socket as recv_response
from pb_communication import send_request_on_socket as send_request
from pb_communication import get_open_socket

import time
import socket
import threading
from concurrent.futures import ThreadPoolExecutor

# Constants

WEBAPP_ADDRESS = ("0.0.0.0", 45678)
# NOTE: Change UPS's address here
# 2 UPS groups' vcm # within our IG: 7844, 8944
WORLD_ADDRESS = ("vcm-8944.vm.duke.edu", 23456)
UPS_ADDRESS = ("vcm-7996.vm.duke.edu", 8888)

def connect_webapp(address):
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sock.bind(address)
    # Listen for incoming connections and wait for a connection
    sock.listen(10)
    webapp_socket, _ = sock.accept()
    sock.close()

    return webapp_socket

def connect_world_command(world_id):
    conn, cursor = connect_db()

    query = f"""
        SELECT id, location_x, location_y
        FROM amazon_frontend_warehouse
    """
    cursor.execute(query)
    rows = cursor.fetchall()
    cursor.close()

    initWarehouses = []
    for row in rows:
        initWarehouse = world.AInitWarehouse()
        initWarehouse.id = row[0]
        initWarehouse.x = row[1]
        initWarehouse.y = row[2]
        initWarehouses.append(initWarehouse)

    command = world.AConnect()
    command.worldid = world_id
    command.isAmazon = True
    for initWarehouse in initWarehouses:
            command.initwh.add().CopyFrom(initWarehouse)

    return command

# --- SERVER STARTS ---
print("Amazon server starting......")

world_socket = get_open_socket(WORLD_ADDRESS)
ups_socket = get_open_socket(UPS_ADDRESS)
webapp_socket = connect_webapp(WEBAPP_ADDRESS)

message = recv_response(ups.UACommands, ups_socket) # Received world_id from UPS
assert(message.HasField('world_id')) # assume UPS created the world

command = connect_world_command(message.world_id) # Connect to world
send_request(command, world_socket)
response = recv_response(world.AConnected, world_socket)
assert(response.result == 'connected!')


thread1 = threading.Thread(target=handle_world_message, args=(world_socket, ups_socket))
thread2 = threading.Thread(target=handle_ups_message, args=(world_socket, ups_socket))
thread3 = threading.Thread(target=handle_webapp_message, args=(webapp_socket, world_socket, ups_socket))

threads = [thread1, thread2, thread3]

for t in threads:
    t.start()

while True:
    pass
