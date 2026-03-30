from rest_framework import serializers
from .models import Address


class AddressSerializer(serializers.ModelSerializer):
    class Meta:
        model = Address
        fields = (
            'id', 'full_name', 'phone', 'address_line',
            'city', 'department', 'country', 'postal_code',
            'reference', 'is_default', 'created_at'
        )
        read_only_fields = ('id', 'created_at')

    def create(self, validated_data):
        user = self.context['request'].user
        return Address.objects.create(user=user, **validated_data)
