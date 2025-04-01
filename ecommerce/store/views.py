from rest_framework import generics, status
from rest_framework.response import Response
from rest_framework.views import APIView
from .models import Product, Cart, CartItem, Order, Discount
from .serializers import ProductSerializer, CartSerializer, OrderSerializer, DiscountSerializer
import random
import string

class ProductList(generics.ListAPIView):
    queryset = Product.objects.all()
    serializer_class = ProductSerializer

class CartView(APIView):
    def get(self, request):
        user_id = request.query_params.get('user_id')
        try:
            cart = Cart.objects.get(user_id=user_id)
            serializer = CartSerializer(cart)
            return Response(serializer.data)
        except Cart.DoesNotExist:
            return Response({'error': 'Cart not found'}, status=status.HTTP_404_NOT_FOUND)

    def post(self, request):
        user_id = request.data.get('user_id')
        product_id = request.data.get('product_id')
        
        cart, created = Cart.objects.get_or_create(user_id=user_id)
        product = Product.objects.get(id=product_id)
        
        cart_item, created = CartItem.objects.get_or_create(
            cart=cart,
            product=product,
            defaults={'quantity': 1}
        )
        
        if not created:
            cart_item.quantity += 1
            cart_item.save()
        
        serializer = CartSerializer(cart)
        return Response(serializer.data)

class CheckoutView(APIView):
    def post(self, request):
        user_id = request.data.get('user_id')
        discount_code = request.data.get('discount_code')
        
        try:
            cart = Cart.objects.get(user_id=user_id)
            
            # Process discount if provided
            discount = None
            if discount_code:
                try:
                    discount = Discount.objects.get(code=discount_code, is_used=False)
                except Discount.DoesNotExist:
                    return Response({'error': 'Invalid discount code'}, status=status.HTTP_400_BAD_REQUEST)
            
            # Calculate totals
            total = cart.total
            discount_amount = 0
            if discount:
                discount_amount = total * (discount.percentage / 100)
                discount.is_used = True
                discount.save()
            
            final_amount = total - discount_amount
            
            # Create order
            order = Order.objects.create(
                cart=cart,
                total=total,
                discount_amount=discount_amount,
                final_amount=final_amount
            )
            
            # Generate new discount if this is nth order
            if Order.objects.count() % 5 == 0:  # Every 5th order
                self.generate_discount()
            
            serializer = OrderSerializer(order)
            return Response(serializer.data, status=status.HTTP_201_CREATED)
            
        except Cart.DoesNotExist:
            return Response({'error': 'Cart not found'}, status=status.HTTP_404_NOT_FOUND)
    
    def generate_discount(self):
        code = ''.join(random.choices(string.ascii_uppercase + string.digits, k=8))
        Discount.objects.create(code=code, percentage=10)

class GenerateDiscountView(APIView):
    def post(self, request):
        code = ''.join(random.choices(string.ascii_uppercase + string.digits, k=8))
        discount = Discount.objects.create(code=code, percentage=10)
        serializer = DiscountSerializer(discount)
        return Response(serializer.data, status=status.HTTP_201_CREATED)

class StatsView(APIView):
    def get(self, request):
        stats = {
            'total_orders': Order.objects.count(),
            'total_sales': sum(order.final_amount for order in Order.objects.all()),
            'total_discounts': Discount.objects.count(),
            'total_discount_amount': sum(order.discount_amount for order in Order.objects.all()),
            'active_discounts': DiscountSerializer(
                Discount.objects.filter(is_used=False),
                many=True
            ).data
        }
        return Response(stats)