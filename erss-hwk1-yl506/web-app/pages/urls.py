from django.urls import path
from . import views

urlpatterns = [
    path('', views.index, name='index'),
    path('request', views.request_ride, name='request'),
    path('claim', views.claim_ride, name='claim'),
    path('join', views.join_ride, name='join'),
]