from django.db import models

class Product(models.Model):
    name = models.CharField(max_length=255)
    price = models.DecimalField(max_digits=10, decimal_places=2)
    description = models.TextField(blank=True)
    
    def __str__(self):
        return self.name

class Discount(models.Model):
    code = models.CharField(max_length=20, unique=True)
    percentage = models.DecimalField(max_digits=5, decimal_places=2, default=10.00)
    is_used = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    used_at = models.DateTimeField(null=True, blank=True)
    
    def __str__(self):
        return f"{self.code} ({'used' if self.is_used else 'active'})"

class Cart(models.Model):
    user_id = models.CharField(max_length=100)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    discount = models.ForeignKey(Discount, null=True, blank=True, on_delete=models.SET_NULL)
    
    @property
    def total(self):
        return sum(item.subtotal for item in self.items.all())

class CartItem(models.Model):
    cart = models.ForeignKey(Cart, related_name='items', on_delete=models.CASCADE)
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    quantity = models.PositiveIntegerField(default=1)
    
    @property
    def subtotal(self):
        return self.product.price * self.quantity

class Order(models.Model):
    cart = models.OneToOneField(Cart, on_delete=models.PROTECT)
    total = models.DecimalField(max_digits=10, decimal_places=2)
    discount_amount = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    final_amount = models.DecimalField(max_digits=10, decimal_places=2)
    created_at = models.DateTimeField(auto_now_add=True)