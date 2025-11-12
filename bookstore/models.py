from django.db import models
from django.contrib.auth.models import User
from django.db.models.signals import post_save
from django.dispatch import receiver
from django.core.exceptions import ValidationError

class Customer(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    phone = models.CharField(max_length=15)
    address = models.TextField()
    registration_date = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.user.username


class Book(models.Model):
    title = models.CharField(max_length=200)
    author = models.CharField(max_length=100)
    category = models.CharField(max_length=50)
    price = models.DecimalField(max_digits=8, decimal_places=2)
    stock = models.PositiveIntegerField()
    description = models.TextField(blank=True, null=True)
    isbn = models.CharField(max_length=13, blank=True, null=True)

    def __str__(self):
        return self.title


class Order(models.Model):
    STATUS_CHOICES = [
        ('Pending', 'Pending'),
        ('Confirmed', 'Confirmed'),
        ('Shipped', 'Shipped'),
        ('Delivered', 'Delivered'),
        ('Cancelled', 'Cancelled'),
    ]
    
    customer = models.ForeignKey(Customer, on_delete=models.CASCADE)
    order_date = models.DateTimeField(auto_now_add=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='Pending')

    def __str__(self):
        return f"Order #{self.id} - {self.customer.user.username}"
    
    @property
    def total_amount(self):
        """Auto calculate order total"""
        return sum(item.subtotal for item in self.orderitem_set.all())

    class Meta:
        ordering = ['-order_date']


class OrderItem(models.Model):
    order = models.ForeignKey(Order, on_delete=models.CASCADE)
    book = models.ForeignKey(Book, on_delete=models.CASCADE)
    quantity = models.PositiveIntegerField()
    unit_price = models.DecimalField(max_digits=8, decimal_places=2)
    subtotal = models.DecimalField(max_digits=8, decimal_places=2)

    def save(self, *args, **kwargs):
        self.unit_price = self.book.price
        self.subtotal = self.unit_price * self.quantity
        
        # Only reduce stock for new order items
        if not self.pk:
            if self.book.stock >= self.quantity:
                self.book.stock -= self.quantity
                self.book.save()
            else:
                raise ValidationError(f"Insufficient stock for {self.book.title}")
        
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.book.title} x {self.quantity}"


class Payment(models.Model):
    PAYMENT_METHODS = [
        ('Cash', 'Cash on Delivery'),
        ('Card', 'Credit/Debit Card'),
        ('UPI', 'UPI'),
        ('Wallet', 'E-Wallet'),
    ]
    
    PAYMENT_STATUS = [
        ('Unpaid', 'Unpaid'),
        ('Paid', 'Paid'),
        ('Failed', 'Failed'),
        ('Refunded', 'Refunded'),
    ]
    
    order = models.OneToOneField(Order, on_delete=models.CASCADE)
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    method = models.CharField(max_length=50, choices=PAYMENT_METHODS)
    status = models.CharField(max_length=20, choices=PAYMENT_STATUS, default='Unpaid')
    transaction_id = models.CharField(max_length=100, blank=True, null=True)
    date = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Payment for Order #{self.order.id} - {self.status}"

class Cart(models.Model):
    customer = models.OneToOneField(Customer, on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"Cart - {self.customer.user.username}"
    
    @property
    def total_amount(self):
        """Calculate total cart value"""
        return sum(item.subtotal for item in self.cartitem_set.all())
    
    @property
    def total_items(self):
        """Count total items in cart"""
        return sum(item.quantity for item in self.cartitem_set.all())


class CartItem(models.Model):
    cart = models.ForeignKey(Cart, on_delete=models.CASCADE)
    book = models.ForeignKey(Book, on_delete=models.CASCADE)
    quantity = models.PositiveIntegerField(default=1)
    added_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('cart', 'book')  # Prevent duplicate books in same cart

    def __str__(self):
        return f"{self.book.title} x {self.quantity}"
    
    @property
    def subtotal(self):
        """Calculate subtotal for this item"""
        return self.book.price * self.quantity



@receiver(post_save, sender=Payment)
def update_order_status(sender, instance, created, **kwargs):
    """Mark order as confirmed if payment is paid"""
    if instance.status == "Paid" and instance.order.status == "Pending":
        instance.order.status = "Confirmed"
        instance.order.save()