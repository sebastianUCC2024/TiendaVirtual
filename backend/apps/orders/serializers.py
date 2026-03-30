from rest_framework import serializers
from .models import Order, OrderItem
from apps.addresses.serializers import AddressSerializer


class OrderItemSerializer(serializers.ModelSerializer):
    class Meta:
        model = OrderItem
        fields = ('id', 'product', 'variant', 'product_name', 'variant_detail',
                  'unit_price', 'quantity', 'total_price')


class OrderSerializer(serializers.ModelSerializer):
    items = OrderItemSerializer(many=True, read_only=True)
    address = AddressSerializer(read_only=True)
    status_display = serializers.CharField(source='get_status_display', read_only=True)

    class Meta:
        model = Order
        fields = (
            'id', 'order_number', 'status', 'status_display',
            'address', 'subtotal', 'discount_amount', 'total',
            'items', 'notes', 'created_at', 'updated_at'
        )
        read_only_fields = fields


class CheckoutSerializer(serializers.Serializer):
    address_id = serializers.IntegerField()
    coupon_code = serializers.CharField(required=False, allow_blank=True)
    notes = serializers.CharField(required=False, allow_blank=True)
    payment_provider = serializers.ChoiceField(choices=['stripe'], default='stripe')


class OrderStatusUpdateSerializer(serializers.Serializer):
    status = serializers.ChoiceField(choices=Order.Status.choices)
