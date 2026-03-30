from django.db import models
from django.utils import timezone


class Coupon(models.Model):
    class DiscountType(models.TextChoices):
        PERCENTAGE = 'percentage', 'Porcentaje'
        FIXED = 'fixed', 'Valor fijo'

    code = models.CharField(max_length=50, unique=True)
    discount_type = models.CharField(max_length=15, choices=DiscountType.choices)
    discount_value = models.DecimalField(max_digits=10, decimal_places=2)
    min_order_amount = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    max_uses = models.PositiveIntegerField(null=True, blank=True)
    used_count = models.PositiveIntegerField(default=0)
    valid_from = models.DateTimeField()
    valid_until = models.DateTimeField()
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'coupons'
        verbose_name = 'Cupón'
        verbose_name_plural = 'Cupones'

    def is_valid(self):
        now = timezone.now()
        if not self.is_active:
            return False
        if now < self.valid_from or now > self.valid_until:
            return False
        if self.max_uses and self.used_count >= self.max_uses:
            return False
        return True

    def calculate_discount(self, amount):
        if self.discount_type == self.DiscountType.PERCENTAGE:
            return (amount * self.discount_value / 100).quantize(amount)
        return min(self.discount_value, amount)

    def __str__(self):
        return self.code
