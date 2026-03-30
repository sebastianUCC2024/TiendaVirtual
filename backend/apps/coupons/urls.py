from django.urls import path
from .views import CouponAdminView, CouponAdminDetailView, ValidateCouponView

urlpatterns = [
    path('', CouponAdminView.as_view(), name='coupon_list'),
    path('<int:pk>/', CouponAdminDetailView.as_view(), name='coupon_detail'),
    path('validate/', ValidateCouponView.as_view(), name='coupon_validate'),
]
