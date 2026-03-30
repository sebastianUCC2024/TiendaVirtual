from django.urls import path
from .views import CartView, CartItemAddView, CartItemDetailView

urlpatterns = [
    path('', CartView.as_view(), name='cart'),
    path('items/', CartItemAddView.as_view(), name='cart_item_add'),
    path('items/<int:item_id>/', CartItemDetailView.as_view(), name='cart_item_detail'),
]
