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
    """Summarizes items and processes the final order record."""
    if not request.user.is_customer:
        return redirect('vendor_dashboard')

    cart = request.session.get('cart', {})
    if not cart:
        messages.error(request, "Your cart is empty.")
        return redirect('marketplace')

    cart_items = []
    total_price = 0
    for pid, item in cart.items():
        product = get_object_or_404(Product, id=pid)
        item_total = product.price * item['quantity']
        total_price += item_total
        cart_items.append({'product': product, 'quantity': item['quantity'], 'total': item_total})

    if request.method == 'POST':
        with transaction.atomic():
            order = Order.objects.create(
                customer=request.user.customer_profile,
                total_amount=total_price,
                status='Pending'
            )

            for pid, item in cart.items():
                product = get_object_or_404(Product, id=pid)
                if product.stock < item['quantity']:
                    messages.error(request, f"Sorry, {product.name} just went out of stock.")
                    return redirect('cart_detail')

                OrderItem.objects.create(
                    order=order,
                    product=product,
                    quantity=item['quantity'],
                    price_at_purchase=product.price
                )

                product.stock -= item['quantity']
                product.save()

            request.session['cart'] = {}
            messages.success(request, "Order placed successfully!")
            return redirect('customer_dashboard')

    return render(request, 'orders/checkout.html', {
        'cart_items': cart_items,
        'total_price': total_price,
        'customer': request.user.customer_profile
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