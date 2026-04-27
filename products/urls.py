from django.urls import path
from . import views

urlpatterns = [
    path('my-products/', views.vendor_product_list, name='vendor_product_list'),
    path('add/', views.add_product, name='add_product'),
    path('marketplace/', views.product_marketplace, name='marketplace'),
    path('edit/<int:product_id>/', views.edit_product, name='edit_product'),
]