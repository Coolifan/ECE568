import world_amazon_pb2 as world
import amazon_ups_pb2 as ups
import webapp_amazon_pb2 as webapp

import psycopg2
import time
import datetime
import random
import threading
from concurrent.futures import ThreadPoolExecutor

from db_operations import connect_db, execute_and_commit
import order_status
from pb_communication import recv_response_on_socket as recv_response, send_request_on_socket as send_request, get_open_socket

# *** Constants ***
RESEND_INTERVAL = 1 # period used to check ACK when sending requests to world


# *** Global locks and objects ***

UPS_WRITER_MUTEX = threading.Lock()  # Locks used when sending messages
WORLD_WRITER_MUTEX = threading.Lock()

WAITING_ACKS_FROM_WORLD = set() # ACK, request resending related
ACKS_FROM_WORLD_MUTEX = threading.Lock()

SEQNUM = 1 # seqnum generator
SEQNUM_GENERATOR_MUTEX = threading.Lock()


# *** Auxillary functions ***

def generate_seqnum_and_add_to_waiting_ack_set():
    ''' Generate a unique seqnum, AND add seqnum to WAITING_ACKS_FROM_WORLD 
        Thread-safe. 2 locks: SEQNUM_GENERATOR_MUTEX, ACKS_FROM_WORLD_MUTEX

        NOTE: Deadlock will happen if SEQNUM_GENERATOR_MUTEX and SEQNUM are not global.
              Possible explanations: within SEQNUM_GENERATOR_MUTEX, an internal lock generated
              by Python is acquired, and the program tries to visit SEQNUM and acquire the same
              internal lock simultaneously, which leads to deadlock.

              Whenever you want to modify a global variable, that var must be declared as a global var
    '''
    global SEQNUM_GENERATOR_MUTEX, SEQNUM, ACKS_FROM_WORLD_MUTEX, WAITING_ACKS_FROM_WORLD
    seqnum = None

    with SEQNUM_GENERATOR_MUTEX:
        seqnum = SEQNUM
        SEQNUM += 1
        
    with ACKS_FROM_WORLD_MUTEX:
        WAITING_ACKS_FROM_WORLD.add(seqnum)

    return seqnum

def resend_to_world_until_ack_received(command, seqnum, world_socket):
    ''' Send command to the world until ACK is received 
        Thread-safe, 2 locks: ACKS_FROM_WORLD_MUTEX and WORLD_WRITER_MUTEX
        Will block until ACK received, must be placed at the end of a handler function
    '''

    while True:
        waiting = None
        global ACKS_FROM_WORLD_MUTEX, WORLD_WRITER_MUTEX, WAITING_ACKS_FROM_WORLD

        with ACKS_FROM_WORLD_MUTEX:
            waiting = seqnum in WAITING_ACKS_FROM_WORLD # Get ack status

        if waiting: # Still waiting for ack from world
            with WORLD_WRITER_MUTEX:
                send_request(command, world_socket)
            time.sleep(RESEND_INTERVAL)
        else: # Received ack from world
            break 
        
def update_order_status(order_id, new_status):
    conn, cursor = connect_db()
    query = f"""
        UPDATE amazon_frontend_order
        SET status='{new_status}'
        WHERE id={order_id}
    """
    execute_and_commit(query, conn, cursor)
    cursor.close()

def send_to_ups_with_lock(command, ups_socket):
    ''' Send command to UPS
        Thread-safe, used UPS_WRITER_MUTEX
    '''

    global UPS_WRITER_MUTEX
    with UPS_WRITER_MUTEX:
        send_request(command, ups_socket)

def reply_ack_to_world_with_lock(response_from_world, world_socket):
    ''' Send ack to world once, thread-safe ''' 
    
    command = world.ACommands()
    command.acks.append(response_from_world.seqnum)

    global WORLD_WRITER_MUTEX
    with WORLD_WRITER_MUTEX:
        send_request(command, world_socket)
    
def connect_world(initWarehouses):
    world_socket = None
    world_id = None

    # // AMAZON CONNECT
    while True:
        world_socket = get_open_socket(WORLD_ADDRESS)
        createWorld = world.AConnect()
        createWorld.isAmazon = True
        send_request(createWorld, world_socket)
        res = recv_response(world.AConnected, world_socket)
        world_id = res.worldid
        world_socket.close()

        world_socket = get_open_socket(WORLD_ADDRESS)
        connectWorld = createWorld
        connectWorld.worldid = world_id
        for initWarehouse in initWarehouses:
            connectWorld.initwh.add().CopyFrom(initWarehouse)
        
        send_request(connectWorld, world_socket) # connect with init_warehouses
        res = recv_response(world.AConnected, world_socket)
        if res.result == 'connected!':
            break

    return world_socket, world_id

def check_canceled(order_id):
    conn, cursor = connect_db()
    query = f"""
        SELECT status 
        FROM amazon_frontend_order
        WHERE id={order_id}
    """
    cursor.execute(query)
    status = cursor.fetchone()[0]
    cursor.close()

    return status == order_status.CANCELED

def check_warehouse_inventory(order_id, warehouse_id):
    try:
        conn, cursor = connect_db()
        query = f"""    
            SELECT product_id, num_product
            FROM amazon_frontend_orderproducttuple
            WHERE order_id={order_id}
        """
        cursor.execute(query)

        rows = cursor.fetchall()
        for row in rows:
            product_id, num_product = row

            query = f"""
                SELECT num_product
                FROM amazon_frontend_warehousestock
                WHERE warehouse_id={warehouse_id} AND product_id={product_id}
            """
            cursor.execute(query)
            num_in_stock = cursor.fetchone()[0]
            if num_in_stock < num_product:
                return False

        cursor.close()
        return True

    except (Exception, psycopg2.DatabaseError) as error:
        print(error) 

def get_current_time():
    ''' Get current time in string up to microseconds '''
    ts = time.time()
    timestamp = datetime.datetime.fromtimestamp(ts).strftime('%Y-%m-%d %H:%M:%S.%f')

    return timestamp


# *** World commands handler ***

def handle_world_message(world_socket, ups_socket):
    """ listen to responses from world and generate tasks """

    num_threads = 100
    pool = ThreadPoolExecutor(num_threads)

    while (1):
        global ACKS_FROM_WORLD_MUTEX, WAITING_ACKS_FROM_WORLD
        response = recv_response(world.AResponses, world_socket)

        for err in response.error: # Error msg from world
            print("Error from world, origin seqnum:", err.originseqnum)
            print("Error message: ", err.err)

        for ack in response.acks:
            print("Received ACK:", ack)
            with ACKS_FROM_WORLD_MUTEX:
                WAITING_ACKS_FROM_WORLD.discard(ack)

        for purchased in response.arrived:
            print("purchased received")
            pool.submit(handle_purchased, world_socket, ups_socket, purchased)

        for packed in response.ready:
            print("packed received")
            if check_canceled(packed.shipid) == False:
                pool.submit(handle_packed, world_socket, packed)

        for loaded in response.loaded:
            if check_canceled(loaded.shipid) == False:
                pool.submit(handle_loaded, world_socket, ups_socket, loaded)

        if response.finished == True:
            print("CONNECTION CLOSED, EXITING...")
            world_socket.close()
            ups_socket.close()
            break

def handle_purchased(world_socket, ups_socket, purchased):
    print("Entered handle_purchased()")

    # Reply ACK to world
    reply_ack_to_world_with_lock(purchased, world_socket)

    try:
        conn, cursor = connect_db()
        query = ""
        for thing in purchased.things:
            query += f"""
                UPDATE amazon_frontend_warehousestock
                SET num_product=num_product+{thing.count}
                WHERE warehouse_id={purchased.whnum} AND product_id={thing.id};
            """
        execute_and_commit(query, conn, cursor)

        query = f"""
            SELECT id 
            FROM amazon_frontend_order
            WHERE status='{order_status.PURCHASING}'
        """
        cursor.execute(query)
        orders = cursor.fetchall()

        for order in orders:
            order_id = order[0]
            if check_warehouse_inventory(order_id, purchased.whnum) == True:
                start_packing(world_socket, order_id)
                start_getting_truck(ups_socket, order_id)

        cursor.close()

    except (Exception, psycopg2.DatabaseError) as error:
        print(error)

def start_getting_truck(ups_socket, order_id):
    ''' Start requesting a truck for order: orderid '''
    print("Entered start_getting_truck()")
    Ucommand = ups.AUCommands()
    get_truck = Ucommand.get_truck
    try:
        conn, cursor = connect_db()
        query = f"""
                SELECT ups_account, warehouse_id, location_x, location_y, destination_x, destination_y
                FROM amazon_frontend_order, amazon_frontend_warehouse
                WHERE amazon_frontend_order.warehouse_id=amazon_frontend_warehouse.id AND amazon_frontend_order.id={order_id}
            """
        cursor.execute(query)
        row = cursor.fetchone()
        
        get_truck.order_id = order_id
        get_truck.ups_account = row[0]
        get_truck.warehouse_id = row[1]
        get_truck.location_x = row[2]
        get_truck.location_y = row[3]
        get_truck.destination_x = row[4]
        get_truck.destination_y = row[5]

        cursor.close()

    except (Exception, psycopg2.DatabaseError) as error:
        print(error) 

    send_to_ups_with_lock(Ucommand, ups_socket)
    print("Exited start_getting_truck()")

def start_packing(world_socket, order_id):
    print("Entered start_packing()")
    command = world.ACommands()
    pack = command.topack.add()
    seqnum = generate_seqnum_and_add_to_waiting_ack_set() 
    pack.seqnum = seqnum

    try:
        conn, cursor = connect_db()

        query = f"""    
            SELECT product_id, description, num_product
            FROM amazon_frontend_orderproducttuple, amazon_frontend_product
            WHERE amazon_frontend_orderproducttuple.product_id=amazon_frontend_product.id AND amazon_frontend_orderproducttuple.order_id={order_id}
        """
        cursor.execute(query)
        rows = cursor.fetchall()
        for row in rows:
            thing = pack.things.add()
            thing.id = row[0]
            thing.description = row[1]
            thing.count = row[2]

        query = f"""
            SELECT warehouse_id
            FROM amazon_frontend_order
            WHERE id={order_id}
        """
        cursor.execute(query)
        pack.whnum = cursor.fetchone()[0]
        pack.shipid = order_id

        # Update warehouse stock
        query = ""
        for thing in pack.things:
            query += f"""
                UPDATE amazon_frontend_warehousestock
                SET num_product=num_product-{thing.count}
                WHERE warehouse_id={pack.whnum} AND product_id={thing.id};
            """
        execute_and_commit(query, conn, cursor)
        cursor.close()
    
    except (Exception, psycopg2.DatabaseError) as error:
        print(error)

    update_order_status(order_id, order_status.PACKING)    
    resend_to_world_until_ack_received(command, seqnum, world_socket)

def handle_packed(world_socket, packed):
    print("Entered handle_packed()")

    # Reply ACK to world
    reply_ack_to_world_with_lock(packed, world_socket)

    try:
        conn, cursor = connect_db()
        query = f"""
            UPDATE amazon_frontend_order
            SET status='{order_status.PACKED}', time_packed='{get_current_time()}'
            WHERE id={packed.shipid}
        """
        execute_and_commit(query, conn, cursor)

        query = f"""
            SELECT truck_id
            FROM amazon_frontend_order
            WHERE id={packed.shipid}
        """
        cursor.execute(query)
        truck_id = cursor.fetchone()[0]
        if truck_id is not None:
            start_loading(world_socket, packed.shipid, truck_id)
        
        cursor.close()
    except (Exception, psycopg2.DatabaseError) as error:
        print(error)

    print("Exited handle_packed()")

def start_loading(world_socket, order_id, truck_id):
    print("Entered start_loading()")
    command = world.ACommands()
    load = command.load.add()
    seqnum = generate_seqnum_and_add_to_waiting_ack_set()

    load.seqnum = seqnum

    try:
        conn, cursor = connect_db()    
        query = f"""
            SELECT warehouse_id
            FROM amazon_frontend_order
            WHERE id={order_id}
        """
        cursor.execute(query)
        
        load.whnum = cursor.fetchone()[0]
        load.truckid = truck_id
        load.shipid = order_id
        
        cursor.close()
    
    except (Exception, psycopg2.DatabaseError) as error:
        print(error)
    
    update_order_status(order_id, order_status.LOADING)
    resend_to_world_until_ack_received(command, seqnum, world_socket)
    
    print("Exited start_loading()")

def handle_loaded(world_socket, ups_socket, loaded):
    print("Entered handle_loaded()")

    # Reply ACK to world
    reply_ack_to_world_with_lock(loaded, world_socket)
    
    try:
        conn, cursor = connect_db()
        query = f"""
            UPDATE amazon_frontend_order
            SET status='{order_status.LOADED}', time_loaded='{get_current_time()}'
            WHERE id={loaded.shipid}
        """
        execute_and_commit(query, conn, cursor)

        start_delivering(ups_socket, loaded.shipid)
        
    except (Exception, psycopg2.DatabaseError) as error:
        print(error)

    print("Exited handle_loaded()")

def start_delivering(ups_socket, order_id):
    print("Entered start_delivering()")
    try:
        conn, cursor = connect_db()

        query = f"""
            UPDATE amazon_frontend_order
            SET status='{order_status.DELIVERING}'
            WHERE id={order_id}
        """
        execute_and_commit(query, conn, cursor)
        cursor.close()

    except (Exception, psycopg2.DatabaseError) as error:
        print(error)
    
    deliver = ups.request_init_delivery()
    deliver.package_id = order_id
    command = ups.AUCommands()
    command.init_delivery.CopyFrom(deliver)

    send_to_ups_with_lock(command, ups_socket)
    print("Exiting start_delivering")


# *** UPS commands handler ***

def handle_ups_message(world_socket, ups_socket):
    """ listen to responses from UPS and generate tasks """

    num_threads = 100
    pool = ThreadPoolExecutor(num_threads)

    while (1):
        response = recv_response(ups.UACommands, ups_socket)
        
        if response.HasField('truck_arrived'):
            if check_canceled(response.truck_arrived.package_id) == False:
                pool.submit(handle_truck_arrived, world_socket, response.truck_arrived)

        if response.HasField('package_delivered'):
            pool.submit(handle_delivered, response.package_delivered)
        
        if response.HasField('destination_changed'):
            pool.submit(handle_destination_changed, response.destination_changed)

        if response.disconnect == True:
            print("CONNECTION CLOSED, EXITING...")
            world_socket.close()
            ups_socket.close()
            break

def handle_truck_arrived(world_socket, truck_arrived):
    print("Entered handle_truck_arrived()")
    try:
        conn, cursor = connect_db()
        query = f"""
            UPDATE amazon_frontend_order
            SET truck_id={truck_arrived.truck_id}
            WHERE id={truck_arrived.package_id}
        """
        execute_and_commit(query, conn, cursor)

        query = f"""
            SELECT status 
            FROM amazon_frontend_order
            WHERE id={truck_arrived.package_id}
        """
        cursor.execute(query)
        row = cursor.fetchone()
        if row[0] == order_status.PACKED:
            start_loading(world_socket, truck_arrived.package_id, truck_arrived.truck_id)
        
        cursor.close()

    except (Exception, psycopg2.DatabaseError) as error:
        print(error)

def handle_delivered(delivered):
    print("Entered handle_delivered()")
    try:
        conn, cursor = connect_db()
        query = f"""
            UPDATE amazon_frontend_order
            SET status='{order_status.DELIVERED}', time_delivered='{get_current_time()}'
            WHERE id={delivered.package_id}
        """ 
        execute_and_commit(query, conn, cursor)

        cursor.close()

    except (Exception, psycopg2.DatabaseError) as error:
        print(error)

def handle_destination_changed(destination_changed): 
    print("Entered handle_destination_changed()") 
    try:
        conn, cursor = connect_db()
        query = f"""
            UPDATE amazon_frontend_order
            SET destination_x={destination_changed.new_destination_x}, destination_y={destination_changed.new_destination_y}
            WHERE id={destination_changed.package_id}
        """ 
        execute_and_commit(query, conn, cursor)

        cursor.close()
        
    except (Exception, psycopg2.DatabaseError) as error:
        print(error)  


# *** Webapp commands handler ***

def handle_webapp_message(webapp_socket, world_socket, ups_socket):
    """ listen to messages from web app and generate tasks """

    num_threads = 100
    pool = ThreadPoolExecutor(max_workers=num_threads)

    while (1):
        response = recv_response(webapp.WACommands, webapp_socket)
        
        if response.HasField('buy'):
            if check_canceled(response.buy.order_id) == False:
                pool.submit(handle_buy, world_socket, ups_socket, response.buy)
        
        if response.HasField('change_destination'):
            if check_canceled(response.change_destination.order_id) == False:
                pool.submit(handle_change_destination, ups_socket, response.change_destination)

        if response.HasField('cancel'):
            pool.submit(handle_cancel)

def handle_buy(world_socket, ups_socket, buy):
    print("Entered handle_buy()")
    Acommand = world.ACommands()
    purchase = Acommand.buy.add()
    seqnum = generate_seqnum_and_add_to_waiting_ack_set()
    purchase.seqnum = seqnum 

    # Ucommand = ups.AUCommands()
    # get_truck = Ucommand.get_truck
    
    try:
        conn, cursor = connect_db()

        # Acommand
        # retrieve things in an order, be careful with the columns queried
        query = f"""    
            SELECT product_id, description, num_product
            FROM amazon_frontend_orderproducttuple, amazon_frontend_product
            WHERE amazon_frontend_orderproducttuple.product_id=amazon_frontend_product.id AND amazon_frontend_orderproducttuple.order_id={buy.order_id}
        """
        cursor.execute(query)
        rows = cursor.fetchall()
        for row in rows:
            thing = purchase.things.add()
            thing.id = row[0]
            thing.description = row[1]
            thing.count = row[2]
        
        query = f"""
            SELECT COUNT(*), MIN(id)
            FROM amazon_frontend_warehouse;
        """
        cursor.execute(query)
        num_warehouse, min_warehouse_id = cursor.fetchone()
        purchase.whnum = buy.order_id % int(num_warehouse) + int(min_warehouse_id)
        
        query = f"""
            UPDATE amazon_frontend_order
            SET warehouse_id={purchase.whnum}
            WHERE id={buy.order_id}
        """
        execute_and_commit(query, conn, cursor)


        # # Ucommand
        # query = f"""
        #     SELECT ups_account, warehouse_id, location_x, location_y, destination_x, destination_y
        #     FROM amazon_frontend_order, amazon_frontend_warehouse
        #     WHERE amazon_frontend_order.warehouse_id=amazon_frontend_warehouse.id AND amazon_frontend_order.id={buy.order_id}
        # """
        # cursor.execute(query)
        # row = cursor.fetchone()
        
        # get_truck.order_id = buy.order_id
        # get_truck.ups_account = row[0]
        # get_truck.warehouse_id = row[1]
        # get_truck.location_x = row[2]
        # get_truck.location_y = row[3]
        # get_truck.destination_x = row[4]
        # get_truck.destination_y = row[5]

        cursor.close()

    except (Exception, psycopg2.DatabaseError) as error:
        print(error) 
    
    # send_to_ups_with_lock(Ucommand, ups_socket)
    resend_to_world_until_ack_received(Acommand, seqnum, world_socket)
       
def handle_change_destination(ups_socket, change_destination):
    print("Entered handle_change_destination()")
    command = ups.AUCommands()
    command.change_destination.package_id = change_destination.order_id
    command.change_destination.new_destination_x = change_destination.new_destination_x
    command.change_destination.new_destination_y = change_destination.new_destination_y

    send_to_ups_with_lock(command, ups_socket)

def handle_cancel(cancel):
    print("Entered handle_cancel()")
    try:
        conn, cursor = connect_db()

        query = f"""
            SELECT status 
            FROM amazon_frontend_order
            WHERE id={cancel.order_id}
        """
        cursor.execute(query)
        status = cursor.fetchone()[0]
        if status == order_status.PURCHASING: 
            query = f"""
                UPDATE amazon_frontend_order
                SET status='{order_status.CANCELED}'
                WHERE id={cancel.order_id}
            """
            execute_and_commit(query, conn, cursor)
        
        cursor.close()

    except (Exception, psycopg2.DatabaseError) as error:
        print(error) 
