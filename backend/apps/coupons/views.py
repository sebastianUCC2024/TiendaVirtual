from rest_framework import generics, status
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated

from .models import Coupon
from .serializers import CouponSerializer, CouponValidateSerializer
from .services import CouponService
from apps.users.permissions import IsAdminUser


class CouponAdminView(generics.ListCreateAPIView):
    queryset = Coupon.objects.all().order_by('-created_at')
    serializer_class = CouponSerializer
    permission_classes = (IsAdminUser,)


class CouponAdminDetailView(generics.RetrieveUpdateDestroyAPIView):
    queryset = Coupon.objects.all()
    serializer_class = CouponSerializer
    permission_classes = (IsAdminUser,)


class ValidateCouponView(APIView):
    permission_classes = (IsAuthenticated,)

    def post(self, request):
        serializer = CouponValidateSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        d = serializer.validated_data
        coupon = CouponService.validate_and_get(d['code'], d['order_amount'])
        discount = CouponService.apply(coupon, d['order_amount'])
        return Response({
            'code': coupon.code,
            'discount_type': coupon.discount_type,
            'discount_value': str(coupon.discount_value),
            'discount_amount': str(discount),
            'final_amount': str(d['order_amount'] - discount),
        })
