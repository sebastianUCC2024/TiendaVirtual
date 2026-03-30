from rest_framework import serializers
from .models import Coupon


class CouponSerializer(serializers.ModelSerializer):
    class Meta:
        model = Coupon
        fields = (
            'id', 'code', 'discount_type', 'discount_value',
            'min_order_amount', 'max_uses', 'used_count',
            'valid_from', 'valid_until', 'is_active'
        )
        read_only_fields = ('id', 'used_count')


class CouponValidateSerializer(serializers.Serializer):
    """Para que el cliente valide un cupón antes del checkout."""
    code = serializers.CharField()
    order_amount = serializers.DecimalField(max_digits=10, decimal_places=2)
