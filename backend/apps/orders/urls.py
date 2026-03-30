from django.urls import path
from .views import (
    CheckoutView, OrderListView, OrderDetailView,
    AdminOrderListView, AdminOrderStatusView
)

urlpatterns = [
    path('checkout/', CheckoutView.as_view(), name='checkout'),
    path('', OrderListView.as_view(), name='order_list'),
    path('<int:order_id>/', OrderDetailView.as_view(), name='order_detail'),
    # Admin
    path('admin/', AdminOrderListView.as_view(), name='admin_order_list'),
    path('admin/<int:order_id>/status/', AdminOrderStatusView.as_view(), name='admin_order_status'),
]
