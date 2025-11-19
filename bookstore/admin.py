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
    
    # Editable fields in the form
    fields = ('user', 'phone', 'address', 'registration_date')
    readonly_fields = ('registration_date',)
    
    # Allow inline editing of phone in list view
    list_editable = ('phone',)


@admin.register(Book)
class BookAdmin(admin.ModelAdmin):
    list_display = ('id', 'title', 'author', 'category', 'price', 'stock', 'isbn', 'cover_image_preview')
    search_fields = ('title', 'author', 'isbn')
    list_filter = ('category',)
    
    # Make price and stock editable directly in list view
    list_editable = ('price', 'stock')
    
    # Fields shown in the edit form
    fields = ('title', 'author', 'category', 'isbn', 'description', 'price', 'stock', 'cover_image')
    
    def cover_image_preview(self, obj):
        if obj.cover_image:
            return f'<img src="{obj.cover_image.url}" width="50" height="75" />'
        return "No Image"
    
    cover_image_preview.allow_tags = True
    cover_image_preview.short_description = 'Cover'


# Inline for OrderItems in Order
class OrderItemInline(admin.TabularInline):
    model = OrderItem
    extra = 0  # Don't show empty forms
    fields = ('book', 'quantity', 'unit_price', 'subtotal')
    readonly_fields = ('unit_price', 'subtotal')
    can_delete = True


@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    list_display = ('id', 'customer', 'order_date', 'status', 'subtotal_display', 'shipping_fee', 'total_amount')
    list_filter = ('status', 'order_date')
    search_fields = ('customer__user__username', 'delivery_name', 'delivery_phone')
    
    # Make status editable directly in list view
    list_editable = ('status',)
    
    # Show OrderItems inline when editing an order
    inlines = [OrderItemInline]
    
    # Fields in the edit form
    fieldsets = (
        ('Order Information', {
            'fields': ('customer', 'status', 'order_date')
        }),
        ('Delivery Details', {
            'fields': ('delivery_name', 'delivery_phone', 'delivery_address', 'delivery_notes')
        }),
        ('Pricing', {
            'fields': ('shipping_fee',)
        }),
    )
    
    readonly_fields = ('order_date',)
    
    def subtotal_display(self, obj):
        return f"Rs. {obj.subtotal}"
    subtotal_display.short_description = 'Subtotal'


@admin.register(OrderItem)
class OrderItemAdmin(admin.ModelAdmin):
    list_display = ('order', 'book', 'quantity', 'unit_price', 'subtotal')
    list_filter = ('order__order_date',)
    search_fields = ('order__id', 'book__title')
    
    # Fields in edit form
    fields = ('order', 'book', 'quantity', 'unit_price', 'subtotal')
    readonly_fields = ('unit_price', 'subtotal')


@admin.register(Payment)
class PaymentAdmin(admin.ModelAdmin):
    list_display = ('id', 'order', 'amount', 'method', 'status', 'transaction_id', 'date')
    list_filter = ('status', 'method', 'date')
    search_fields = ('order__id', 'transaction_id')
    
    # Make status editable in list view
    list_editable = ('status',)
    
    # Fields in edit form
    fields = ('order', 'amount', 'method', 'status', 'transaction_id', 'date')
    readonly_fields = ('date',)


# Inline for CartItems in Cart
class CartItemInline(admin.TabularInline):
    model = CartItem
    extra = 0
    fields = ('book', 'quantity', 'subtotal_display', 'added_at')
    readonly_fields = ('subtotal_display', 'added_at')
    
    def subtotal_display(self, obj):
        return f"Rs. {obj.subtotal}"
    subtotal_display.short_description = 'Subtotal'


@admin.register(Cart)
class CartAdmin(admin.ModelAdmin):
    list_display = ('id', 'customer', 'total_items', 'subtotal_display', 'shipping_display', 'total_display', 'updated_at')
    search_fields = ('customer__user__username',)
    readonly_fields = ('created_at', 'updated_at', 'total_items', 'subtotal_display', 'shipping_display', 'total_display')
    
    # Show cart items inline
    inlines = [CartItemInline]
    
    fields = ('customer', 'created_at', 'updated_at', 'total_items', 'subtotal_display', 'shipping_display', 'total_display')
    
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
    list_display = ('id', 'cart', 'book', 'quantity', 'subtotal_display', 'added_at')
    list_filter = ('added_at',)
    search_fields = ('cart__customer__user__username', 'book__title')
    
    # Make quantity editable in list view
    list_editable = ('quantity',)
    
    fields = ('cart', 'book', 'quantity', 'added_at')
    readonly_fields = ('added_at',)
    
    def subtotal_display(self, obj):
        return f"Rs. {obj.subtotal}"
    subtotal_display.short_description = 'Subtotal'