'''
    This file will only be executed ONCE when migrating
'''
from django.shortcuts import render, redirect
from django.contrib.auth.models import User
from django.contrib import messages
from django.core.mail import send_mail

from .models import Order, OrderProductTuple, Product, Warehouse, WarehouseStock, UserCartTuple
from . import order_status
from .utils import get_open_socket, send_request_on_socket as send_request, connect_db, execute_and_commit
from . import webapp_amazon_pb2 as amazon

import time

amazon_socket = None


# MARK: views 
def index(request):
    all_products = Product.objects.order_by('id')
    
    context = {
        'all_products': all_products,
    }
    return render(request, 'amazon_frontend/index.html', context)

def add_to_cart(request):
    if request.method == 'POST':
        ids = [str(product.id) for product in Product.objects.all()]

    elif request.method == 'GET':
        return redirect('index')

def buy(request):
    """ send buy request to amazon server """
    if request.method == 'POST':
        destination_x = request.POST['x']
        destination_y = request.POST['y']
        if 'email' in request.POST:
            email = request.POST['email']
        else:
            email = "yl506@duke.edu"
        if 'ups_account' in request.POST:
            ups_account = request.POST['ups_account']
        else:
            ups_account = ""
        order = Order(ups_account=ups_account, status=order_status.PURCHASING, destination_x=destination_x, destination_y=destination_y, price=10.00)

        order_saved = False
        ids = [str(product.id) for product in Product.objects.all()]
        for id in ids:
            product = Product.objects.get(pk=id)
            print("product id", id)
            num_product = int(request.POST[id]) 
            if num_product > 0:
                order.save() # Fields of order are accessible after calling .save()
                order.tracking_number = order.id
                order.save() # Save tracking number
                order_saved = True
                OrderProductTuple(order=order, product=product, num_product=num_product).save()

        if order_saved == True:
            # Send email confirmation
            send_mail(
                'Amazon Order Confirmation',
                f'Your order is being processed. Order ID is {order.id}. You can query status, change destination, and cancel this order. Thanks for choosing Amazon.',
                'DukeUpsOfficial@gmail.com',
                [email],
                fail_silently = False
            )
            # Send command to backend (amazon_server)
            command = amazon.WACommands()
            command.buy.order_id = order.id
            send_request(command, amazon_socket)
            # Send notification to frontend (web)
            messages.success(request, f'Order {order.id} successfully created! Tracking number: {order.tracking_number}')
            return redirect('index')
        else:
            messages.error(request, 'Please buy something')
            return redirect('index')
        
            
    elif request.method == 'GET':
        return redirect('index')    

def change_destination(request):
    """ send change destination request to amazon server """
    if request.method == 'POST':
        order_id = request.POST['order_id']
        new_destination_x = request.POST['x']
        new_destination_y = request.POST['y']

        order = None
        try:
            order = Order.objects.get(pk=order_id)
        except Order.DoesNotExist:
            order = None

        if order is not None:
            if order.status not in [order_status.CANCELED, order_status.DELIVERING, order_status.DELIVERED]:  # okay to change destination
                command = amazon.WACommands()
                command.change_destination.order_id = int(order_id)
                command.change_destination.new_destination_x = int(new_destination_x)
                command.change_destination.new_destination_y = int(new_destination_y)
                send_request(command, amazon_socket)

                messages.success(request, f'Order {order_id} shipping address is being updated.')
                return redirect('query')
            else: # cannot change destination due to status
                messages.error(request, f'Order is already {order.status} and the shipping address cannot be changed.')
                return render(request, 'amazon_frontend/change_destination.html')
        else: # Order not found
            messages.error(request, 'Order does not exist.')
            return render(request, 'amazon_frontend/change_destination.html')

    elif request.method == 'GET':
        return render(request, 'amazon_frontend/change_destination.html')

def cancel(request):
    if request.method == 'POST':
        order_id = request.POST['order_id']
        order = None
        try:
            order = Order.objects.get(pk=order_id)
        except Order.DoesNotExist:
            order = None

        if order is not None:
            if order.status == order_status.PURCHASING:
                order.status = order_status.CANCELED # NOTE: possibly concurrency issues w/ amazon server
                order.save()
                # send cancel request to amazon server
                command = amazon.WACommands()
                command.cancel.order_id = order.id
                send_request(command, amazon_socket)
                # send notification to frontend
                messages.success(request, f"Order {order.id} successfully canceled.")
                return render(request, 'amazon_frontend/cancel.html')
            elif order.status == order_status.CANCELED:
                messages.error(request, f"Order {order.id} has already been canceled.")
                return render(request, 'amazon_frontend/cancel.html')
            else:
                messages.error(request, f"Order {order.id} has already been processed and cannot be canceled.")
                return render(request, 'amazon_frontend/cancel.html')
        else:
            messages.error(request, 'Order does not exist')
            return render(request, 'amazon_frontend/cancel.html')


    elif request.method == 'GET':
        return render(request, 'amazon_frontend/cancel.html')
    
def query(request):
    if request.method == 'POST':
        order_id = request.POST['order_id']
        order = None
        try:
            order = Order.objects.get(pk=order_id)
        except Order.DoesNotExist:
            order = None
            
        if order is not None:
            context = {
                'order': order
            }
            return render(request, 'amazon_frontend/query.html', context)
        else:
            messages.error(request, 'Order does not exist')
            return render(request, 'amazon_frontend/query.html')

    elif request.method == 'GET':
        return render(request, 'amazon_frontend/query.html')