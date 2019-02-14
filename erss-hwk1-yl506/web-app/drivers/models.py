from django.db import models

# Create your models here.
class Driver(models.Model):
    name = models.CharField(max_length=200)
    email = models.CharField(max_length=200)
    username = models.CharField(max_length=200)
    vehicle_type_registered = models.CharField(max_length=200, blank=False)
    license_plate_number = models.CharField(max_length=200, blank=False)
    max_capacity = models.IntegerField(default=4, blank=False)
    special_requests = models.CharField(max_length=200, blank=False)

    def __str__(self):
        return self.name