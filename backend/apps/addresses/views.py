from rest_framework import generics, status
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated

from .serializers import AddressSerializer
from .services import AddressService


class AddressListCreateView(generics.ListCreateAPIView):
    serializer_class = AddressSerializer
    permission_classes = (IsAuthenticated,)

    def get_queryset(self):
        return AddressService.get_user_addresses(self.request.user)


class AddressDetailView(generics.RetrieveUpdateDestroyAPIView):
    serializer_class = AddressSerializer
    permission_classes = (IsAuthenticated,)

    def get_queryset(self):
        return AddressService.get_user_addresses(self.request.user)

    def destroy(self, request, *args, **kwargs):
        AddressService.delete(request.user, kwargs['pk'])
        return Response(status=status.HTTP_204_NO_CONTENT)


class SetDefaultAddressView(APIView):
    permission_classes = (IsAuthenticated,)

    def patch(self, request, pk):
        address = AddressService.set_default(request.user, pk)
        return Response(AddressSerializer(address).data)
