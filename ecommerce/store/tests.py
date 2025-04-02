from django.test import TestCase
from django.contrib.admin.sites import AdminSite
from django.contrib.auth import get_user_model
from django.urls import reverse
from django.test import RequestFactory

from store.models import Product, Discount, Cart, CartItem, Order
from store.admin import ProductAdmin, DiscountAdmin, CartAdmin, OrderAdmin

User = get_user_model()

class ModelTests(TestCase):
    @classmethod
    def setUpTestData(cls):
        # Create test data that will be used by all test methods
        cls.product = Product.objects.create(
            name="Test Product",
            price=99.99,
            description="Test description"
        )
        cls.discount = Discount.objects.create(
            code="TEST10",
            percentage=10.00
        )
        cls.user_id = "test_user_123"
        cls.cart = Cart.objects.create(user_id=cls.user_id)
        cls.cart_item = CartItem.objects.create(
            cart=cls.cart,
            product=cls.product,
            quantity=2
        )
        cls.order = Order.objects.create(
            cart=cls.cart,
            total=199.98,
            discount_amount=19.998,
            final_amount=179.982
        )

    def test_product_creation(self):
        self.assertEqual(self.product.name, "Test Product")
        self.assertEqual(str(self.product), "Test Product")
        self.assertEqual(self.product.price, 99.99)

    def test_discount_creation(self):
        self.assertEqual(self.discount.code, "TEST10")
        self.assertEqual(self.discount.percentage, 10.00)
        self.assertFalse(self.discount.is_used)

    def test_cart_relationships(self):
        self.assertEqual(self.cart.user_id, self.user_id)
        self.assertEqual(self.cart.items.count(), 1)
        self.assertEqual(self.cart_item.subtotal, 99.99 * 2)

    def test_order_calculations(self):
        self.assertAlmostEqual(self.order.total, 199.98, places=2)
        self.assertAlmostEqual(self.order.discount_amount, 19.998, places=3)
        self.assertAlmostEqual(self.order.final_amount, 179.982, places=3)

    def test_discount_str_method(self):
        self.assertEqual(str(self.discount), "TEST10")

    def test_cart_item_str_method(self):
        self.assertEqual(str(self.cart_item), "2x Test Product")


class AdminTests(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.site = AdminSite()
        cls.superuser = User.objects.create_superuser(
            username='admin',
            password='admin123',
            email='admin@example.com'
        )
        cls.factory = RequestFactory()
        
        # Create test data
        cls.product = Product.objects.create(
            name="Admin Product",
            price=49.99,
            description="Admin test description"
        )
        cls.discount = Discount.objects.create(code="ADMIN10")
        cls.cart = Cart.objects.create(user_id="admin_test_user")
        CartItem.objects.create(
            cart=cls.cart,
            product=cls.product,
            quantity=3
        )

    def test_product_admin(self):
        product_admin = ProductAdmin(Product, self.site)
        
        # Test list_display
        self.assertEqual(
            list(product_admin.get_list_display(None)),
            ['name', 'formatted_price', 'description_short', 'created_at']
        )
        
        # Test search_fields
        self.assertEqual(
            product_admin.search_fields,
            ('name', 'description')
        )
        
        # Test custom methods
        self.assertEqual(
            product_admin.formatted_price(self.product),
            "$49.99"
        )
        self.assertTrue(
            product_admin.description_short(self.product).startswith("Admin test")
        )

    def test_discount_admin_actions(self):
        discount_admin = DiscountAdmin(Discount, self.site)
        
        # Test action
        request = self.factory.get('/admin/store/discount/')
        request.user = self.superuser
        queryset = Discount.objects.all()
        
        # Test generate_discount_codes action
        discount_admin.generate_discount_codes(request, queryset)
        self.assertEqual(Discount.objects.count(), 6)  # 1 existing + 5 new
        
        # Test list display
        self.assertIn('is_used', discount_admin.list_display)

    def test_cart_admin(self):
        cart_admin = CartAdmin(Cart, self.site)
        
        # Test inlines
        self.assertEqual(len(cart_admin.inlines), 1)
        self.assertEqual(cart_admin.inlines[0].__name__, "CartItemInline")
        
        # Test custom methods
        self.assertEqual(cart_admin.item_count(self.cart), 1)
        self.assertEqual(cart_admin.cart_total(self.cart), "$149.97")  # 49.99 * 3

    def test_order_admin(self):
        order = Order.objects.create(
            cart=self.cart,
            total=149.97,
            discount_amount=0,
            final_amount=149.97
        )
        order_admin = OrderAdmin(Order, self.site)
        
        # Test list display
        self.assertEqual(
            order_admin.order_total(order),
            "$149.97"
        )
        self.assertEqual(
            order_admin.discount_amount(order),
            "None"
        )


class ViewTests(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.product = Product.objects.create(
            name="View Product",
            price=29.99,
            description="View test description"
        )
        cls.user_id = "test_user_456"
        cls.cart = Cart.objects.create(user_id=cls.user_id)
        cls.discount = Discount.objects.create(code="VIEW10")

    def test_product_list_view(self):
        url = reverse('product-list')
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.data), 1)
        self.assertEqual(response.data[0]['name'], "View Product")

    def test_cart_operations(self):
        # Add to cart
        add_url = reverse('cart')
        response = self.client.post(add_url, {
            'user_id': self.user_id,
            'product_id': self.product.id
        })
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data['items'][0]['product']['name'], "View Product")
        
        # Check cart total
        self.assertEqual(float(response.data['total']), 29.99)

    def test_checkout_process(self):
        # First add item to cart
        self.client.post(reverse('cart'), {
            'user_id': self.user_id,
            'product_id': self.product.id
        })
        
        # Checkout without discount
        checkout_url = reverse('checkout')
        response = self.client.post(checkout_url, {
            'user_id': self.user_id
        })
        self.assertEqual(response.status_code, 201)
        self.assertEqual(float(response.data['total']), 29.99)
        
        # Verify order creation
        self.assertEqual(Order.objects.count(), 1)
        
        # Checkout with invalid discount
        response = self.client.post(checkout_url, {
            'user_id': self.user_id,
            'discount_code': 'INVALID'
        })
        self.assertEqual(response.status_code, 400)
        
        # Checkout with valid discount
        response = self.client.post(checkout_url, {
            'user_id': self.user_id,
            'discount_code': 'VIEW10'
        })
        self.assertEqual(response.status_code, 201)
        self.assertAlmostEqual(float(response.data['discount_amount']), 2.999, places=3)


class BusinessLogicTests(TestCase):
    def test_discount_generation(self):
        # Test that every 5th order generates a discount
        from store.services.order_service import OrderService
        
        service = OrderService()
        user_id = "logic_test_user"
        product = Product.objects.create(name="Logic Product", price=10.00)
        
        for i in range(1, 6):
            cart = Cart.objects.create(user_id=f"{user_id}_{i}")
            CartItem.objects.create(cart=cart, product=product, quantity=1)
            service.process_order(cart)
            
            if i % 5 == 0:
                self.assertTrue(Discount.objects.filter(is_used=False).exists())
            else:
                self.assertFalse(Discount.objects.exists())