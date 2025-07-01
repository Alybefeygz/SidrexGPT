from rest_framework import serializers
from django.contrib.auth.models import User


class CustomUserDetailsSerializer(serializers.ModelSerializer):
    """
    Custom user serializer for dj_rest_auth that includes admin fields and brand information
    """
    brand_id = serializers.SerializerMethodField()
    brand_name = serializers.SerializerMethodField()
    brand_package_type = serializers.SerializerMethodField()
    
    class Meta:
        model = User
        fields = ['pk', 'username', 'email', 'first_name', 'last_name', 'is_staff', 'is_superuser', 'is_active', 'brand_id', 'brand_name', 'brand_package_type']
        read_only_fields = ['pk', 'username', 'is_staff', 'is_superuser', 'is_active', 'brand_id', 'brand_name', 'brand_package_type']
    
    def get_brand_id(self, obj):
        """Kullanıcının brand ID'sini döndür"""
        if hasattr(obj, 'profil') and obj.profil.brand:
            return obj.profil.brand.id
        return None
    
    def get_brand_name(self, obj):
        """Kullanıcının brand adını döndür"""
        if hasattr(obj, 'profil') and obj.profil.brand:
            return obj.profil.brand.name
        return None
    
    def get_brand_package_type(self, obj):
        """Kullanıcının brand paket türünü döndür"""
        if hasattr(obj, 'profil') and obj.profil.brand:
            return obj.profil.brand.paket_turu
        return None 