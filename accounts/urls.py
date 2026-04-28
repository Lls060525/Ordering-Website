# accounts/urls.py
from django.urls import path
from . import views

urlpatterns = [
    # Auth views
    path('login/', views.login_view, name='login'),
    path('logout/', views.logout_view, name='logout'),

    # Registration views
    path('signup/customer/', views.customer_signup, name='customer_signup'),
    path('signup/vendor/', views.vendor_signup, name='vendor_signup'),

    # Dashboard routing
    path('dashboard/', views.dashboard_redirect, name='dashboard_redirect'),
    path('dashboard/customer/', views.customer_dashboard, name='customer_dashboard'),
    path('dashboard/vendor/', views.vendor_dashboard, name='vendor_dashboard'),
    path('profile/', views.profile_view, name='user_profile'),
]