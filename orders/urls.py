from django.urls import path
from . import views

urlpatterns = [
    path('cart/', views.cart_detail, name='cart_detail'),
    path('add/<int:product_id>/', views.add_to_cart, name='add_to_cart'),
    path('checkout/', views.checkout, name='checkout'),
    path('my-sales/', views.vendor_orders, name='vendor_orders'),
    path('history/', views.customer_order_history, name='customer_orders'),
]