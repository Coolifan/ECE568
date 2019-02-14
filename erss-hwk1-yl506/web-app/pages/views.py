from django.shortcuts import render

from drivers.models import Driver

# Create your views here.
def index(request):
    return render(request, 'pages/index.html')

def request_ride(request):
    return render(request, 'pages/request.html')

def claim_ride(request):
    from django.core.exceptions import ObjectDoesNotExist
    is_driver = True
    try:
        driver = Driver.objects.get(username=request.user.username)
    except ObjectDoesNotExist:
        is_driver = False
    
    context = {
        'is_driver': is_driver
    }
    return render(request, 'pages/claim.html', context)

def join_ride(request):
    return render(request, 'pages/join.html')