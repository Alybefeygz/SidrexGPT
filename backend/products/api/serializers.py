from rest_framework import serializers
from products.models import Product, ProductImage, ProductFeature, ProductReview


class ProductImageSerializer(serializers.ModelSerializer):
    public_url = serializers.ReadOnlyField()

    class Meta:
        model = ProductImage
        fields = ['id', 'supabase_path', 'public_url', 'is_primary', 'order', 'alt_text']


class ProductFeatureSerializer(serializers.ModelSerializer):
    class Meta:
        model = ProductFeature
        fields = ['id', 'feature', 'order']


class ProductReviewSerializer(serializers.ModelSerializer):
    class Meta:
        model = ProductReview
        fields = ['id', 'name', 'rating', 'comment', 'date', 'order']


class ProductListSerializer(serializers.ModelSerializer):
    """Ana sayfa için ürün listesi - daha az detay"""
    primary_image = ProductImageSerializer(read_only=True)

    class Meta:
        model = Product
        fields = [
            'id', 'name', 'slug', 'brand', 'price', 'original_price', 
            'rating', 'review_count', 'bg_color', 'primary_image'
        ]


class ProductDetailSerializer(serializers.ModelSerializer):
    """Ürün detay sayfası için - tüm bilgiler"""
    images = ProductImageSerializer(many=True, read_only=True)
    features = ProductFeatureSerializer(many=True, read_only=True)
    reviews = ProductReviewSerializer(many=True, read_only=True)
    primary_image = ProductImageSerializer(read_only=True)

    class Meta:
        model = Product
        fields = [
            'id', 'name', 'slug', 'brand', 'price', 'original_price',
            'rating', 'review_count', 'description', 'ingredients',
            'usage', 'warnings', 'bg_color', 'is_active',
            'created_at', 'updated_at', 'images', 'features', 
            'reviews', 'primary_image'
        ] 