from django.urls import path
from . import views

urlpatterns = [
    path('login', views.login, name='login'),
    path('register', views.register, name='register'),
    path('logout', views.logout, name='logout'),
    path('dashboard', views.dashboard, name='dashboard'),
    path('driver_register', views.driver_register, name='driver_register'),
    path('driver_edit_info', views.driver_edit_info, name='driver_edit_info'),
]