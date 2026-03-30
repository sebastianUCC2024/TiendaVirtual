from django.db import models


class Payment(models.Model):
    class Status(models.TextChoices):
        PENDING = 'pending', 'Pendiente'
        PROCESSING = 'processing', 'Procesando'
        APPROVED = 'approved', 'Aprobado'
        REJECTED = 'rejected', 'Rechazado'
        REFUNDED = 'refunded', 'Reembolsado'

    class Provider(models.TextChoices):
        STRIPE = 'stripe', 'Stripe'

    order = models.OneToOneField('orders.Order', on_delete=models.CASCADE, related_name='payment')
    provider = models.CharField(max_length=20, choices=Provider.choices, default=Provider.STRIPE)
    payment_intent_id = models.CharField(max_length=200, blank=True)
    client_secret = models.CharField(max_length=500, blank=True)
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    currency = models.CharField(max_length=3, default='COP')
    status = models.CharField(max_length=20, choices=Status.choices, default=Status.PENDING)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'payments'
        verbose_name = 'Pago'
        verbose_name_plural = 'Pagos'

    def __str__(self):
        return f"Pago {self.order.order_number} - {self.status}"


class Transaction(models.Model):
    class EventType(models.TextChoices):
        CREATED = 'created', 'Creado'
        CONFIRMED = 'confirmed', 'Confirmado'
        FAILED = 'failed', 'Fallido'
        REFUNDED = 'refunded', 'Reembolsado'
        WEBHOOK = 'webhook', 'Webhook'

    payment = models.ForeignKey(Payment, on_delete=models.CASCADE, related_name='transactions')
    event_type = models.CharField(max_length=20, choices=EventType.choices)
    provider_event_id = models.CharField(max_length=200, blank=True)
    raw_response = models.JSONField(default=dict)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'transactions'
        ordering = ['-created_at']
