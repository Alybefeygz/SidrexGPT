from rest_framework import generics
from rest_framework.permissions import IsAuthenticated, IsAdminUser
from profiller.models import Profil, ProfilDurum
from profiller.api.serializers import ProfilSerializer, ProfilDurumSerializer, ProfilFotoSerializer
# from rest_framework.viewsets import ReadOnlyModelViewSet
from rest_framework.viewsets import ModelViewSet
from rest_framework.viewsets import GenericViewSet
from rest_framework import mixins
from rest_framework.decorators import action

from profiller.api.permissions import KendiProfiliYaDaReadOnly, DurumSahibiYaDaReadOnly

from rest_framework.filters import SearchFilter
from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response
from rest_framework import status
from django.contrib.auth.models import User
from robots.models import Brand
from django.db import transaction
from rest_framework.exceptions import ValidationError
import json
from rest_framework import serializers
 
class ProfilViewSet(ModelViewSet):
    """
    Profil yönetimi için ViewSet.
    Tüm CRUD işlemlerini destekler:
    - GET /api/profile/profilleri/ -> Liste
    - POST /api/profile/profilleri/ -> Yeni oluştur
    - GET /api/profile/profilleri/{id}/ -> Detay
    - PUT/PATCH /api/profile/profilleri/{id}/ -> Güncelle
    - DELETE /api/profile/profilleri/{id}/ -> Sil
    
    Özel action'lar:
    - POST /api/profile/profilleri/{id}/toggle_active/ -> Aktif/Pasif
    - POST /api/profile/profilleri/{id}/update_brand/ -> Marka güncelle
    """
    
    queryset = Profil.objects.all()
    serializer_class = ProfilSerializer
    permission_classes = [IsAdminUser]
    filter_backends = [SearchFilter]
    search_fields = ['bio']
    
    def get_permissions(self):
        """
        Her request için permissions'ları dinamik olarak al
        Debug için ek loglama ekle
        """
        permissions = super().get_permissions()
        print(f"🔍 PERMISSION DEBUG - User: {self.request.user}")
        print(f"🔍 PERMISSION DEBUG - User authenticated: {self.request.user.is_authenticated}")
        print(f"🔍 PERMISSION DEBUG - User is_staff: {getattr(self.request.user, 'is_staff', False)}")
        print(f"🔍 PERMISSION DEBUG - User is_superuser: {getattr(self.request.user, 'is_superuser', False)}")
        print(f"🔍 PERMISSION DEBUG - Action: {self.action}")
        print(f"🔍 PERMISSION DEBUG - Method: {self.request.method}")
        print(f"🔍 PERMISSION DEBUG - Path: {self.request.path}")
        print(f"🔍 PERMISSION DEBUG - URL Name: {getattr(self.request.resolver_match, 'url_name', 'N/A')}")
        print(f"🔍 PERMISSION DEBUG - Permissions: {[p.__class__.__name__ for p in permissions]}")
        return permissions
    
    def check_permissions(self, request):
        """
        Permission kontrolünü override et ve debug bilgisi ekle
        """
        print(f"🔍 CHECK_PERMISSIONS DEBUG - User: {request.user}")
        print(f"🔍 CHECK_PERMISSIONS DEBUG - Method: {request.method}")
        print(f"🔍 CHECK_PERMISSIONS DEBUG - Action: {getattr(self, 'action', 'None')}")
        
        try:
            result = super().check_permissions(request)
            print(f"✅ CHECK_PERMISSIONS DEBUG - Permission check PASSED")
            return result
        except Exception as e:
            print(f"❌ CHECK_PERMISSIONS DEBUG - Permission check FAILED: {str(e)}")
            raise
    
    def create(self, request, *args, **kwargs):
        """Yeni profil oluştur"""
        user = None
        try:
            # Debug: Gelen veriyi logla
            print(f"🔍 Gelen request.data: {request.data}")
            print(f"🔍 Content type: {request.content_type}")
            print(f"🔍 Method: {request.method}")
            print(f"🔍 Request.data.dict(): {request.data.dict() if hasattr(request.data, 'dict') else 'N/A'}")
            
            # Serializer'ı kullanarak veriyi doğrula
            serializer = self.get_serializer(data=request.data)
            print(f"🔍 Serializer validation öncesi data: {serializer.initial_data}")
            
            if not serializer.is_valid():
                print(f"🔍 Serializer errors: {serializer.errors}")
                print(f"🔍 Serializer non_field_errors: {serializer.non_field_errors()}")
                return Response({
                    'error': 'Validation errors',
                    'details': serializer.errors
                }, status=status.HTTP_400_BAD_REQUEST)
            
            print(f"🔍 Validated data: {serializer.validated_data}")
            
            # Validasyon
            username = serializer.validated_data.get('username')
            password = serializer.validated_data.get('password')
            email = serializer.validated_data.get('email', '')
            
            if not username or not password:
                return Response({
                    'error': 'Kullanıcı adı ve şifre gereklidir'
                }, status=status.HTTP_400_BAD_REQUEST)
            
            # Kullanıcı kontrolü ve temizlik
            existing_user = User.objects.filter(username=username).first()
            if existing_user:
                # Eğer kullanıcı var ama profili yoksa, kullanıcıyı sil (orphan user)
                if not hasattr(existing_user, 'profil'):
                    print(f"🗑️ Orphan user bulundu, siliniyor: {username}")
                    existing_user.delete()
                else:
                    # Kullanıcı ve profil her ikisi de varsa hata dön
                    return Response({
                        'error': f'"{username}" kullanıcı adı zaten kullanılıyor'
                    }, status=status.HTTP_400_BAD_REQUEST)
            
            # Marka kontrolü
            brand_id = serializer.validated_data.get('brand_id', '')
            brand = None
            if brand_id and brand_id != 'none':
                try:
                    brand = Brand.objects.get(id=brand_id)
                    # Kullanıcı sınırını kontrol et
                    if not brand.can_add_user():
                        return Response({
                            'error': f'Bu marka için kullanıcı sınırına ulaşıldı. Maksimum {brand.get_user_limit()} kullanıcı eklenebilir.'
                        }, status=status.HTTP_400_BAD_REQUEST)
                except (Brand.DoesNotExist, ValueError):
                    return Response({
                        'error': 'Belirtilen marka bulunamadı'
                    }, status=status.HTTP_404_NOT_FOUND)
            
            # Transaction ile güvenli oluşturma
            with transaction.atomic():
                try:
                    # Kullanıcı oluştur
                    user = User.objects.create_user(
                        username=username,
                        password=password,
                        email=email,
                        is_active=True
                    )
                    
                    # Kullanıcı türüne göre yetkileri ayarla
                    user_type = serializer.validated_data.get('user_type', 'normal')
                    print(f"🔍 User type: {user_type}")
                    if user_type == 'admin':
                        user.is_staff = True
                        user.is_superuser = False
                    elif user_type == 'superadmin':
                        user.is_staff = True
                        user.is_superuser = True
                    else:
                        user.is_staff = False
                        user.is_superuser = False
                    user.save()
                    
                    # Profil oluştur veya varsa al
                    profil, profil_created = Profil.objects.get_or_create(
                        user=user,
                        defaults={
                            'brand': brand,
                            'bio': serializer.validated_data.get('bio', f"{username} kullanıcısının profili")
                        }
                    )
                    
                    # Eğer profil zaten varsa brand'i güncelle
                    if not profil_created and brand:
                        profil.brand = brand
                        profil.save()
                    
                    print(f"🔍 Profil created: {profil_created}, Profil ID: {profil.id}")
                    
                    # Başarılı oluşturma durumunda log
                    print(f"✅ {username} kullanıcısı ve profili başarıyla oluşturuldu")
                    
                    # Oluşturulan profili serialize et ve dön
                    result_serializer = self.get_serializer(profil)
                    return Response(result_serializer.data, status=status.HTTP_201_CREATED)
                    
                except ValidationError as ve:
                    # Transaction otomatik olarak rollback yapacak
                    print(f"❌ Validation hatası: {str(ve)}")
                    return Response({
                        'error': str(ve)
                    }, status=status.HTTP_400_BAD_REQUEST)
                except Exception as e:
                    # Transaction otomatik olarak rollback yapacak
                    print(f"❌ Beklenmeyen hata: {str(e)}")
                    raise e
                    
        except serializers.ValidationError as e:
            print(f"❌ Serializer validation hatası: {str(e)}")
            return Response({
                'error': str(e)
            }, status=status.HTTP_400_BAD_REQUEST)
        except Exception as e:
            # Hata durumunda detaylı loglama
            import traceback
            print("❌ Kullanıcı oluşturma hatası:")
            print(f"Gelen veri: {request.data}")
            print(f"Content type: {request.content_type}")
            print(f"Hata: {str(e)}")
            print(traceback.format_exc())
            
            # Eğer kullanıcı oluşturuldu ama profil oluşturulamadıysa kullanıcıyı sil
            if user:
                try:
                    print(f"🗑️ Hata sonrası {user.username} kullanıcısı siliniyor...")
                    user.delete()
                    print(f"✅ {user.username} kullanıcısı başarıyla silindi")
                except Exception as delete_error:
                    print(f"❌ Kullanıcı silme hatası: {str(delete_error)}")
            
            return Response({
                'error': f'Kullanıcı oluşturulurken hata oluştu: {str(e)}'
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
    
    def perform_destroy(self, instance):
        """Profil ve ilişkili User'ı sil"""
        user = instance.user
        instance.delete()
        user.delete()
        
    def perform_update(self, serializer):
        """Profil güncelleme"""
        instance = serializer.instance
        
        # QueryDict'ten normal dict'e çevir ve ilk değerleri al
        data = {}
        for key in self.request.data:
            values = self.request.data.getlist(key)
            # Eğer liste boş değilse ilk değeri al
            if values:
                # Eğer tek elemanlı liste ise ilk elemanı al
                if len(values) == 1:
                    data[key] = values[0]
                else:
                    # Birden fazla değer varsa listeyi olduğu gibi kullan
                    data[key] = values
            else:
                data[key] = None
        
        # Debug bilgileri
        print(f"🔍 UPDATE - Gelen raw data: {self.request.data}")
        print(f"🔍 UPDATE - Düzenlenmiş data: {data}")
        print(f"🔍 UPDATE - Instance user: {instance.user.username}")
        print(f"🔍 UPDATE - Current brand: {instance.brand}")
        print(f"🔍 UPDATE - Serializer validated_data: {serializer.validated_data}")
        
        # Marka kontrolü - validated_data'yı kullan
        brand_id = serializer.validated_data.get('brand_id')
        print(f"🔍 UPDATE - brand_id from validated_data: '{brand_id}'")
        
        if brand_id is not None:
            try:
                brand = Brand.objects.get(id=brand_id)
                # Eğer farklı bir markaya geçiş yapılıyorsa sınırı kontrol et
                if not instance.brand or instance.brand.id != brand.id:
                    # Markanın mevcut kullanıcı sayısını ve limitini kontrol et
                    # Mevcut kullanıcıyı hariç tut
                    current_user_count = brand.users.filter(user__is_active=True).exclude(user=instance.user).count()
                    user_limit = brand.get_user_limit()
                    print(f"🔍 UPDATE - Brand {brand.name} - Current users (excluding current user): {current_user_count}, Limit: {user_limit}")
                    
                    if current_user_count >= user_limit:
                        error_message = (
                            f'Bu marka için kullanıcı sınırına ulaşıldı. '
                            f'Maksimum {user_limit} kullanıcı eklenebilir. '
                            f'Şu anda {current_user_count} kullanıcı var. '
                            f'Paket türü: {brand.paket_turu}'
                        )
                        detail = {
                            'brand_id_input': [error_message],
                            'code': 'user_limit_exceeded',
                            'current_count': current_user_count,
                            'limit': user_limit,
                            'brand_name': brand.name,
                            'package_type': brand.paket_turu
                        }
                        print(f"🔍 Validation Error: {error_message}")
                        raise ValidationError(detail)
                instance.brand = brand
                print(f"🔍 UPDATE - Brand set to: {brand.name}")
            except Brand.DoesNotExist as e:
                print(f"🔍 UPDATE - Brand error: {str(e)}")
                raise ValidationError({'brand_id_input': ['Belirtilen marka bulunamadı']})
        else:
            # brand_id None ise brand'i None yap
            instance.brand = None
            print(f"🔍 UPDATE - Brand set to None")
        
        # User bilgilerini güncelle
        user = instance.user
        username = serializer.validated_data.get('username')
        if username and username != user.username:
            if User.objects.filter(username=username).exclude(id=user.id).exists():
                raise ValidationError(f'"{username}" kullanıcı adı zaten kullanılıyor')
            user.username = username
        
        password = serializer.validated_data.get('password')
        if password:
            user.set_password(password)
        
        user_type = serializer.validated_data.get('user_type')
        print(f"🔍 UPDATE - user_type from validated_data: '{user_type}'")
        print(f"🔍 UPDATE - user_type bool: {bool(user_type)}")
        print(f"🔍 UPDATE - user_type == 'superadmin': {user_type == 'superadmin'}")
        print(f"🔍 UPDATE - user_type == 'admin': {user_type == 'admin'}")
        
        if user_type:
            if user_type == 'admin':
                user.is_staff = True
                user.is_superuser = False
                print(f"🔍 Setting user as ADMIN")
            elif user_type == 'superadmin':
                user.is_staff = True
                user.is_superuser = True
                print(f"🔍 Setting user as SUPERADMIN")
            else:
                user.is_staff = False
                user.is_superuser = False
                print(f"🔍 Setting user as NORMAL")
        else:
            print(f"🔍 user_type is empty/null, not changing permissions")
        
        user.save()
        serializer.save()
        
        # Debug: Güncelleme sonrası durumu logla
        instance.refresh_from_db()
        user.refresh_from_db()
        print(f"🔍 UPDATE AFTER - User: {user.username}")
        print(f"🔍 UPDATE AFTER - User staff: {user.is_staff}")
        print(f"🔍 UPDATE AFTER - User superuser: {user.is_superuser}")
        print(f"🔍 UPDATE AFTER - Brand: {instance.brand}")
        print(f"✅ UPDATE completed successfully")
        
    @action(detail=True, methods=['post'])
    def toggle_active(self, request, pk=None):
        """Kullanıcının aktif/pasif durumunu değiştirir"""
        profil = self.get_object()
        user = profil.user
        user.is_active = not user.is_active
        user.save()
        
        # Eğer kullanıcı pasif yapılıyorsa ve bir markaya bağlıysa, markanın kullanıcı sayısı güncellenir
        if not user.is_active and profil.brand:
            profil.brand.active_users_count()
        
        return Response({
            'status': 'success',
            'message': f'Kullanıcı {"aktif" if user.is_active else "pasif"} duruma getirildi',
            'is_active': user.is_active
        })
        
    @action(detail=True, methods=['post'])
    def update_brand(self, request, pk=None):
        """Kullanıcının markasını günceller"""
        profil = self.get_object()
        brand_id = request.data.get('brand_id')
        
        try:
            # Marka ID boş veya 'none' ise markayı kaldır
            if not brand_id or brand_id == 'none':
                profil.brand = None
                profil.save()
                return Response({
                    'status': 'success',
                    'message': 'Kullanıcının markası kaldırıldı',
                    'brand': None
                })
            
            # Yeni markayı bul
            brand = Brand.objects.get(id=brand_id)
            
            # Kullanıcı sınırını kontrol et
            if not brand.can_add_user() and (not profil.brand or profil.brand.id != brand.id):
                return Response({
                    'status': 'error',
                    'message': f'Bu marka için kullanıcı sınırına ulaşıldı. Maksimum {brand.get_user_limit()} kullanıcı eklenebilir.',
                    'current_count': brand.active_users_count(),
                    'limit': brand.get_user_limit()
                }, status=status.HTTP_400_BAD_REQUEST)
            
            # Markayı güncelle
            profil.brand = brand
            profil.save()
            
            return Response({
                'status': 'success',
                'message': f'Kullanıcının markası {brand.name} olarak güncellendi',
                'brand': {
                    'id': brand.id,
                    'name': brand.name,
                    'package_type': brand.paket_turu
                }
            })
            
        except Brand.DoesNotExist:
            return Response({
                'status': 'error',
                'message': 'Belirtilen marka bulunamadı'
            }, status=status.HTTP_404_NOT_FOUND)
        except Exception as e:
            return Response({
                'status': 'error',
                'message': str(e)
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
    
    
    
    
class ProfilDurumViewSet(ModelViewSet):
    serializer_class = ProfilDurumSerializer
    permission_classes = [IsAdminUser]
    
    def get_queryset(self):
        queryset = ProfilDurum.objects.all()
        username = self.request.query_params.get('username', None)
        
        if username is not None:
            queryset = queryset.filter(user_profil__user__username = username)
        return queryset
    
    def perform_create(self, serializer):
        user_profil = self.request.user.profil
        serializer.save(user_profil = user_profil)
        
        
class ProfilFotoUpdateView(generics.UpdateAPIView):
    serializer_class = ProfilFotoSerializer
    permission_classes = [IsAdminUser]
    
    def get_object(self):
        profil_nesnesi = self.request.user.profil
        return profil_nesnesi


@api_view(['POST'])
@permission_classes([IsAdminUser])
def create_user_with_profile(request):
    """
    Yeni kullanıcı ve profil oluşturma endpoint'i
    Sadece admin kullanıcılar erişebilir
    """
    try:
        data = json.loads(request.body) if isinstance(request.body, bytes) else request.data
        
        username = data.get('username', '').strip()
        password = data.get('password', '')
        brand_id = data.get('brand_id')
        
        # Validasyon
        if not username:
            return Response(
                {'error': 'Kullanıcı adı gereklidir'}, 
                status=status.HTTP_400_BAD_REQUEST
            )
        
        if not password:
            return Response(
                {'error': 'Şifre gereklidir'}, 
                status=status.HTTP_400_BAD_REQUEST
            )
        
        if len(password) < 4:
            return Response(
                {'error': 'Şifre en az 4 karakter olmalıdır'}, 
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # Kullanıcı adı kontrolü
        if User.objects.filter(username=username).exists():
            return Response(
                {'error': f'"{username}" kullanıcı adı zaten kullanılıyor'}, 
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # Marka kontrolü
        brand = None
        if brand_id and brand_id != 'none':
            try:
                brand = Brand.objects.get(id=brand_id)
            except Brand.DoesNotExist:
                return Response(
                    {'error': 'Seçilen marka bulunamadı'}, 
                    status=status.HTTP_400_BAD_REQUEST
                )
        
        # Transaction ile güvenli oluşturma
        with transaction.atomic():
            # Kullanıcı oluştur
            user = User.objects.create_user(
                username=username,
                password=password,
                is_active=True
            )
            
            # Kullanıcı türüne göre yetkileri ayarla
            user_type = data.get('user_type', 'normal')
            if user_type == 'admin':
                user.is_staff = True
            elif user_type == 'superadmin':
                user.is_staff = True
                user.is_superuser = True
            
            user.save()
            
            # Profil oluştur - eğer yoksa
            profil, created = Profil.objects.get_or_create(
                user=user,
                defaults={
                    'brand': brand,
                    'bio': f"{username} kullanıcısının profili"
                }
            )
            
            # Eğer profil zaten varsa brand'i güncelle
            if not created and brand:
                profil.brand = brand
                profil.save()
        
        # Serialize et ve döndür
        serializer = ProfilSerializer(profil)
        
        return Response({
            'message': f'Kullanıcı "{username}" başarıyla oluşturuldu',
            'user': serializer.data
        }, status=status.HTTP_201_CREATED)
        
    except json.JSONDecodeError:
        return Response(
            {'error': 'Geçersiz JSON formatı'}, 
            status=status.HTTP_400_BAD_REQUEST
        )
    except Exception as e:
        return Response(
            {'error': f'Kullanıcı oluşturulurken hata oluştu: {str(e)}'}, 
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )


@api_view(['PUT'])
@permission_classes([IsAdminUser])
def update_user(request, user_id):
    """
    Kullanıcı güncelleme endpoint'i
    Sadece admin kullanıcılar erişebilir
    """
    try:
        data = json.loads(request.body) if isinstance(request.body, bytes) else request.data
        
        username = data.get('username', '').strip()
        user_type = data.get('user_type', 'normal')
        brand_id = data.get('brand_id')
        
        # Kullanıcıyı bul
        try:
            user = User.objects.get(id=user_id)
        except User.DoesNotExist:
            return Response(
                {'error': 'Kullanıcı bulunamadı'}, 
                status=status.HTTP_404_NOT_FOUND
            )
        
        # Validasyon
        if not username:
            return Response(
                {'error': 'Kullanıcı adı gereklidir'}, 
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # Kullanıcı adı kontrolü (kendi kullanıcı adı değişse bile başka birinin kullanıp kullanmadığını kontrol et)
        if User.objects.filter(username=username).exclude(id=user_id).exists():
            return Response(
                {'error': f'"{username}" kullanıcı adı zaten kullanılıyor'}, 
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # Marka kontrolü
        brand = None
        if brand_id and brand_id != 'none':
            try:
                brand = Brand.objects.get(id=brand_id)
            except Brand.DoesNotExist:
                return Response(
                    {'error': 'Seçilen marka bulunamadı'}, 
                    status=status.HTTP_400_BAD_REQUEST
                )
        
        # Kullanıcıyı güncelle
        user.username = username
        
        # Kullanıcı türüne göre yetkileri ayarla
        if user_type == 'normal':
            user.is_staff = False
            user.is_superuser = False
        elif user_type == 'admin':
            user.is_staff = True
            user.is_superuser = False
        elif user_type == 'superadmin':
            user.is_staff = True
            user.is_superuser = True
        
        user.save()
        
        # Profili güncelle
        try:
            profil = user.profil
            profil.brand = brand
            profil.save()
        except Profil.DoesNotExist:
            # Profil yoksa oluştur
            profil = Profil.objects.create(
                user=user,
                brand=brand,
                bio=f"{username} kullanıcısının profili"
            )
        
        # Serialize et ve döndür
        serializer = ProfilSerializer(profil)
        
        return Response({
            'message': f'Kullanıcı "{username}" başarıyla güncellendi',
            'user': serializer.data
        }, status=status.HTTP_200_OK)
        
    except json.JSONDecodeError:
        return Response(
            {'error': 'Geçersiz JSON formatı'}, 
            status=status.HTTP_400_BAD_REQUEST
        )
    except Exception as e:
        return Response(
            {'error': f'Kullanıcı güncellenirken hata oluştu: {str(e)}'}, 
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )


@api_view(['DELETE'])
@permission_classes([IsAdminUser])
def delete_user(request, user_id):
    """
    Kullanıcı silme endpoint'i
    Sadece admin kullanıcılar erişebilir
    """
    try:
        # Kullanıcıyı bul
        try:
            user = User.objects.get(id=user_id)
        except User.DoesNotExist:
            return Response(
                {'error': 'Kullanıcı bulunamadı'}, 
                status=status.HTTP_404_NOT_FOUND
            )
        
        # Kullanıcı kendini silmesini engelleyelim
        if user.id == request.user.id:
            return Response(
                {'error': 'Kendi hesabınızı silemezsiniz'}, 
                status=status.HTTP_400_BAD_REQUEST
            )
        
        username = user.username
        
        # Kullanıcıyı sil (CASCADE ile profil de silinecek)
        user.delete()
        
        return Response({
            'message': f'Kullanıcı "{username}" başarıyla silindi'
        }, status=status.HTTP_200_OK)
        
    except Exception as e:
        return Response(
            {'error': f'Kullanıcı silinirken hata oluştu: {str(e)}'}, 
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )


@api_view(['PATCH'])
@permission_classes([IsAdminUser])
def toggle_user_active(request, user_id):
    """
    Kullanıcının aktif/pasif durumunu değiştir
    Sadece admin kullanıcılar erişebilir
    """
    try:
        # Kullanıcıyı bul
        try:
            user = User.objects.get(id=user_id)
        except User.DoesNotExist:
            return Response(
                {'error': 'Kullanıcı bulunamadı'}, 
                status=status.HTTP_404_NOT_FOUND
            )
        
        # Kullanıcı kendini pasif yapmasını engelleyelim
        if user.id == request.user.id:
            return Response(
                {'error': 'Kendi hesabınızın durumunu değiştiremezsiniz'}, 
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # Durumu değiştir
        old_status = "aktif" if user.is_active else "pasif"
        user.is_active = not user.is_active
        new_status = "aktif" if user.is_active else "pasif"
        
        # Kullanıcıyı kaydet
        user.save()
        
        # Marka limit kontrolü
        brand_info = None
        if hasattr(user, 'profil') and user.profil.brand and user.is_active:
            brand = user.profil.brand
            if brand.is_user_limit_exceeded():
                # Eğer aktif yapıldıktan sonra limit aşılırsa kullanıcıyı tekrar pasif yap
                user.is_active = False
                user.save()
                return Response({
                    'error': f'Kullanıcı aktif yapılamadı. "{brand.name}" markasının kullanıcı limiti ({brand.get_user_limit()}) aşıldı.',
                    'brand_name': brand.name,
                    'user_limit': brand.get_user_limit(),
                    'active_users_count': brand.active_users_count()
                }, status=status.HTTP_400_BAD_REQUEST)
            
            brand_info = {
                'brand_name': brand.name,
                'user_limit': brand.get_user_limit(),
                'active_users_count': brand.active_users_count(),
                'user_status': brand.user_status()
            }
        
        # Güncellenmiş profil bilgilerini döndür
        try:
            profil = user.profil
            serializer = ProfilSerializer(profil)
            user_data = serializer.data
        except Profil.DoesNotExist:
            # Profil yoksa basit kullanıcı bilgilerini döndür
            user_data = {
                'id': user.id,
                'user': user.username,
                'is_active': user.is_active,
                'is_staff': user.is_staff,
                'is_superuser': user.is_superuser,
                'user_id': user.id
            }
        
        return Response({
            'message': f'Kullanıcı "{user.username}" başarıyla {old_status} durumundan {new_status} durumuna değiştirildi',
            'user': user_data,
            'old_status': old_status,
            'new_status': new_status,
            'brand_info': brand_info
        }, status=status.HTTP_200_OK)
        
    except Exception as e:
        return Response(
            {'error': f'Kullanıcı durumu değiştirilirken hata oluştu: {str(e)}'}, 
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )