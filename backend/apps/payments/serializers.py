from rest_framework import serializers
from .models import Payment, Transaction


class PaymentSerializer(serializers.ModelSerializer):
    status_display = serializers.CharField(source='get_status_display', read_only=True)

    class Meta:
        model = Payment
        fields = (
            'id', 'provider', 'payment_intent_id', 'client_secret',
            'amount', 'currency', 'status', 'status_display', 'created_at'
        )
        read_only_fields = fields


class CreatePaymentIntentSerializer(serializers.Serializer):
    order_id = serializers.IntegerField()
    provider = serializers.ChoiceField(choices=['stripe'], default='stripe')


class PaymentIntentResponseSerializer(serializers.Serializer):
    """Lo que se devuelve al frontend para que complete el pago."""
    payment_id = serializers.IntegerField()
    client_secret = serializers.CharField()
    payment_intent_id = serializers.CharField()
    amount = serializers.DecimalField(max_digits=10, decimal_places=2)
    currency = serializers.CharField()
    publishable_key = serializers.CharField()
