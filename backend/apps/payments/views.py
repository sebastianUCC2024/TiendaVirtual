from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework import status

from .serializers import CreatePaymentIntentSerializer, PaymentIntentResponseSerializer
from .services import PaymentService
from .exceptions import WebhookException


class CreatePaymentIntentView(APIView):
    permission_classes = (IsAuthenticated,)

    def post(self, request):
        serializer = CreatePaymentIntentSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        result = PaymentService.create_payment_intent(
            user=request.user,
            order_id=serializer.validated_data['order_id'],
            provider=serializer.validated_data.get('provider', 'stripe'),
        )
        return Response(PaymentIntentResponseSerializer(result).data, status=status.HTTP_201_CREATED)


class StripeWebhookView(APIView):
    """
    Endpoint público que recibe eventos de Stripe.
    No requiere autenticación JWT — usa firma HMAC de Stripe.
    """
    permission_classes = (AllowAny,)
    authentication_classes = ()  # Sin auth JWT

    def post(self, request):
        payload = request.body
        signature = request.META.get('HTTP_STRIPE_SIGNATURE', '')

        try:
            PaymentService.process_webhook(payload, signature, provider='stripe')
        except Exception as e:
            return Response({'detail': str(e)}, status=status.HTTP_400_BAD_REQUEST)

        return Response({'received': True}, status=status.HTTP_200_OK)
