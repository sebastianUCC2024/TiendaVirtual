from rest_framework import generics, status
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework.parsers import MultiPartParser, FormParser
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework.filters import SearchFilter, OrderingFilter

from .models import Category, Product, ProductVariant
from .serializers import (
    CategorySerializer, ProductListSerializer,
    ProductDetailSerializer, ProductVariantSerializer, ProductImageSerializer
)
from .services import CategoryService, ProductService
from apps.users.permissions import IsAdminUser


class CategoryListCreateView(generics.ListCreateAPIView):
    serializer_class = CategorySerializer

    def get_permissions(self):
        if self.request.method == 'GET':
            return [AllowAny()]
        return [IsAdminUser()]

    def get_queryset(self):
        return CategoryService.get_active_tree()


class CategoryDetailView(generics.RetrieveUpdateDestroyAPIView):
    queryset = Category.objects.all()
    serializer_class = CategorySerializer

    def get_permissions(self):
        if self.request.method == 'GET':
            return [AllowAny()]
        return [IsAdminUser()]

    def destroy(self, request, *args, **kwargs):
        instance = self.get_object()
        CategoryService.soft_delete(instance)
        return Response(status=status.HTTP_204_NO_CONTENT)


class ProductListView(generics.ListAPIView):
    serializer_class = ProductListSerializer
    permission_classes = (AllowAny,)
    filter_backends = (DjangoFilterBackend, SearchFilter, OrderingFilter)
    filterset_fields = ('category__slug', 'is_featured', 'is_active')
    search_fields = ('name', 'description', 'sku')
    ordering_fields = ('price', 'created_at', 'name')
    ordering = ('-created_at',)

    def get_queryset(self):
        return ProductService.get_active_products()


class ProductCreateView(generics.CreateAPIView):
    serializer_class = ProductDetailSerializer
    permission_classes = (IsAdminUser,)

    def perform_create(self, serializer):
        ProductService.create_product(serializer.validated_data)


class ProductDetailView(generics.RetrieveUpdateAPIView):
    queryset = Product.objects.filter(is_active=True)
    lookup_field = 'slug'

    def get_permissions(self):
        if self.request.method == 'GET':
            return [AllowAny()]
        return [IsAdminUser()]

    def get_serializer_class(self):
        if self.request.method == 'GET':
            return ProductDetailSerializer
        return ProductDetailSerializer


class ProductImageUploadView(APIView):
    permission_classes = (IsAdminUser,)
    parser_classes = (MultiPartParser, FormParser)

    def post(self, request, pk):
        try:
            product = Product.objects.get(pk=pk)
        except Product.DoesNotExist:
            return Response({'detail': 'Producto no encontrado.'}, status=status.HTTP_404_NOT_FOUND)

        image = ProductService.add_image(
            product=product,
            image_file=request.FILES.get('image'),
            alt_text=request.data.get('alt_text', ''),
            is_primary=request.data.get('is_primary', False),
        )
        return Response(ProductImageSerializer(image).data, status=status.HTTP_201_CREATED)


class ProductVariantView(generics.ListCreateAPIView):
    serializer_class = ProductVariantSerializer
    permission_classes = (IsAdminUser,)

    def get_queryset(self):
        return ProductVariant.objects.filter(product_id=self.kwargs['pk'])

    def perform_create(self, serializer):
        product = Product.objects.get(pk=self.kwargs['pk'])
        serializer.save(product=product)


class StockUpdateView(APIView):
    permission_classes = (IsAdminUser,)

    def patch(self, request, variant_id):
        quantity = request.data.get('quantity')
        if quantity is None:
            return Response({'detail': 'Campo quantity requerido.'}, status=status.HTTP_400_BAD_REQUEST)
        variant = ProductService.update_variant_stock(variant_id, int(quantity))
        return Response(ProductVariantSerializer(variant).data)
