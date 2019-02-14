from django.shortcuts import render, get_object_or_404, redirect
from django.core.paginator import EmptyPage, PageNotAnInteger, Paginator
from django.utils.dateparse import parse_date, parse_time, parse_datetime
from django.contrib import messages
from django.core.mail import send_mail

from .models import Ride, Driver

# Create your views here.
def index(request):
    rides = Ride.objects.order_by('-arrival_time_owner').filter(is_completed=False)
    paginator = Paginator(rides, 9)
    page = request.GET.get('page')
    paged_rides = paginator.get_page(page)

    context = {
        'rides': paged_rides
    }
    return render(request, 'rides/rides.html', context)


def ride(request, ride_id):
    ride = get_object_or_404(Ride, pk=ride_id)
    context = {
        'ride': ride
    }
    return render(request, 'rides/ride.html', context)


def owner_request_ride(request):
    if request.method == 'POST':
        owner_first_name = request.POST['owner_first_name']
        owner_last_name = request.POST['owner_last_name']
        owner_email = request.POST['owner_email']
        owner_id = request.POST['owner_id']
        street_address = request.POST['address']
        city = request.POST['city']
        state = request.POST['state']
        passengers_owner = request.POST['passengers_owner']
        arrival_date = request.POST['arrival_date']
        arrival_time = request.POST['arrival_time']
        is_shareable = request.POST.get('is_shareable', '') == 'on'
        vehicle_type_requested = request.POST['vehicle_type_requested']
        special_requests_owner = request.POST.get('special_requests_owner', '')

        # Combine inputs for DB
        owner_name = owner_first_name + ' ' + owner_last_name
        destination_owner = street_address + ', ' + city + ', ' + state
        arrival_time_owner = parse_datetime(arrival_date + ' ' + arrival_time)

        open_ride = Ride(owner_name=owner_name, owner_email=owner_email, owner_id=owner_id, destination_owner=destination_owner, arrival_time_owner=arrival_time_owner, passengers_owner=passengers_owner, is_shareable=is_shareable, vehicle_type_requested=vehicle_type_requested, special_requests_owner=special_requests_owner)

        open_ride.save()
        messages.success(request, 'Successfully requested!')
        return redirect('dashboard')

    else:
        return render(request, 'rides/request.html')


def driver_search_ride(request):
    if request.method == 'GET':
        queryset_list = Ride.objects.order_by('-arrival_time_owner').filter(is_confirmed=False)
        driver = Driver.objects.get(username=request.user.username)
        queryset_list = [query for query in queryset_list if (query.passengers_owner + query.passengers_sharer <= driver.max_capacity)]
        queryset_list = [query for query in queryset_list if (query.vehicle_type_requested == '' or query.vehicle_type_requested != '' and query.vehicle_type_requested == driver.vehicle_type_registered)]
        queryset_list = [query for query in queryset_list if (query.special_requests_owner == '' or query.special_requests_owner != '' and query.special_requests_owner == driver.special_requests)]

        context = {
            'rides': queryset_list,
            'driver' : driver,
        }
        return render(request, 'rides/driver_search_ride.html', context)


def sharer_search_ride(request):
    if request.method == 'GET':
        queryset_list = Ride.objects.order_by('-arrival_time_owner').filter(is_confirmed=False)
        # Destination input
        if 'destination_sharer' in request.GET:
            destination_sharer = request.GET['destination_sharer']
            if destination_sharer:
                queryset_list = queryset_list.filter(destination_owner__icontains=destination_sharer)
        if 'city' in request.GET:
            city = request.GET['city']
            if city:
                queryset_list = queryset_list.filter(destination_owner__icontains=city)
        if 'state' in request.GET:
            state = request.GET['state']
            if state:
                queryset_list = queryset_list.filter(destination_owner__icontains=state)
        # Arrival time window
        if 'arrival_date' in request.GET:
            arrival_date = parse_date(request.GET['arrival_date'])
        if 'arrival_time' in request.GET:
            arrival_time = parse_time(request.GET['arrival_time'])
        queryset_list = queryset_list.filter(arrival_time_owner__date=arrival_date)
        queryset_list = queryset_list.filter(is_shareable=True)
        queryset_list = [query for query in queryset_list if (query.owner_id != request.GET['sharer_id'])]

        context = {
            'rides': queryset_list,
            'sharer_name': request.GET['sharer_first_name'] + ' ' + request.GET['sharer_last_name'],
            'sharer_id': request.GET['sharer_id'],
            'sharer_email': request.GET['sharer_email'],
            'destination_sharer': request.GET['destination_sharer'] + ', ' + request.GET['city'] + ', ' + request.GET['state'],
            'passengers_sharer': request.GET['passengers_sharer'],
            'arrival_time': request.GET['arrival_time'],
            'arrival_date': request.GET['arrival_date'],
        }
        return render(request, 'rides/sharer_search_ride.html', context)


def owner_edit_ride(request):
    if request.method == 'POST':
        street_address = request.POST['street_address_owner']
        city = request.POST['city']
        state = request.POST['state']
        passengers_owner = request.POST['passengers_owner']
        arrival_date = request.POST['arrival_date']
        arrival_time = request.POST['arrival_time']
        is_shareable = request.POST.get('is_shareable', '') == 'on'
        vehicle_type_requested = request.POST['vehicle_type_requested']
        special_requests_owner = request.POST.get('special_requests_owner', '')
        ride_id = request.POST['ride_id']

        destination_owner = street_address + ', ' + city + ', ' + state
        arrival_time_owner = parse_datetime(arrival_date + ' ' + arrival_time)

        ride = Ride.objects.get(id=ride_id)
        ride.destination_owner = destination_owner
        ride.passengers_owner = passengers_owner
        ride.arrival_time_owner = arrival_time_owner
        ride.is_shareable = is_shareable
        ride.vehicle_type_requested = vehicle_type_requested
        ride.special_requests_owner = special_requests_owner

        ride.save()
        messages.success(request, 'Request info successfully edited')
        return redirect('index')

def owner_cancel_ride(request):
    if request.method == 'POST':
        ride_id = request.POST['ride_id']
        ride = Ride.objects.get(id=ride_id)
        ride.delete()
        messages.success(request, 'Ride has been canceled!')
        return redirect('index')


def sharer_join_ride(request):
    if request.method == 'POST':
        sharer_name = request.POST['sharer_name']
        sharer_id = request.POST['sharer_id']
        sharer_email = request.POST['sharer_email']
        destination_sharer = request.POST['destination_sharer']
        passengers_sharer = request.POST['passengers_sharer']
        arrival_date = request.POST['arrival_date'] 
        arrival_time = request.POST['arrival_time']
        arrival_time_sharer = parse_datetime(arrival_date + ' ' + arrival_time)
        ride_id = request.POST['ride_id']

        ride = Ride.objects.get(id=ride_id)
        ride.sharer_name = sharer_name
        ride.sharer_id = sharer_id
        ride.sharer_email = sharer_email
        ride.destination_sharer = destination_sharer
        ride.passengers_sharer = passengers_sharer
        ride.arrival_time_sharer = arrival_time_sharer
        ride.is_shareable = False # for now, only allows 1 sharer group

        ride.save()
        messages.success(request, 'Successfully joined ride!')
        return redirect('dashboard')

def sharer_edit_ride(request):
    if request.method == 'POST':
        street_address = request.POST['street_address_sharer']
        city = request.POST['city']
        state = request.POST['state']
        passengers_sharer = request.POST['passengers_sharer']
        arrival_date = request.POST['arrival_date']
        arrival_time = request.POST['arrival_time']
        ride_id = request.POST['ride_id']

        destination_sharer = street_address + ', ' + city + ', ' + state
        arrival_time_sharer = parse_datetime(arrival_date + ' ' + arrival_time)

        ride = Ride.objects.get(id=ride_id)
        ride.destination_sharer = destination_sharer
        ride.passengers_sharer = passengers_sharer
        ride.arrival_time_sharer = arrival_time_sharer

        ride.save()
        messages.success(request, 'Request info successfully edited')
        return redirect('index')

def sharer_cancel_ride(request):
    if request.method == 'POST':
        ride_id = request.POST['ride_id']
        ride = Ride.objects.get(id=ride_id)
        ride.sharer_id = 0
        ride.sharer_name = ''
        ride.sharer_email = ''
        ride.destination_sharer = ''
        import datetime
        ride.arrival_time_sharer = datetime.datetime.now()
        ride.passengers_sharer = 0
        ride.is_shareable = True
        ride.save()
        messages.success(request, 'You have left the ride!')
        return redirect('index')

def driver_confirm_ride(request):
    if request.method == 'POST':
        driver_name = request.POST['driver_name']
        driver_id = request.POST['driver_id']
        driver_email = request.POST['driver_email']
        vehicle_type_registered = request.POST['vehicle_type_registered']
        license_plate_number = request.POST['license_plate_number']
        special_requests_driver = request.POST['special_requests']
        max_capacity = request.POST['max_capacity']
        ride_id = request.POST['ride_id']

        ride = Ride.objects.get(id=ride_id)
        ride.driver_name = driver_name
        ride.driver_email = driver_email
        ride.driver_id = driver_id
        ride.vehicle_type_registered = vehicle_type_registered
        ride.license_plate_number = license_plate_number
        ride.special_requests_driver = special_requests_driver
        ride.max_capacity = max_capacity
        ride.is_confirmed = True

        owner_email = ride.owner_email
        sharer_email = ride.sharer_email

        ride.save()

        # Send mail
        # send_mail(
        #         'ECE 568 Ride Sharing Web - Lyber by Yifan Li (yl506)',
        #         'Your ride request has been confirmed by ' + driver_name + '. You can contact your driver at ' + driver_email + '.',
        #         'lyf901901@gmail.com',
        #         [owner_email, sharer_email, 'yl506@duke.edu'],
        #         fail_silently=False
        # )
        messages.success(request, 'Successfully confirmed ride!')
        return redirect('dashboard')

def driver_complete_ride(request):
    if request.method == 'POST':
        ride_id = request.POST['ride_id']
        completed_ride = Ride.objects.get(id=ride_id)
        completed_ride.is_completed = True
        completed_ride.save()
        messages.success(request, 'Successfully completed ride!')
        return redirect('dashboard')
    