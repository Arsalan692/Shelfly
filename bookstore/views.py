from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth import login, logout, authenticate
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.contrib import messages
from .models import Book, Order, OrderItem, Customer, Payment, Cart, CartItem, Coupon, CouponUsage
from decimal import Decimal
import json
from django.http import JsonResponse
from django.db.models import Q

# Authentication Views
def register(request):
    if request.method == 'POST':
        username = request.POST.get('username')
        email = request.POST.get('email')
        password = request.POST.get('password')
        password_confirm = request.POST.get('password_confirm')
        phone = request.POST.get('phone')
        address = request.POST.get('address')
        
        # Validation
        if password != password_confirm:
            messages.error(request, 'Passwords do not match!')
            return redirect('register')
        
        if User.objects.filter(username=username).exists():
            messages.error(request, 'Username already exists!')
            return redirect('register')
        
        if User.objects.filter(email=email).exists():
            messages.error(request, 'Email already registered!')
            return redirect('register')
        
        # Create User and Customer
        user = User.objects.create_user(username=username, email=email, password=password)
        customer = Customer.objects.create(user=user, phone=phone, address=address, is_first_time_buyer=True)
        
        Cart.objects.create(customer=customer)
        messages.success(request, 'Account created successfully! Please login.')
        return redirect('login')
    
    return render(request, 'bookstore/register.html')


def login_view(request):
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')
        
        user = authenticate(request, username=username, password=password)
        
        if user is not None:
            login(request, user)
            messages.success(request, f'Welcome back, {username}!')
            return redirect('home')
        else:
            messages.error(request, 'Invalid username or password!')
            return redirect('login')
    
    return render(request, 'bookstore/login.html')


def logout_view(request):
    logout(request)
    messages.success(request, 'You have been logged out successfully!')
    return redirect('home')


# Main Pages
def home_page(request):
    return render(request, 'bookstore/home.html')


def book_list(request):
    # Get search query from GET parameters
    search_query = request.GET.get('search', '').strip()
    
    # Start with all books
    books = Book.objects.all()
    
    # Apply search filter if query exists
    if search_query:
        books = books.filter(
            Q(title__icontains=search_query) |
            Q(author__icontains=search_query) |
            Q(category__icontains=search_query) |
            Q(isbn__icontains=search_query)
        )
    
    context = {
        'books': books,
        'search_query': search_query,
    }
    
    return render(request, 'bookstore/book_list.html', context)


def book_detail(request, book_id):
    book = get_object_or_404(Book, id=book_id)
    return render(request, 'bookstore/book_detail.html', {'book': book})


@login_required(login_url='login')
def order_history(request):
    customer = request.user.customer
    orders = Order.objects.filter(customer=customer)
    return render(request, 'bookstore/order_history.html', {'orders': orders})


def about_page(request):
    return render(request, 'bookstore/about.html')


def contact(request):
    if request.method == 'POST':
        name = request.POST.get('name')
        email = request.POST.get('email')
        phone = request.POST.get('phone')
        subject = request.POST.get('subject')
        message = request.POST.get('message')
        
        messages.success(request, 'Thank you! Your message has been sent.')
        return redirect('contact')
    
    return render(request, 'bookstore/contact.html')


# Cart Management
@login_required(login_url='login')
def add_to_cart(request, book_id):
    book = get_object_or_404(Book, id=book_id)
    customer = request.user.customer
    
    cart, created = Cart.objects.get_or_create(customer=customer)
    cart_item, created = CartItem.objects.get_or_create(cart=cart, book=book)
    
    if not created:
        if cart_item.quantity < book.stock:
            cart_item.quantity += 1
            cart_item.save()
            messages.success(request, f"Increased quantity of '{book.title}' in cart!")
        else:
            messages.warning(request, f"Cannot add more. Only {book.stock} in stock!")
    else:
        messages.success(request, f"'{book.title}' added to cart!")
    
    return redirect('view_cart')


@login_required(login_url='login')
def view_cart(request):
    customer = request.user.customer
    cart, created = Cart.objects.get_or_create(customer=customer)
    cart_items = cart.cartitem_set.all()
    
    context = {
        'cart': cart,
        'cart_items': cart_items,
    }
    return render(request, 'bookstore/cart.html', context)


@login_required(login_url='login')
def apply_coupon(request):
    if request.method == 'POST':
        coupon_code = request.POST.get('coupon_code', '').strip().upper()
        customer = request.user.customer
        cart = get_object_or_404(Cart, customer=customer)
        
        if not coupon_code:
            messages.error(request, 'Please enter a coupon code!')
            return redirect('view_cart')
        
        try:
            coupon = Coupon.objects.get(code=coupon_code)
        except Coupon.DoesNotExist:
            messages.error(request, 'Invalid coupon code!')
            return redirect('view_cart')
        
        # Validate coupon
        is_valid, msg = coupon.is_valid()
        if not is_valid:
            messages.error(request, f"Coupon error: {msg}")
            return redirect('view_cart')
        
        # Check minimum purchase
        if cart.subtotal < coupon.min_purchase:
            messages.error(request, f'Minimum purchase of Rs. {coupon.min_purchase} required for this coupon!')
            return redirect('view_cart')
        
        # Apply coupon
        cart.applied_coupon = coupon
        cart.save()
        
        discount_amount = coupon.calculate_discount(cart.subtotal)
        messages.success(request, f'Coupon "{coupon_code}" applied! You saved Rs. {discount_amount:.2f}')
        return redirect('view_cart')
    
    return redirect('view_cart')


@login_required(login_url='login')
def remove_coupon(request):
    if request.method == 'POST':
        customer = request.user.customer
        cart = get_object_or_404(Cart, customer=customer)
        
        if cart.applied_coupon:
            coupon_code = cart.applied_coupon.code
            cart.applied_coupon = None
            cart.save()
            messages.success(request, f'Coupon "{coupon_code}" removed!')
        else:
            messages.warning(request, 'No coupon applied!')
        
        return redirect('view_cart')
    
    return redirect('view_cart')


@login_required(login_url='login')
def update_cart_item(request, item_id):
    cart_item = get_object_or_404(CartItem, id=item_id, cart__customer=request.user.customer)
    
    if request.method == 'POST':
        action = request.POST.get('action')
        
        if action == 'increase':
            if cart_item.quantity < cart_item.book.stock:
                cart_item.quantity += 1
                cart_item.save()
                messages.success(request, 'Quantity updated!')
            else:
                messages.warning(request, 'Maximum stock reached!')
        
        elif action == 'decrease':
            if cart_item.quantity > 1:
                cart_item.quantity -= 1
                cart_item.save()
                messages.success(request, 'Quantity updated!')
            else:
                messages.warning(request, 'Minimum quantity is 1!')
    
    return redirect('view_cart')


@login_required(login_url='login')
def remove_from_cart(request, item_id):
    cart_item = get_object_or_404(CartItem, id=item_id, cart__customer=request.user.customer)
    book_title = cart_item.book.title
    cart_item.delete()
    messages.success(request, f"'{book_title}' removed from cart!")
    return redirect('view_cart')


# Checkout and Order Processing
@login_required(login_url='login')
def checkout(request):
    customer = request.user.customer
    cart = get_object_or_404(Cart, customer=customer)
    cart_items = cart.cartitem_set.all()
    
    if not cart_items:
        messages.warning(request, 'Your cart is empty!')
        return redirect('view_cart')
    
    if request.method == 'POST':
        payment_method = request.POST.get('payment_method', 'Cash')
        delivery_name = request.POST.get('delivery_name')
        delivery_phone = request.POST.get('delivery_phone')
        delivery_address = request.POST.get('delivery_address')
        delivery_notes = request.POST.get('delivery_notes', '')
        
        # Create Order
        order = Order.objects.create(
            customer=customer,
            delivery_name=delivery_name,
            delivery_phone=delivery_phone,
            delivery_address=delivery_address,
            delivery_notes=delivery_notes,
            shipping_fee=cart.shipping_fee,
            applied_coupon=cart.applied_coupon,
            coupon_discount=cart.coupon_discount,
            order_value_discount=cart.order_value_discount,
            first_time_discount=cart.first_time_discount,
            discount_code_used=cart.applied_coupon.code if cart.applied_coupon else None
        )
        
        # Create Order Items
        for cart_item in cart_items:
            OrderItem.objects.create(
                order=order,
                book=cart_item.book,
                quantity=cart_item.quantity,
                unit_price=cart_item.book.price,
                subtotal=cart_item.subtotal
            )
        
        # Update Coupon Usage
        if cart.applied_coupon:
            coupon = cart.applied_coupon
            coupon.current_usage += 1
            coupon.save()
            
            CouponUsage.objects.create(
                coupon=coupon,
                customer=customer,
                order=order
            )
        
        # Update First-Time Buyer Status
        if customer.is_first_time_buyer:
            customer.is_first_time_buyer = False
            customer.save()
        
        # Create Payment
        Payment.objects.create(
            order=order,
            amount=order.total_amount,
            method=payment_method,
            status='Paid'
        )
        
        # Clear Cart
        cart_items.delete()
        cart.applied_coupon = None
        cart.save()
        
        messages.success(request, f'Order #{order.id} placed successfully! You saved Rs. {order.total_discount:.2f}')
        return redirect('order_history')
    
    context = {
        'cart': cart,
        'cart_items': cart_items,
        'customer': customer,
    }
    return render(request, 'bookstore/checkout.html', context)


@login_required(login_url='login')
def edit_profile(request):
    customer = request.user.customer
    
    if request.method == 'POST':
        email = request.POST.get('email')
        phone = request.POST.get('phone')
        address = request.POST.get('address')
        
        request.user.email = email
        request.user.save()
        
        customer.phone = phone
        customer.address = address
        customer.save()
        
        messages.success(request, 'Profile updated successfully!')
        return redirect('edit_profile')
    
    return render(request, 'bookstore/edit_profile.html', {'customer': customer})