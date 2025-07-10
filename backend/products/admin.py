from django.contrib import admin
from .models import Product, ProductImage, ProductFeature, ProductReview


class ProductImageInline(admin.TabularInline):
    model = ProductImage
    extra = 1
    readonly_fields = ('public_url',)


class ProductFeatureInline(admin.TabularInline):
    model = ProductFeature
    extra = 1


class ProductReviewInline(admin.TabularInline):
    model = ProductReview
    extra = 1


@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = ('name', 'slug', 'brand', 'price', 'rating', 'review_count', 'is_active')
    list_filter = ('brand', 'is_active', 'rating')
    search_fields = ('name', 'slug', 'description')
    prepopulated_fields = {'slug': ('name',)}
    inlines = [ProductImageInline, ProductFeatureInline, ProductReviewInline]
    
    fieldsets = (
        ('Temel Bilgiler', {
            'fields': ('name', 'slug', 'brand', 'price', 'original_price')
        }),
        ('Değerlendirme', {
            'fields': ('rating', 'review_count')
        }),
        ('İçerik', {
            'fields': ('description', 'ingredients', 'usage', 'warnings')
        }),
        ('Görünüm', {
            'fields': ('bg_color', 'is_active')
        }),
    )


@admin.register(ProductImage)
class ProductImageAdmin(admin.ModelAdmin):
    list_display = ('product', 'is_primary', 'order', 'alt_text')
    list_filter = ('is_primary', 'product')
    readonly_fields = ('public_url',)


@admin.register(ProductFeature)
class ProductFeatureAdmin(admin.ModelAdmin):
    list_display = ('product', 'feature', 'order')
    list_filter = ('product',)


@admin.register(ProductReview)
class ProductReviewAdmin(admin.ModelAdmin):
    list_display = ('product', 'name', 'rating', 'date', 'order')
    list_filter = ('product', 'rating')
    search_fields = ('name', 'comment')
