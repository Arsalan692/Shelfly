from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth import login, logout, authenticate
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.contrib import messages
from .models import Book, Order, OrderItem, Customer, Payment
from decimal import Decimal

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
        Customer.objects.create(user=user, phone=phone, address=address)
        
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


# Existing views - Updated with authentication
def home_page(request):
    return render(request, 'bookstore/home.html')


def book_list(request):
    books = Book.objects.all()
    return render(request, 'bookstore/book_list.html', {'books': books})


def book_detail(request, book_id):
    book = get_object_or_404(Book, id=book_id)
    return render(request, 'bookstore/book_detail.html', {'book': book})


@login_required(login_url='login')
def place_order(request, book_id):
    book = get_object_or_404(Book, id=book_id)
    customer = request.user.customer  # Get current logged-in customer

    if book.stock <= 0:
        messages.error(request, "Sorry, this book is out of stock!")
        return redirect('book_list')

    order = Order.objects.create(customer=customer)
    OrderItem.objects.create(order=order, book=book, quantity=1, subtotal=book.price)
    Payment.objects.create(order=order, amount=book.price, method="Cash", status="Paid")

    messages.success(request, f"You successfully ordered '{book.title}'!")
    return redirect('order_history')


@login_required(login_url='login')
def order_history(request):
    customer = request.user.customer  # Get current logged-in customer
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
        
        # Save to database or send email
        # Contact.objects.create(name=name, email=email, ...)
        
        messages.success(request, 'Thank you! Your message has been sent.')
        return redirect('contact')
    
    return render(request, 'bookstore/contact.html')