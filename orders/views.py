from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.db import transaction
from products.models import Product
from .models import Order, OrderItem


# 1. Add to Cart Logic
def add_to_cart(request, product_id):
    """Adds a product to the session-based shopping cart."""
    product = get_object_or_404(Product, id=product_id)
    cart = request.session.get('cart', {})

    pid = str(product_id)
    if pid in cart:
        cart[pid]['quantity'] += 1
    else:
        cart[pid] = {'quantity': 1, 'price': str(product.price)}

    request.session['cart'] = cart
    messages.success(request, f"{product.name} added to cart!")
    return redirect('marketplace')


# 2. View Cart Logic
def cart_detail(request):
    """Displays items currently in the user's session cart."""
    cart = request.session.get('cart', {})
    cart_items = []
    total_price = 0

    for pid, item in cart.items():
        product = get_object_or_404(Product, id=pid)
        item_total = product.price * item['quantity']
        total_price += item_total
        cart_items.append({
            'product': product,
            'quantity': item['quantity'],
            'total': item_total
        })

    return render(request, 'orders/cart_detail.html', {
        'cart_items': cart_items,
        'total_price': total_price
    })


# 3. Checkout Logic
@login_required
def checkout(request):
    cart = request.session.get('cart', {})
    if not cart:
        messages.warning(request, "Your cart is empty.")
        return redirect('marketplace')

    # Calculate total and prepare data for the review page
    cart_items = []
    total_price = 0
    for pid, item in cart.items():
        product = get_object_or_404(Product, id=pid)
        item_total = product.price * item['quantity']
        total_price += item_total
        cart_items.append({'product': product, 'quantity': item['quantity'], 'total': item_total})

    if request.method == 'POST':
        # 1. Create the Order object
        order = Order.objects.create(
            customer=request.user.customer_profile,
            total_amount=total_price,
            status='Paid'  # Instant status update
        )

        # 2. Move items from Session Cart to OrderItem Model
        for item in cart_items:
            OrderItem.objects.create(
                order=order,
                product=item['product'],
                quantity=item['quantity'],
                price_at_purchase=item['product'].price
            )

        # 3. Clear the session cart
        request.session['cart'] = {}

        messages.success(request, f"Success! Order #{order.id} has been placed and paid.")
        return redirect('customer_orders')

    return render(request, 'orders/checkout.html', {
        'cart_items': cart_items,
        'total_price': total_price
    })


@login_required
def customer_order_history(request):
    """Displays past orders for the logged-in customer."""
    # Fetch orders belonging to this customer profile
    orders = Order.objects.filter(customer=request.user.customer_profile).order_by('-created_at')

    return render(request, 'orders/order_history.html', {
        'orders': orders
    })


# 4. Vendor Sales Logic
@login_required
def vendor_orders(request):
    """Allows a vendor to see orders specifically for their products."""
    if not request.user.is_seller:
        return redirect('customer_dashboard')

    vendor_items = OrderItem.objects.filter(
        product__vendor=request.user.vendor_profile
    ).order_by('-order__created_at')

    return render(request, 'orders/vendor_orders.html', {'vendor_items': vendor_items})