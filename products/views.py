from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from .models import Product
from .forms import ProductForm


@login_required
def vendor_product_list(request):
    """Shows only the products belonging to the logged-in vendor."""
    if not request.user.is_seller:
        return redirect('customer_dashboard')

    # We use vendor_profile because of the related_name in your OneToOneField
    products = Product.objects.filter(vendor=request.user.vendor_profile)
    return render(request, 'products/vendor_product_list.html', {'products': products})


@login_required
def add_product(request):
    """Handles adding new products with images."""
    if request.method == 'POST':
        # NEW: request.FILES handles the image upload
        form = ProductForm(request.POST, request.FILES)
        if form.is_valid():
            product = form.save(commit=False)
            product.vendor = request.user.vendor_profile
            product.save()
            messages.success(request, f"Product '{product.name}' added successfully!")
            return redirect('vendor_product_list')
    else:
        form = ProductForm()

    # We share the modern 'product_form.html' for add/edit
    return render(request, 'products/product_form.html', {
        'form': form,
        'title': 'Add New Product'
    })


def product_marketplace(request):
    """A public view showing products with optional category filtering."""
    # 1. Get the category name from the URL (e.g., ?category=Tech)
    category_name = request.GET.get('category')

    # 2. Filter products based on the category if provided
    if category_name:
        all_products = Product.objects.filter(category__name=category_name, stock__gt=0)
    else:
        all_products = Product.objects.filter(stock__gt=0)

    # 3. Get all categories to display the filter links in the template
    categories = Product.objects.values_list('category', flat=True).exclude(category__isnull=True).exclude(category='').distinct()

    return render(request, 'products/marketplace.html', {
        'products': all_products,
        'categories': categories,
        'selected_category': category_name
    })

@login_required
def edit_product(request, product_id):
    """Allows vendors to update their existing products."""
    # Fetch the product or return a 404 if it doesn't exist or doesn't belong to the vendor
    product = get_object_or_404(Product, id=product_id, vendor=request.user.vendor_profile)

    if request.method == 'POST':
        # 'instance=product' tells Django to update this specific record instead of creating a new one
        # Include request.FILES for your new image support!
        form = ProductForm(request.POST, request.FILES, instance=product)
        if form.is_valid():
            form.save()
            messages.success(request, f"'{product.name}' has been updated!")
            return redirect('vendor_dashboard') # Or vendor_product_list
    else:
        # Pre-fill the form with the current product data
        form = ProductForm(instance=product)

    return render(request, 'products/product_form.html', {
        'form': form,
        'title': 'Edit Product' # Pass a dynamic title
    })