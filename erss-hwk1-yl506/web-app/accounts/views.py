from django.shortcuts import render, redirect
from django.contrib import messages, auth
from django.contrib.auth.models import User

from owners.models import Owner
from sharers.models import Sharer
from rides.models import Ride
from drivers.models import Driver

# Create your views here.
def register(request):
    if request.method == 'POST':
        # Get form values
        first_name = request.POST['first_name']
        last_name = request.POST['last_name']
        username = request.POST['username']
        email = request.POST['email']
        password = request.POST['password']
        password2 = request.POST['password2']
        name = first_name + ' ' + last_name

        # Check if passwords match
        if password == password2:
            # Check username
            if User.objects.filter(username=username).exists():
                messages.error(request, 'A user with this username already exists.')
                return redirect('register')
            else:
                if User.objects.filter(email=email).exists():
                    messages.error(request, 'A user with this email address already exists.')
                    return redirect('register')
                else: 
                    # Looks good 
                    user = User.objects.create_user(username=username, email=email, password=password, first_name=first_name, last_name=last_name)
                    user.save()
                    
                    owner = Owner(name=name, email=email, username=username)
                    owner.save()
                    sharer = Sharer(name=name, email=email, username=username)
                    sharer.save()

                    messages.success(request, 'Registration successful!')
                    return redirect('login')

        else:
            messages.error(request, 'Passwords do not match')
            return redirect('register')

    else:
        return render(request, 'accounts/register.html')

def login(request):
    if request.method == 'POST':
        username = request.POST['username']
        password = request.POST['password']
        user = auth.authenticate(username=username, password=password)

        if user is not None:
            auth.login(request, user)
            messages.success(request, 'Login successful!')
            return redirect('dashboard')
        else:
            messages.error(request, 'Invalid credentials')
            return redirect('login')
    else:
        return render(request, 'accounts/login.html')

def logout(request):
    if request.method == 'POST':
        auth.logout(request)
        messages.success(request, 'Logout successful!')
        return redirect('index')

def dashboard(request):
    open_rides = Ride.objects.order_by('-arrival_time_owner').filter(is_confirmed=False)
    confirmed_rides = Ride.objects.order_by('-arrival_time_owner').filter(is_confirmed=True, is_completed=False)
    completed_rides = Ride.objects.order_by('-arrival_time_owner').filter(is_completed=True)
    
    open_rides = [q for q in open_rides if (q.owner_id == request.user.id or q.sharer_id == request.user.id or q.driver_id == request.user.id)]
    confirmed_rides = [q for q in confirmed_rides if (q.owner_id == request.user.id or q.sharer_id == request.user.id or q.driver_id == request.user.id)]
    completed_rides = [q for q in completed_rides if (q.owner_id == request.user.id or q.sharer_id == request.user.id or q.driver_id == request.user.id)]

    from django.core.exceptions import ObjectDoesNotExist
    is_driver = True
    try:
        driver = Driver.objects.get(username=request.user.username)
    except ObjectDoesNotExist:
        is_driver = False

    context = {
        'open_rides': open_rides,
        'confirmed_rides': confirmed_rides,
        'completed_rides': completed_rides,
        'is_driver': is_driver
    }
    return render(request, 'accounts/dashboard.html', context)

def driver_register(request):
    if request.method == 'POST':
        name = request.POST['driver_name']
        email = request.POST['driver_email']
        username = request.POST['driver_username']
        driver_id = request.POST['driver_id']
        vehicle_type_registered = request.POST['vehicle_type_registered']
        license_plate_number = request.POST['license_plate_number']
        max_capacity = request.POST['max_capacity']
        special_requests = request.POST['special_requests']

        driver = Driver(name=name, email=email, username=username, vehicle_type_registered=vehicle_type_registered, license_plate_number=license_plate_number, max_capacity=max_capacity, special_requests=special_requests)
        driver.save()

        messages.success(request, 'Driver registration successful!')
        return redirect('dashboard')

def driver_edit_info(request):
    if request.method == 'POST':
        driver_id = request.POST['driver_id']
        username = request.POST['driver_username']
        vehicle_type_registered = request.POST['vehicle_type_registered']
        license_plate_number = request.POST['license_plate_number']
        max_capacity = request.POST['max_capacity']
        special_requests = request.POST['special_requests']

        driver = Driver.objects.get(username=username)
        driver.vehicle_type_registered = vehicle_type_registered
        driver.license_plate_number = license_plate_number
        driver.max_capacity = max_capacity
        driver.special_requests = special_requests
        driver.save()
        messages.success(request, 'Driver information update successful!')
        return redirect('dashboard')
        