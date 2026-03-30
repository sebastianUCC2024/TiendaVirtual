from django.contrib import admin
from .models import Order, OrderItem


class OrderItemInline(admin.TabularInline):
    model = OrderItem
    extra = 0
    readonly_fields = ('product_name', 'variant_detail', 'unit_price', 'quantity', 'total_price')


@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    list_display = ('order_number', 'user', 'status', 'total', 'created_at')
    list_filter = ('status',)
    search_fields = ('order_number', 'user__email')
    readonly_fields = ('order_number', 'subtotal', 'discount_amount', 'total', 'created_at')
    inlines = (OrderItemInline,)
    ordering = ('-created_at',)
