from django.urls import path
from .views import AddressListCreateView, AddressDetailView, SetDefaultAddressView

urlpatterns = [
    path('', AddressListCreateView.as_view(), name='address_list'),
    path('<int:pk>/', AddressDetailView.as_view(), name='address_detail'),
    path('<int:pk>/set-default/', SetDefaultAddressView.as_view(), name='address_set_default'),
]
