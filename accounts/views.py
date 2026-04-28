#accounts views.py
from django.contrib import messages
from django.shortcuts import render, redirect
from django.contrib.auth import login, authenticate, logout
from django.contrib.auth.decorators import login_required
from django.db.models import Q

from orders.models import Order
from products import models
from products.models import Product
from .forms import CustomerSignUpForm, VendorSignUpForm, UserUpdateForm, \
    CustomerProfileForm, VendorProfileForm  # You will need to create these
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
    query = request.GET.get('q', '')
    cat_name = request.GET.get('category', '')

    products = Product.objects.filter(stock__gt=0).order_by('-id')

    if query:
        products = products.filter(Q(name__icontains=query) | Q(description__icontains=query))

    if cat_name:
        products = products.filter(category=cat_name) # Filter by string match

    # Fetch unique category strings currently used in the system
    categories = Product.objects.values_list('category', flat=True).exclude(category__isnull=True).exclude(category='').distinct()

    return render(request, 'accounts/customer_dashboard.html', {
        'products': products,
        'categories': categories, # This is now a list of strings
        'selected_category': cat_name,
        'query': query
    })

@login_required
def vendor_dashboard(request):
    if not request.user.is_seller:
        return redirect('customer_dashboard')

    # NEW: Fetch products for the current vendor
    vendor_products = Product.objects.filter(vendor=request.user.vendor_profile)
    categories = Product.objects.values_list('category', flat=True).exclude(category__isnull=True).exclude(category='').distinct()


    return render(request, 'accounts/vendor_dashboard.html', {
        'products': vendor_products  # Pass the list to the template
    })


@login_required
def profile_view(request):
    user = request.user

    # Initialize both forms
    u_form = UserUpdateForm(instance=user)

    if user.is_customer:
        p_form = CustomerProfileForm(instance=user.customer_profile)
    else:
        p_form = VendorProfileForm(instance=user.vendor_profile)

    if request.method == 'POST':
        u_form = UserUpdateForm(request.POST, instance=user)

        if user.is_customer:
            p_form = CustomerProfileForm(request.POST, instance=user.customer_profile)
        else:
            p_form = VendorProfileForm(request.POST, instance=user.vendor_profile)

        if u_form.is_valid() and p_form.is_valid():
            u_form.save()
            p_form.save()
            messages.success(request, "Your profile has been updated!")
            return redirect('user_profile')

    return render(request, 'accounts/profile.html', {
        'u_form': u_form,
        'p_form': p_form
    })