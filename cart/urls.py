from django.urls import path
from . import views

app_name = 'cart'

urlpatterns = [
    path('', views.view_cart, name='view'),  # კალათის ნახვა
    path('add/', views.choose_bus_stop, name='choose_stop'),  # გაჩერების არჩევა
    path('add/<int:stop_id>/', views.add_cart_choose_bus_and_time, name='add_bus_time'),  # დროისა და ავტობუსის არჩევა და დამატება
    path('delete/<int:item_id>/', views.delete_cart_item, name='delete_item'),
]
