from django.contrib import admin
from django.contrib.auth.models import User
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from .models import Customer, Book, Order, OrderItem, Payment

# Inline Customer info with User
class CustomerInline(admin.StackedInline):
    model = Customer
    can_delete = False
    verbose_name_plural = 'Customer Profile'

# Extend User Admin
class UserAdmin(BaseUserAdmin):
    inlines = (CustomerInline,)

# Re-register UserAdmin
admin.site.unregister(User)
admin.site.register(User, UserAdmin)

@admin.register(Customer)
class CustomerAdmin(admin.ModelAdmin):
    list_display = ('id', 'user', 'phone', 'address', 'registration_date')
    search_fields = ('user__username', 'user__email', 'phone')
    list_filter = ('registration_date',)

@admin.register(Book)
class BookAdmin(admin.ModelAdmin):
    list_display = ('id', 'title', 'author', 'category', 'price', 'stock', 'isbn')
    search_fields = ('title', 'author', 'isbn')
    list_filter = ('category',)

@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    list_display = ('id', 'customer', 'order_date', 'status', 'total_amount')
    list_filter = ('status', 'order_date')
    search_fields = ('customer__user__username',)

@admin.register(OrderItem)
class OrderItemAdmin(admin.ModelAdmin):
    list_display = ('order', 'book', 'quantity', 'unit_price', 'subtotal')

@admin.register(Payment)
class PaymentAdmin(admin.ModelAdmin):
    list_display = ('order', 'amount', 'method', 'status', 'date')
    list_filter = ('status', 'method', 'date')