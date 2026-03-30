from django.contrib import admin
from .models import Payment, Transaction


class TransactionInline(admin.TabularInline):
    model = Transaction
    extra = 0
    readonly_fields = ('event_type', 'provider_event_id', 'created_at')


@admin.register(Payment)
class PaymentAdmin(admin.ModelAdmin):
    list_display = ('order', 'provider', 'amount', 'currency', 'status', 'created_at')
    list_filter = ('status', 'provider')
    search_fields = ('order__order_number', 'payment_intent_id')
    readonly_fields = ('payment_intent_id', 'client_secret', 'created_at', 'updated_at')
    inlines = (TransactionInline,)
