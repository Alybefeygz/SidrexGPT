from profiller.models import Profil, ProfilDurum
from rest_framework import serializers
from dj_rest_auth.serializers import LoginSerializer as RestAuthLoginSerializer


class CustomLoginSerializer(RestAuthLoginSerializer):
    email = None
    username = serializers.CharField(required=True)
    password = serializers.CharField(style={'input_type': 'password'})


class ProfilSerializer(serializers.ModelSerializer):
    user = serializers.StringRelatedField(read_only = True)
    foto = serializers.ImageField(read_only = True)
    brand = serializers.StringRelatedField(read_only = True)
    brand_id = serializers.SerializerMethodField()
    brand_name = serializers.SerializerMethodField()
    brand_package_type = serializers.SerializerMethodField()
    
    # Kullanıcı oluşturma için gerekli alanlar
    username = serializers.CharField(write_only=True, required=False)
    password = serializers.CharField(write_only=True, required=False, style={'input_type': 'password'})
    email = serializers.EmailField(write_only=True, required=False, allow_blank=True)
    brand_id_input = serializers.CharField(write_only=True, required=False, allow_blank=True, allow_null=True)
    user_type_input = serializers.CharField(write_only=True, required=False, allow_blank=True)
    
    # User auth bilgilerini de döndür
    is_staff = serializers.SerializerMethodField()
    is_superuser = serializers.SerializerMethodField()
    is_active = serializers.SerializerMethodField()
    user_id = serializers.SerializerMethodField()
    
    class Meta:
        model = Profil
        fields = ['id', 'user', 'foto', 'bio', 'brand', 'username', 'password', 'email', 'brand_id_input', 'user_type_input',
                 'brand_id', 'brand_name', 'brand_package_type', 'is_staff', 'is_superuser', 'is_active', 'user_id']

    def to_representation(self, instance):
        """
        Profil nesnesini serialize eder.
        """
        from django.contrib.auth.models import User
        
        # User nesnesi kontrolü - daha güvenli yöntem
        if isinstance(instance, User):
            profil_instance = getattr(instance, 'profil', None)
            if not profil_instance:
                # Eğer kullanıcının profili yoksa, temel kullanıcı bilgilerini döndür.
                return {
                    'id': None,
                    'user': str(instance),
                    'user_id': instance.id,
                    'is_staff': instance.is_staff,
                    'is_superuser': instance.is_superuser,
                    'is_active': instance.is_active,
                    'brand_id': None,
                    'brand_name': None,
                    'brand_package_type': None,
                    'detail': 'Bu kullanıcı için bir profil bulunamadı.'
                }
            instance = profil_instance

        # Profil instance için representation oluştur
        try:
            # ModelSerializer'in `to_representation` metodunu çağır
            representation = super().to_representation(instance)
        except Exception as e:
            print(f"🔍 to_representation error: {str(e)}")
            # Eğer hata olursa manuel olarak temel alanları dön
            representation = {
                'id': instance.id if hasattr(instance, 'id') else None,
                'user': str(instance.user) if hasattr(instance, 'user') else None,
                'foto': instance.foto.url if hasattr(instance, 'foto') and instance.foto else None,
                'bio': instance.bio if hasattr(instance, 'bio') else None,
                'brand': str(instance.brand) if hasattr(instance, 'brand') and instance.brand else None,
            }
        
        # Tüm gerekli alanları manuel olarak ekle
        representation['is_staff'] = self.get_is_staff(instance)
        representation['is_superuser'] = self.get_is_superuser(instance)
        representation['is_active'] = self.get_is_active(instance)
        representation['user_id'] = self.get_user_id(instance)
        representation['brand_id'] = self.get_brand_id(instance)
        representation['brand_name'] = self.get_brand_name(instance)
        representation['brand_package_type'] = self.get_brand_package_type(instance)
        
        return representation
        
    def get_is_staff(self, obj):
        return obj.user.is_staff if obj.user else False
        
    def get_is_superuser(self, obj):
        return obj.user.is_superuser if obj.user else False
        
    def get_is_active(self, obj):
        return obj.user.is_active if obj.user else True
        
    def get_user_id(self, obj):
        return obj.user.id if obj.user else None
        
    def get_brand_id(self, obj):
        return obj.brand.id if obj.brand else None
        
    def get_brand_name(self, obj):
        return obj.brand.name if obj.brand else None
        
    def get_brand_package_type(self, obj):
        return obj.brand.paket_turu if obj.brand else None
    
    def validate_brand_id(self, value):
        """brand_id alanını validate et"""
        if value is None or (isinstance(value, str) and (not value.strip() or value.lower() == 'none')):
            return None
        try:
            return int(value)
        except (ValueError, TypeError):
            raise serializers.ValidationError('Geçersiz marka ID formatı. Sayısal bir değer girilmelidir.')
    
    def validate(self, data):
        """Tüm verileri validate et"""
        print(f"🔍 SERIALIZER - Validate başlangıç data: {data}")
        
        # brand_id_input'u brand_id'ye çevir
        brand_id_input = data.pop('brand_id_input', None)
        if brand_id_input is not None:
            # Eğer liste olarak geldiyse ilk elemanı al
            if isinstance(brand_id_input, (list, tuple)):
                brand_id_input = brand_id_input[0] if brand_id_input else None
            
            try:
                validated_brand_id = self.validate_brand_id(brand_id_input)
                data['brand_id'] = validated_brand_id
                print(f"🔍 SERIALIZER - Brand ID dönüşümü: {brand_id_input} -> {validated_brand_id}")
            except serializers.ValidationError as e:
                raise serializers.ValidationError({'brand_id_input': str(e)})
        
        # user_type_input'u user_type'a çevir
        user_type_input = data.pop('user_type_input', None)
        if user_type_input:
            # Eğer liste olarak geldiyse ilk elemanı al
            if isinstance(user_type_input, (list, tuple)):
                user_type_input = user_type_input[0] if user_type_input else None
            
            if user_type_input not in ['normal', 'admin', 'superadmin']:
                raise serializers.ValidationError({
                    'user_type_input': 'Geçersiz kullanıcı tipi. "normal", "admin" veya "superadmin" olmalıdır.'
                })
            data['user_type'] = user_type_input
            print(f"🔍 SERIALIZER - User type dönüşümü: {user_type_input}")
        
        print(f"🔍 SERIALIZER - Validate sonuç data: {data}")
        return data
        
        
class ProfilFotoSerializer(serializers.ModelSerializer):
    
    class Meta:
        model = Profil
        fields = ['foto']
        
        
class ProfilDurumSerializer(serializers.ModelSerializer):
    user_profil = serializers.StringRelatedField(read_only = True)
    class Meta:
        model = ProfilDurum
        fields = '__all__'