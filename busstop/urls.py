from django.urls import path, include
from . import views

urlpatterns = [
    path('', views.bus_stop_list, name='bus_stops'),
    path('გაჩერებები/<int:stop_id>/', views.bus_stop_detail, name='bus_stop_detail'),
    path('buses/', include('buses.urls')),  
]