from django.db import models
from django.conf import settings


class Address(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='addresses')
    full_name = models.CharField(max_length=150)
    phone = models.CharField(max_length=20)
    address_line = models.CharField(max_length=255)
    city = models.CharField(max_length=100)
    department = models.CharField(max_length=100)
    country = models.CharField(max_length=100, default='Colombia')
    postal_code = models.CharField(max_length=20, blank=True)
    reference = models.TextField(blank=True)
    is_default = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'addresses'
        verbose_name = 'Dirección'
        verbose_name_plural = 'Direcciones'

    def save(self, *args, **kwargs):
        # Solo una dirección puede ser default por usuario
        if self.is_default:
            Address.objects.filter(user=self.user, is_default=True).update(is_default=False)
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.full_name} - {self.city}, {self.department}"
