from django.db import models
from django.conf import settings
import uuid


class Product(models.Model):
    name = models.CharField(max_length=255, verbose_name="Ürün Adı")
    slug = models.SlugField(max_length=255, unique=True, verbose_name="URL Slug")
    brand = models.CharField(max_length=100, default="SIDREX®", verbose_name="Marka")
    price = models.CharField(max_length=50, verbose_name="Fiyat")  # ₺820.00 formatında
    original_price = models.CharField(max_length=50, null=True, blank=True, verbose_name="Eski Fiyat")
    rating = models.IntegerField(default=5, verbose_name="Puan")
    review_count = models.IntegerField(default=0, verbose_name="Değerlendirme Sayısı")
    description = models.TextField(verbose_name="Açıklama")
    ingredients = models.TextField(verbose_name="İçerik")
    usage = models.TextField(verbose_name="Kullanım")
    warnings = models.TextField(verbose_name="Uyarılar")
    bg_color = models.CharField(max_length=50, default="bg-gray-50", verbose_name="Arka Plan Rengi")
    is_active = models.BooleanField(default=True, verbose_name="Aktif")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "Ürün"
        verbose_name_plural = "Ürünler"
        ordering = ['name']

    def __str__(self):
        return self.name

    @property
    def primary_image(self):
        """Ana resmi döndürür"""
        primary = self.images.filter(is_primary=True).first()
        return primary if primary else self.images.first()


class ProductFeature(models.Model):
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name='features')
    feature = models.CharField(max_length=255, verbose_name="Özellik")
    order = models.IntegerField(default=0, verbose_name="Sıra")

    class Meta:
        verbose_name = "Ürün Özelliği"
        verbose_name_plural = "Ürün Özellikleri"
        ordering = ['order']

    def __str__(self):
        return f"{self.product.name} - {self.feature}"


class ProductImage(models.Model):
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name='images')
    supabase_path = models.CharField(max_length=1024, verbose_name="Supabase Yolu")
    is_primary = models.BooleanField(default=False, verbose_name="Ana Resim")
    order = models.IntegerField(default=0, verbose_name="Sıra")
    alt_text = models.CharField(max_length=255, blank=True, verbose_name="Alt Metin")

    class Meta:
        verbose_name = "Ürün Resmi"
        verbose_name_plural = "Ürün Resimleri"
        ordering = ['order']

    def __str__(self):
        return f"{self.product.name} - Resim {self.order}"

    @property
    def public_url(self):
        if not self.supabase_path:
            return None
        return f"{settings.SUPABASE_URL}/storage/v1/object/public/{settings.SUPABASE_BUCKET_NAME}/{self.supabase_path}"


class ProductReview(models.Model):
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name='reviews')
    name = models.CharField(max_length=100, verbose_name="İsim")
    rating = models.IntegerField(verbose_name="Puan")
    comment = models.TextField(verbose_name="Yorum")
    date = models.CharField(max_length=50, verbose_name="Tarih")  # "15 Ocak 2024" formatında
    order = models.IntegerField(default=0, verbose_name="Sıra")

    class Meta:
        verbose_name = "Ürün Yorumu"
        verbose_name_plural = "Ürün Yorumları"
        ordering = ['order']

    def __str__(self):
        return f"{self.product.name} - {self.name} ({self.rating}★)"
