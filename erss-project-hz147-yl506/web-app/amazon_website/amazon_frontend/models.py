from django.db import models
from django.contrib.auth.models import User

# Create your models here.
class Product(models.Model):
    name = models.CharField(max_length=500, default="Product name")
    description = models.CharField(max_length=2000, default ="Product description")
    seller = models.CharField(max_length=500, default="Product seller")
    price = models.DecimalField(max_digits=9, decimal_places=2)
    def __str__(self):
        return self.name

class UserCartTuple(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    num_product = models.IntegerField(default=1)

    class Meta:
        unique_together = (('user', 'product'),)
    def __str__(self):
        return self.user.name + ' ' + self.product.name + ' ' + str(self.num_product) 

class Warehouse(models.Model):
    location_x = models.IntegerField()
    location_y = models.IntegerField()

    class Meta:
        unique_together = (('location_x', 'location_y'),)

class WarehouseStock(models.Model):
    warehouse = models.ForeignKey(Warehouse, on_delete=models.CASCADE)
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    num_product = models.IntegerField()

    class Meta:
        unique_together = (('warehouse','product'),)

class Order(models.Model):
    truck_id = models.IntegerField(blank=True, null=True)
    ups_account = models.CharField(max_length=100, blank=True)
    user = models.ForeignKey(User, on_delete=models.CASCADE, null=True)
    status  = models.CharField(max_length=500, default ="status")
    destination_x = models.IntegerField()
    destination_y = models.IntegerField()
    warehouse = models.ForeignKey(Warehouse, on_delete=models.CASCADE, null=True)
    price = models.DecimalField(max_digits=9, decimal_places=2)
    time_created = models.DateTimeField(auto_now_add=True)
    time_packed = models.DateTimeField(blank=True, null=True)
    time_loaded = models.DateTimeField(blank=True, null=True)
    time_delivered = models.DateTimeField(blank=True, null=True)
    tracking_number = models.IntegerField(blank=True, null=True)

class OrderProductTuple(models.Model):
    order = models.ForeignKey(Order, on_delete=models.CASCADE)
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    num_product = models.IntegerField()
    
    class Meta:
        unique_together = (('order', 'product'),)