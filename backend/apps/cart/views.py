from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import IsAuthenticated

from .serializers import CartSerializer, CartItemAddSerializer, CartItemUpdateSerializer
from .services import CartService
from .exceptions import InsufficientStockError


class CartView(APIView):
    permission_classes = (IsAuthenticated,)

    def get(self, request):
        cart = CartService.get_or_create_cart(request.user)
        return Response(CartSerializer(cart).data)

    def delete(self, request):
        CartService.clear_cart(request.user)
        return Response(status=status.HTTP_204_NO_CONTENT)


class CartItemAddView(APIView):
    permission_classes = (IsAuthenticated,)

    def post(self, request):
        serializer = CartItemAddSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        d = serializer.validated_data
        try:
            item = CartService.add_item(
                user=request.user,
                product_id=d['product_id'],
                quantity=d['quantity'],
                variant_id=d.get('variant_id'),
            )
        except InsufficientStockError as e:
            return Response({'detail': str(e)}, status=status.HTTP_400_BAD_REQUEST)

        cart = CartService.get_or_create_cart(request.user)
        return Response(CartSerializer(cart).data, status=status.HTTP_201_CREATED)


class CartItemDetailView(APIView):
    permission_classes = (IsAuthenticated,)

    def patch(self, request, item_id):
        serializer = CartItemUpdateSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        try:
            CartService.update_item(request.user, item_id, serializer.validated_data['quantity'])
        except InsufficientStockError as e:
            return Response({'detail': str(e)}, status=status.HTTP_400_BAD_REQUEST)
        cart = CartService.get_or_create_cart(request.user)
        return Response(CartSerializer(cart).data)

    def delete(self, request, item_id):
        CartService.remove_item(request.user, item_id)
        return Response(status=status.HTTP_204_NO_CONTENT)
