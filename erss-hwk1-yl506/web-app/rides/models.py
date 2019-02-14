from django.db import models
from owners.models import Owner
from drivers.models import Driver
from sharers.models import Sharer
from datetime import datetime

# Create your models here.
class Ride(models.Model):
    # Owners related
    #owner = models.ForeignKey(Owner, on_delete=models.DO_NOTHING)
    owner_name = models.CharField(max_length=200)
    owner_email = models.CharField(max_length=200)
    owner_id = models.IntegerField()

    destination_owner = models.CharField(max_length=200)
    arrival_time_owner = models.DateTimeField(default=datetime.now, blank=True)
    passengers_owner = models.IntegerField(default=1)
    is_shareable = models.BooleanField(default=True)
    vehicle_type_requested = models.CharField(max_length=200, blank=True)
    special_requests_owner = models.CharField(max_length=200, blank=True)
    

    # Drivers related
    #driver = models.ForeignKey(Driver, on_delete=models.DO_NOTHING)
    driver_name = models.CharField(max_length=200, blank=True)
    driver_email = models.CharField(max_length=200, blank=True)
    driver_id = models.IntegerField(default=0)

    vehicle_type_registered = models.CharField(max_length=200, blank=True)
    license_plate_number = models.CharField(max_length=200, blank=True)
    max_capacity = models.IntegerField(default=4, blank=True)
    special_requests_driver = models.CharField(max_length=200, blank=True)
    

    # Sharers related
    #sharer = models.ForeignKey(Sharer, on_delete=models.DO_NOTHING)
    sharer_name = models.CharField(max_length=200, blank=True)
    sharer_email = models.CharField(max_length=200, blank=True)
    sharer_id = models.IntegerField(default=0)

    destination_sharer = models.CharField(max_length=200, blank=True)
    arrival_time_sharer = models.DateTimeField(default=datetime.now, blank=True)
    passengers_sharer = models.IntegerField(default=0, blank=True)

    # Other parameters
    is_confirmed = models.BooleanField(default=False)
    is_completed = models.BooleanField(default=False)

    def __str__(self):
        return self.owner_name + "'s Ride with " + self.driver_name + " on " + '{:%Y-%m-%d, %H:%M}'.format(self.arrival_time_owner)