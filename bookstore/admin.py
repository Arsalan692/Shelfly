from django.contrib import admin
from django.contrib.auth.models import User
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from .models import Customer, Book, Order, OrderItem, Payment, Cart, CartItem

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
    list_display = ('id', 'title', 'author', 'category', 'price', 'stock', 'isbn', 'cover_image_preview')
    search_fields = ('title', 'author', 'isbn')
    list_filter = ('category',)
    
    def cover_image_preview(self, obj):
        if obj.cover_image:
            return f'<img src="{obj.cover_image.url}" width="50" height="75" />'
        return "No Image"
    
    cover_image_preview.allow_tags = True
    cover_image_preview.short_description = 'Cover'

@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    list_display = ('id', 'customer', 'order_date', 'status', 'subtotal_display', 'shipping_fee', 'total_amount')
    list_filter = ('status', 'order_date')
    search_fields = ('customer__user__username',)
    
    def subtotal_display(self, obj):
        return f"Rs. {obj.subtotal}"
    subtotal_display.short_description = 'Subtotal'

@admin.register(OrderItem)
class OrderItemAdmin(admin.ModelAdmin):
    list_display = ('order', 'book', 'quantity', 'unit_price', 'subtotal')

@admin.register(Payment)
class PaymentAdmin(admin.ModelAdmin):
    list_display = ('order', 'amount', 'method', 'status', 'date')
    list_filter = ('status', 'method', 'date')

@admin.register(Cart)
class CartAdmin(admin.ModelAdmin):
    list_display = ('id', 'customer', 'total_items', 'subtotal_display', 'shipping_display', 'total_display', 'updated_at')
    search_fields = ('customer__user__username',)
    
    def subtotal_display(self, obj):
        return f"Rs. {obj.subtotal}"
    subtotal_display.short_description = 'Subtotal'
    
    def shipping_display(self, obj):
        if obj.shipping_fee == 0:
            return "FREE"
        return f"Rs. {obj.shipping_fee}"
    shipping_display.short_description = 'Shipping'
    
    def total_display(self, obj):
        return f"Rs. {obj.total_amount}"
    total_display.short_description = 'Total'

@admin.register(CartItem)
class CartItemAdmin(admin.ModelAdmin):
    list_display = ('cart', 'book', 'quantity', 'subtotal', 'added_at')