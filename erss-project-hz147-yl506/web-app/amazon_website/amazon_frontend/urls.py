from django.urls import path
from . import views

urlpatterns = [
    path('', views.index, name='index'),
    path('buy', views.buy, name='buy'),
    path('change_destination', views.change_destination, name='change_destination'),
    path('cancel', views.cancel, name='cancel'),
    path('query', views.query, name='query'),
    path('add_to_cart', views.add_to_cart, name='add_to_cart'),
]