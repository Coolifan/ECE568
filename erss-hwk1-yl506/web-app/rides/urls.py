from django.urls import path
from . import views

urlpatterns = [
    path('', views.index, name='rides'),
    path('<int:ride_id>', views.ride, name='ride'),
    path('owner_request_ride', views.owner_request_ride, name='owner_request_ride'),
    path('driver_search_ride', views.driver_search_ride, name='driver_search_ride'),
    path('sharer_search_ride', views.sharer_search_ride, name='sharer_search_ride'),
    path('owner_edit_ride', views.owner_edit_ride, name='owner_edit_ride'),
    path('owner_cancel_ride', views.owner_cancel_ride, name='owner_cancel_ride'),
    path('sharer_join_ride', views.sharer_join_ride, name='sharer_join_ride'),
    path('sharer_edit_ride', views.sharer_edit_ride, name='sharer_edit_ride'),
    path('sharer_cancel_ride', views.sharer_cancel_ride, name='sharer_cancel_ride'),
    path('driver_confirm_ride', views.driver_confirm_ride, name='driver_confirm_ride'),
    path('driver_complete_ride', views.driver_complete_ride, name='driver_complete_ride'),

]