from rest_framework.views import APIView
from rest_framework import generics, status
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated

from .serializers import OrderSerializer, CheckoutSerializer, OrderStatusUpdateSerializer
from .services import OrderService
from .exceptions import EmptyCartError
from apps.users.permissions import IsAdminUser


class CheckoutView(APIView):
    permission_classes = (IsAuthenticated,)

    def post(self, request):
        serializer = CheckoutSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        d = serializer.validated_data
        try:
            order = OrderService.create_from_cart(
                user=request.user,
                address_id=d['address_id'],
                coupon_code=d.get('coupon_code', ''),
                notes=d.get('notes', ''),
                payment_provider=d.get('payment_provider', 'stripe'),
            )
        except EmptyCartError as e:
            return Response({'detail': str(e)}, status=status.HTTP_400_BAD_REQUEST)
        return Response(OrderSerializer(order).data, status=status.HTTP_201_CREATED)


class OrderListView(generics.ListAPIView):
    serializer_class = OrderSerializer
    permission_classes = (IsAuthenticated,)

    def get_queryset(self):
        return OrderService.get_user_orders(self.request.user)


class OrderDetailView(APIView):
    permission_classes = (IsAuthenticated,)

    def get(self, request, order_id):
        order = OrderService.get_order_detail(request.user, order_id)
        return Response(OrderSerializer(order).data)


# Admin
class AdminOrderListView(generics.ListAPIView):
    serializer_class = OrderSerializer
    permission_classes = (IsAdminUser,)

    def get_queryset(self):
        from .models import Order
        return Order.objects.all().select_related('user', 'address').prefetch_related('items').order_by('-created_at')


class AdminOrderStatusView(APIView):
    permission_classes = (IsAdminUser,)

    def patch(self, request, order_id):
        from .models import Order
        try:
            order = Order.objects.get(id=order_id)
        except Order.DoesNotExist:
            return Response({'detail': 'Pedido no encontrado.'}, status=status.HTTP_404_NOT_FOUND)
        serializer = OrderStatusUpdateSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        order = OrderService.update_status(order, serializer.validated_data['status'])
        return Response(OrderSerializer(order).data)
