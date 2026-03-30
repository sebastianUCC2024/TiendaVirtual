from django.urls import path
from .views import (
    CategoryListCreateView, CategoryDetailView,
    ProductListView, ProductCreateView, ProductDetailView,
    ProductImageUploadView, ProductVariantView, StockUpdateView
)

urlpatterns = [
    # Categorías
    path('categories/', CategoryListCreateView.as_view(), name='category_list'),
    path('categories/<int:pk>/', CategoryDetailView.as_view(), name='category_detail'),

    # Productos
    path('products/', ProductListView.as_view(), name='product_list'),
    path('products/create/', ProductCreateView.as_view(), name='product_create'),
    path('products/<slug:slug>/', ProductDetailView.as_view(), name='product_detail'),
    path('products/<int:pk>/images/', ProductImageUploadView.as_view(), name='product_images'),
    path('products/<int:pk>/variants/', ProductVariantView.as_view(), name='product_variants'),

    # Stock
    path('variants/<int:variant_id>/stock/', StockUpdateView.as_view(), name='stock_update'),
]
