from django.urls import path
from . import views

urlpatterns = [
    path('ავტობუსები/', views.bus_stop_list, name='Buses'),
    path('ავტობუსები/<str:stop_id>/', views.bus_stop_detail, name='Buses_detail'),
]