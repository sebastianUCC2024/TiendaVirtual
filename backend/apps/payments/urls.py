from django.urls import path
from .views import CreatePaymentIntentView, StripeWebhookView

urlpatterns = [
    path('create-intent/', CreatePaymentIntentView.as_view(), name='create_payment_intent'),
    path('webhook/stripe/', StripeWebhookView.as_view(), name='stripe_webhook'),
]
