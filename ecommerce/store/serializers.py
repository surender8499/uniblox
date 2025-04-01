from rest_framework import serializers
from .models import Product, Cart, CartItem, Order, Discount

class ProductSerializer(serializers.ModelSerializer):
    class Meta:
        model = Product
        fields = ['id', 'name', 'price', 'description']

class CartItemSerializer(serializers.ModelSerializer):
    product = ProductSerializer()
    subtotal = serializers.DecimalField(max_digits=10, decimal_places=2, read_only=True)
    
    class Meta:
        model = CartItem
        fields = ['id', 'product', 'quantity', 'subtotal']

class CartSerializer(serializers.ModelSerializer):
    items = CartItemSerializer(many=True, read_only=True)
    total = serializers.DecimalField(max_digits=10, decimal_places=2, read_only=True)
    
    class Meta:
        model = Cart
        fields = ['id', 'user_id', 'items', 'total', 'discount']

class OrderSerializer(serializers.ModelSerializer):
    class Meta:
        model = Order
        fields = ['id', 'total', 'discount_amount', 'final_amount', 'created_at']

class DiscountSerializer(serializers.ModelSerializer):
    class Meta:
        model = Discount
        fields = ['code', 'percentage', 'is_used', 'created_at']