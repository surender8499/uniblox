from django.urls import path
from .views import (
    ProductList,
    CartView,
    CheckoutView,
    GenerateDiscountView,
    StatsView
)

urlpatterns = [
    path('products/', ProductList.as_view()),
    path('cart/', CartView.as_view()),
    path('checkout/', CheckoutView.as_view()),
    path('admin/discounts/generate/', GenerateDiscountView.as_view()),
    path('admin/stats/', StatsView.as_view()),
]