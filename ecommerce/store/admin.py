from django.contrib import admin
from .models import Product, Discount, Cart, CartItem, Order
from django.utils.html import format_html
from django.urls import reverse
from django.db.models import Sum, F

@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = ('name', 'formatted_price', 'description_short', 'created_at')
    search_fields = ('name', 'description')
    list_filter = ('created_at',)
    ordering = ('-created_at',)
    
    def formatted_price(self, obj):
        return f"${obj.price:.2f}"
    formatted_price.short_description = 'Price'
    
    def description_short(self, obj):
        return obj.description[:50] + '...' if len(obj.description) > 50 else obj.description
    description_short.short_description = 'Description'

@admin.register(Discount)
class DiscountAdmin(admin.ModelAdmin):
    list_display = ('code', 'percentage', 'is_used', 'created_at', 'used_at')
    list_filter = ('is_used', 'created_at')
    readonly_fields = ('created_at',)
    actions = ['generate_discount_codes']
    
    @admin.action(description='Generate new discount codes')
    def generate_discount_codes(self, request, queryset):
        import random
        import string
        for _ in range(5):  # Generate 5 codes at once
            code = ''.join(random.choices(string.ascii_uppercase + string.digits, k=8))
            Discount.objects.create(code=code, percentage=10)
        self.message_user(request, "5 new discount codes generated")

class CartItemInline(admin.TabularInline):
    model = CartItem
    extra = 1
    fields = ('product', 'quantity', 'subtotal')
    readonly_fields = ('subtotal',)
    
    def subtotal(self, instance):
        return instance.product.price * instance.quantity

@admin.register(Cart)
class CartAdmin(admin.ModelAdmin):
    list_display = ('user_id', 'item_count', 'cart_total', 'discount_applied', 'created_at')
    inlines = [CartItemInline]
    readonly_fields = ('created_at', 'updated_at')
    
    def item_count(self, obj):
        return obj.items.count()
    item_count.short_description = 'Items'
    
    def cart_total(self, obj):
        total = obj.items.aggregate(
            total=Sum(F('product__price') * F('quantity'))
        )['total'] or 0
        return f"${total:.2f}"
    cart_total.short_description = 'Total'
    
    def discount_applied(self, obj):
        return obj.discount.code if obj.discount else "None"
    discount_applied.short_description = 'Discount'

@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    list_display = ('id', 'user_id', 'order_total', 'discount_amount', 'final_amount', 'created_at')
    readonly_fields = ('created_at',)
    list_filter = ('created_at',)
    
    def user_id(self, obj):
        return obj.cart.user_id
    user_id.short_description = 'User ID'
    
    def order_total(self, obj):
        return f"${obj.total:.2f}"
    order_total.short_description = 'Total'
    
    def discount_amount(self, obj):
        return f"-${obj.discount_amount:.2f}" if obj.discount_amount else "None"
    discount_amount.short_description = 'Discount'
    
    def final_amount(self, obj):
        return f"${obj.final_amount:.2f}"
    final_amount.short_description = 'Final Amount'