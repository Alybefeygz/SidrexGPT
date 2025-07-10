from rest_framework import generics, status
from rest_framework.response import Response
from rest_framework.permissions import AllowAny
from django.shortcuts import get_object_or_404
from products.models import Product
from .serializers import ProductListSerializer, ProductDetailSerializer


class ProductListView(generics.ListAPIView):
    """
    Tüm aktif ürünleri listeler (ana sayfa için)
    """
    queryset = Product.objects.filter(is_active=True).prefetch_related('images')
    serializer_class = ProductListSerializer
    permission_classes = [AllowAny]
    
    def get_queryset(self):
        return super().get_queryset().order_by('name')


class ProductDetailView(generics.RetrieveAPIView):
    """
    Slug'a göre ürün detayını getirir
    """
    queryset = Product.objects.filter(is_active=True).prefetch_related(
        'images', 'features', 'reviews'
    )
    serializer_class = ProductDetailSerializer
    permission_classes = [AllowAny]
    lookup_field = 'slug'
    
    def get_object(self):
        slug = self.kwargs.get('slug')
        return get_object_or_404(self.get_queryset(), slug=slug) 