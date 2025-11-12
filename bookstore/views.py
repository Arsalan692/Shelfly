from django.shortcuts import render, get_object_or_404, redirect
from .models import Book, Order, OrderItem, Customer, Payment
from django.contrib import messages
from decimal import Decimal

def home_page(request):
    return render(request, 'bookstore/home.html')


def book_list(request):
    books = Book.objects.all()
    return render(request, 'bookstore/book_list.html', {'books': books})


def book_detail(request, book_id):
    book = get_object_or_404(Book, id=book_id)
    return render(request, 'bookstore/book_detail.html', {'book': book})


def place_order(request, book_id):
    book = get_object_or_404(Book, id=book_id)
    customer = Customer.objects.first() 

    if book.stock <= 0:
        messages.error(request, "Sorry, this book is out of stock!")
        return redirect('book_list')

    order = Order.objects.create(customer=customer)
    OrderItem.objects.create(order=order, book=book, quantity=1, subtotal=book.price)
    Payment.objects.create(order=order, amount=book.price, method="Cash", status="Paid")

    messages.success(request, f"You successfully ordered '{book.title}'!")
    return redirect('order_history')


def order_history(request):
    customer = Customer.objects.first()
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

        # I will make the connection later... . .

        # Contact.objects.create(name=name, email=email, ...)
        
        messages.success(request, 'Thank you! Your message has been sent.')
        return redirect('contact')
    
    return render(request, 'bookstore/contact.html')