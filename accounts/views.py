#accounts views.py
from django.contrib import messages
from django.shortcuts import render, redirect
from django.contrib.auth import login, authenticate, logout
from django.contrib.auth.decorators import login_required

from orders.models import Order
from products.models import Product
from .forms import CustomerSignUpForm, VendorSignUpForm # You will need to create these
from django.contrib.auth.forms import AuthenticationForm

# 1. Dashboard Redirect Logic
@login_required
def dashboard_redirect(request):
    """Redirects users to their specific dashboard based on their role."""
    if request.user.is_superuser or request.user.is_staff:
        return redirect('/admin/') # Django built-in Admin side
    elif request.user.is_seller:
        return redirect('vendor_dashboard')
    elif request.user.is_customer:
        return redirect('customer_dashboard')
    else:
        return redirect('login')

# 2. Registration Views
def customer_signup(request):
    if request.method == 'POST':
        form = CustomerSignUpForm(request.POST) #
        if form.is_valid():
            user = form.save()
            login(request, user)
            messages.success(request, "Registration successful! Welcome to the marketplace.")
            return redirect('customer_dashboard')
        else:
            messages.error(request, "Please correct the errors below.")
    else:
        form = CustomerSignUpForm()
    return render(request, 'accounts/signup_customer.html', {'form': form})

def vendor_signup(request):
    if request.method == 'POST':
        form = VendorSignUpForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            return redirect('vendor_dashboard')
    else:
        form = VendorSignUpForm()
    return render(request, 'accounts/signup_vendor.html', {'form': form})

# 3. Login / Logout
def login_view(request):
    if request.method == 'POST':
        form = AuthenticationForm(data=request.POST)
        if form.is_valid():
            user = form.get_user()
            login(request, user)
            messages.success(request, f"Welcome back, {user.username}!") #
            return redirect('dashboard_redirect')
        else:
            messages.error(request, "Invalid username or password.") #
    else:
        form = AuthenticationForm()
    return render(request, 'accounts/login.html', {'form': form})

def logout_view(request):
    logout(request)
    return redirect('login')


@login_required
def customer_dashboard(request):
    if not request.user.is_customer:
        return redirect('vendor_dashboard')

    # Fetch data for the unified dashboard
    products = Product.objects.filter(stock__gt=0).order_by('-id')
    recent_orders = Order.objects.filter(customer=request.user.customer_profile).order_by('-created_at')[:5]

    return render(request, 'accounts/customer_dashboard.html', {
        'products': products,
        'orders': recent_orders,
    })

@login_required
def vendor_dashboard(request):
    if not request.user.is_seller:
        return redirect('customer_dashboard')

    # NEW: Fetch products for the current vendor
    vendor_products = Product.objects.filter(vendor=request.user.vendor_profile)

    return render(request, 'accounts/vendor_dashboard.html', {
        'products': vendor_products  # Pass the list to the template
    })