from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static

API_V1 = 'api/v1/'

urlpatterns = [
    path('admin/', admin.site.urls),
    path(API_V1 + 'auth/', include('apps.users.urls')),
    path(API_V1 + 'catalog/', include('apps.products.urls')),
    path(API_V1 + 'cart/', include('apps.cart.urls')),
    path(API_V1 + 'orders/', include('apps.orders.urls')),
    path(API_V1 + 'payments/', include('apps.payments.urls')),
    path(API_V1 + 'addresses/', include('apps.addresses.urls')),
    path(API_V1 + 'coupons/', include('apps.coupons.urls')),
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
