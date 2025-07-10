from rest_framework import viewsets, permissions, status, serializers
from rest_framework.decorators import action, api_view, renderer_classes, permission_classes
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated, IsAdminUser, AllowAny
from rest_framework.renderers import JSONRenderer, BrowsableAPIRenderer
from rest_framework.views import APIView
from rest_framework.parsers import MultiPartParser, FormParser
from rest_framework.reverse import reverse
from robots.models import Robot, RobotPDF, Brand
from .permissions import CanAccessRobotData, CanAccessBrandData
from .serializers import (
    RobotSerializer, RobotPDFSerializer, RobotPDFCreateSerializer,
    ChatMessageSerializer
)
from robots.services import upload_pdf_to_services, get_robot_pdf_contents_for_ai
from robots.rag_services import RAGService
from rest_framework.throttling import UserRateThrottle
from concurrent.futures import ThreadPoolExecutor
import asyncio
import subprocess
import json
from django.conf import settings
import logging

logger = logging.getLogger(__name__)


class RobotViewSet(viewsets.ModelViewSet):
    # ⚡ PERFORMANS OPTİMİZASYONU: Select_related ve prefetch_related ekle
    queryset = Robot.objects.select_related('brand').prefetch_related('pdf_dosyalari')
    permission_classes = [IsAuthenticated]  # Temel yetkilendirme: Login olmuş kullanıcı
    
    def get_permissions(self):
        """
        Action'a göre farklı permission'lar:
        - list, retrieve: Login olan kullanıcı görebilir
        - create, update, delete: Admin yetkisi gerekli
        - pdf_dosyalari vb. özel action'lar: Marka bazlı yetkilendirme
        """
        if self.action in ['create', 'update', 'partial_update', 'destroy']:
            permission_classes = [IsAdminUser]
        elif self.action in ['pdf_dosyalari', 'aktif_pdf_dosyalari', 'kural_pdfleri', 
                           'rol_pdfleri', 'bilgi_pdfleri', 'beyan_pdfleri', 'upload_pdf']:
            permission_classes = [IsAuthenticated, CanAccessRobotData]
        else:
            permission_classes = [IsAuthenticated]
        
        return [permission() for permission in permission_classes]
    
    def get_queryset(self):
        """
        Kullanıcının markasına göre robot listesini filtrele
        Admin kullanıcılar tüm robotları görebilir
        Normal kullanıcılar sadece kendi markalarının robotlarını görebilir
        """
        # ⚡ PERFORMANS: Base queryset zaten optimize edildi (select_related + prefetch_related)
        queryset = Robot.objects.select_related('brand').prefetch_related('pdf_dosyalari')
        
        # Superuser ve admin staff tüm robotları görebilir
        if self.request.user.is_superuser or self.request.user.is_staff:
            return queryset
        
        # Normal kullanıcılar için marka kontrolü
        if hasattr(self.request.user, 'profil') and self.request.user.profil.brand:
            user_brand = self.request.user.profil.brand
            return queryset.filter(brand=user_brand)
        
        # Markası olmayan kullanıcılar hiçbir robot göremez
        return queryset.none()

    def get_serializer_class(self):
        if self.action == 'create':
            return RobotCreateSerializer
        return RobotSerializer
    
    @action(detail=True, methods=['get'])
    def pdf_dosyalari(self, request, pk=None):
        """Robot'un tüm PDF dosyalarını getir"""
        robot = self.get_object()
        pdfs = robot.pdf_dosyalari.all()
        serializer = RobotPDFSerializer(pdfs, many=True)
        return Response(serializer.data)
    
    @action(detail=True, methods=['get'])
    def aktif_pdf_dosyalari(self, request, pk=None):
        """Robot'un sadece aktif PDF dosyalarını getir"""
        robot = self.get_object()
        aktif_pdfs = robot.pdf_dosyalari.filter(is_active=True)
        serializer = RobotPDFSerializer(aktif_pdfs, many=True)
        return Response(serializer.data)
    
    @action(detail=True, methods=['get'])
    def kural_pdfleri(self, request, pk=None):
        """Robot'un kural PDF'lerini getir"""
        robot = self.get_object()
        kural_pdfs = robot.pdf_dosyalari.filter(is_active=True, has_rules=True)
        serializer = RobotPDFSerializer(kural_pdfs, many=True)
        return Response(serializer.data)
        
    @action(detail=True, methods=['get'])
    def rol_pdfleri(self, request, pk=None):
        """Robot'un rol PDF'lerini getir"""
        robot = self.get_object()
        rol_pdfs = robot.pdf_dosyalari.filter(is_active=True, has_role=True)
        serializer = RobotPDFSerializer(rol_pdfs, many=True)
        return Response(serializer.data)
        
    @action(detail=True, methods=['get'])
    def bilgi_pdfleri(self, request, pk=None):
        """Robot'un bilgi PDF'lerini getir"""
        robot = self.get_object()
        bilgi_pdfs = robot.pdf_dosyalari.filter(is_active=True, has_info=True)
        serializer = RobotPDFSerializer(bilgi_pdfs, many=True)
        return Response(serializer.data)
        
    @action(detail=True, methods=['get'])
    def beyan_pdfleri(self, request, pk=None):
        """Robot'un beyan PDF'lerini getir (İlaç firması yasal compliance için)"""
        robot = self.get_object()
        beyan_pdfs = robot.pdf_dosyalari.filter(is_active=True, has_declaration=True)
        serializer = RobotPDFSerializer(beyan_pdfs, many=True)
        return Response(serializer.data)

    @action(detail=True, methods=['post'], parser_classes=[MultiPartParser, FormParser])
    def upload_pdf(self, request, pk=None):
        """
        Bir robota yeni bir PDF dosyası yükler.
        Dosya hem Google Drive'a hem de Supabase'e yüklenir.
        """
        robot = self.get_object()
        file_obj = request.FILES.get('file')
        
        if not file_obj:
            return Response(
                {"error": "Yüklenecek dosya bulunamadı. Lütfen 'file' adında bir dosya gönderin."},
                status=status.HTTP_400_BAD_REQUEST
            )

        # Servis fonksiyonunu çağırarak dosyayı yükle
        upload_result = upload_pdf_to_services(file_obj, robot)

        if upload_result.get('error'):
            return Response(
                {"error": f"Dosya yüklenirken bir hata oluştu: {upload_result['error']}"},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )

        # Veritabanına kaydet
        # Aynı isimde dosya varsa üzerine yaz, yoksa yeni oluştur.
        pdf_instance, created = RobotPDF.objects.update_or_create(
            robot=robot,
            dosya_adi=file_obj.name,
            defaults={
                'pdf_dosyasi': upload_result['gdrive_link'],
                'gdrive_file_id': upload_result['gdrive_file_id'],
                'supabase_path': upload_result['supabase_path'],
                'aciklama': request.data.get('aciklama', ''),
                'is_active': True,
                # PDF türünü isteğe bağlı olarak alabiliriz, şimdilik 'bilgi' diyelim
                'pdf_type': request.data.get('pdf_type', 'bilgi') 
            }
        )
        
        # RAG sistemi için PDF'i chunk'la
        try:
            rag_service = RAGService()
            chunks_processed = rag_service.process_single_pdf(pdf_instance)
            logger.info(f"PDF upload başarılı: {chunks_processed} chunk oluşturuldu")
        except Exception as e:
            logger.error(f"RAG chunking hatası: {e}")
            # RAG hatası upload'ı engellemez, sadece log'larız
        
        serializer = RobotPDFSerializer(pdf_instance, context={'request': request})
        return Response(serializer.data, status=status.HTTP_201_CREATED if created else status.HTTP_200_OK)

    # ==================== YENİ OPTİMİZASYON YÖNETİMİ ====================
    
    @action(detail=True, methods=['post'])
    def toggle_optimization(self, request, pk=None):
        """Robot için optimizasyon modunu açar/kapatır"""
        robot = self.get_object()
        
        # Yetki kontrolü
        if not (request.user.is_staff or request.user.is_superuser):
            if not hasattr(request.user, 'profil') or not request.user.profil.brand:
                return Response({
                    'detail': 'Bu işlem için yetkiniz yok.'
                }, status=status.HTTP_403_FORBIDDEN)
            if robot.brand != request.user.profil.brand:
                return Response({
                    'detail': 'Bu robota erişim yetkiniz yok.'
                }, status=status.HTTP_403_FORBIDDEN)
        
        # Optimizasyon durumunu toggle et
        from robots.services import toggle_optimization_mode, is_optimization_enabled
        
        current_status = is_optimization_enabled(robot.id)
        new_status = not current_status
        
        success = toggle_optimization_mode(robot.id, new_status)
        
        if success:
            return Response({
                'success': True,
                'optimization_enabled': new_status,
                'message': f"Optimizasyon modu {'açıldı' if new_status else 'kapatıldı'}",
                'robot_name': robot.name
            })
        else:
            return Response({
                'success': False,
                'message': 'Optimizasyon durumu değiştirilemedi'
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
    
    @action(detail=True, methods=['get'])
    def optimization_status(self, request, pk=None):
        """Robot optimizasyon durumunu ve istatistiklerini döndürür"""
        robot = self.get_object()
        
        # Yetki kontrolü
        if not (request.user.is_staff or request.user.is_superuser):
            if not hasattr(request.user, 'profil') or not request.user.profil.brand:
                return Response({
                    'detail': 'Bu işlem için yetkiniz yok.'
                }, status=status.HTTP_403_FORBIDDEN)
            if robot.brand != request.user.profil.brand:
                return Response({
                    'detail': 'Bu robota erişim yetkiniz yok.'
                }, status=status.HTTP_403_FORBIDDEN)
        
        from robots.services import get_optimization_stats
        
        stats = get_optimization_stats(robot.id)
        
        # PDF content boyutları
        from robots.services import get_robot_pdf_contents_for_ai, get_optimized_robot_pdf_contents_for_ai
        
        try:
            standard_content = get_robot_pdf_contents_for_ai(robot)
            optimized_content = get_optimized_robot_pdf_contents_for_ai(robot)
            
            content_reduction = ((len(standard_content) - len(optimized_content)) / len(standard_content)) * 100 if len(standard_content) > 0 else 0
            
            stats.update({
                'robot_name': robot.name,
                'robot_id': robot.id,
                'standard_content_size': len(standard_content),
                'optimized_content_size': len(optimized_content),
                'content_reduction_percentage': round(content_reduction, 1),
                'estimated_speed_improvement': f"{round(content_reduction * 0.8, 1)}%"  # Tahmini hız artışı
            })
        except Exception as e:
            logger.error(f"İçerik boyutu hesaplama hatası: {e}")
            stats.update({
                'content_size_error': str(e)
            })
        
        return Response(stats)
    
    @action(detail=True, methods=['post'])
    def test_optimization(self, request, pk=None):
        """Optimizasyonu test et - örnek soru ile deneme"""
        robot = self.get_object()
        
        # Test mesajı
        test_message = request.data.get('test_message', 'Bağışıklık sistemi hakkında bilgi verir misin?')
        
        from robots.services import (
            get_robot_system_prompt,
            get_optimized_system_prompt, 
            get_robot_pdf_contents_for_ai,
            get_optimized_robot_pdf_contents_for_ai
        )
        
        # Standart versiyon
        standard_prompt = get_robot_system_prompt(robot, test_message)
        standard_content = get_robot_pdf_contents_for_ai(robot)
        standard_total = len(standard_prompt) + len(standard_content)
        
        # Optimize versiyon
        optimized_prompt = get_optimized_system_prompt(robot, test_message)
        optimized_content = get_optimized_robot_pdf_contents_for_ai(robot)
        optimized_total = len(optimized_prompt) + len(optimized_content)
        
        # Karşılaştırma
        reduction_percentage = ((standard_total - optimized_total) / standard_total) * 100 if standard_total > 0 else 0
        
        return Response({
            'robot_name': robot.name,
            'test_message': test_message,
            'standard_version': {
                'prompt_size': len(standard_prompt),
                'content_size': len(standard_content),
                'total_size': standard_total
            },
            'optimized_version': {
                'prompt_size': len(optimized_prompt),
                'content_size': len(optimized_content),
                'total_size': optimized_total
            },
            'improvement': {
                'size_reduction': f"{standard_total - optimized_total} karakter",
                'reduction_percentage': f"{round(reduction_percentage, 1)}%",
                'estimated_speed_improvement': f"{round(reduction_percentage * 0.8, 1)}%"
            },
            'recommendation': "Optimizasyon önerilir" if reduction_percentage > 50 else "Standart mod yeterli"
        })


class RobotPDFViewSet(viewsets.ModelViewSet):
    # ⚡ PERFORMANS OPTİMİZASYONU: Select_related ekle
    queryset = RobotPDF.objects.select_related('robot', 'robot__brand')
    permission_classes = [IsAuthenticated]  # Login olan kullanıcılar erişebilir
    
    def get_serializer_class(self):
        if self.action in ['create', 'update', 'partial_update']:
            return RobotPDFCreateSerializer
        return RobotPDFSerializer
    
    def get_permissions(self):
        """Action'a göre farklı permission'lar"""
        if self.action in ['list', 'retrieve']:
            # Görüntüleme için authentication yeterli
            permission_classes = [IsAuthenticated]
        else:
            # Düzenleme işlemleri için özel izin kontrolü
            permission_classes = [IsAuthenticated]
        
        return [permission() for permission in permission_classes]
    
    def perform_create(self, serializer):
        """PDF oluşturma öncesi izin kontrolü"""
        if not self._can_edit_pdf():
            from rest_framework.exceptions import PermissionDenied
            raise PermissionDenied("PDF düzenleme için Pro veya Premium paket gereklidir.")
        super().perform_create(serializer)
    
    def perform_update(self, serializer):
        """PDF güncelleme öncesi izin kontrolü"""
        if not self._can_edit_pdf():
            from rest_framework.exceptions import PermissionDenied
            raise PermissionDenied("PDF düzenleme için Pro veya Premium paket gereklidir.")
        
        # PDF türü değiştiyse ilgili alanları güncelle
        if 'pdf_type' in serializer.validated_data:
            pdf_type = serializer.validated_data['pdf_type']
            serializer.validated_data.update({
                'has_rules': pdf_type == 'kural',
                'has_role': pdf_type == 'rol',
                'has_info': pdf_type == 'bilgi',
                'has_declaration': pdf_type == 'beyan'
            })
        
        super().perform_update(serializer)
    
    def perform_destroy(self, instance):
        """PDF silme öncesi izin kontrolü"""
        if not self._can_edit_pdf():
            from rest_framework.exceptions import PermissionDenied
            raise PermissionDenied("PDF düzenleme için Pro veya Premium paket gereklidir.")
        super().perform_destroy(instance)
    
    def _can_edit_pdf(self):
        """Kullanıcının PDF düzenleme yetkisi var mı kontrol et"""
        user = self.request.user
        
        # Admin users have full access
        if user.is_staff or user.is_superuser:
            return True
        
        # Check if user has brand connection and premium/pro package
        if hasattr(user, 'profil') and user.profil.brand:
            package_type = user.profil.brand.paket_turu
            return package_type in ['pro', 'premium']
        
        return False
    
    def get_serializer_context(self):
        """Serializer context'e request'i ekle"""
        context = super().get_serializer_context()
        context.update({"request": self.request})
        return context
    
    def get_queryset(self):
        # ⚡ PERFORMANS: Select_related ile robot ve brand'i önceden yükle
        queryset = RobotPDF.objects.select_related('robot', 'robot__brand')
        
        # Brand bazlı filtreleme - sadece admin olmayan kullanıcılar için
        if not (self.request.user.is_superuser or self.request.user.is_staff):
            # Normal kullanıcılar sadece kendi markalarının robot PDF'lerini görebilir
            if hasattr(self.request.user, 'profil') and self.request.user.profil.brand:
                user_brand = self.request.user.profil.brand
                queryset = queryset.filter(robot__brand=user_brand)
            else:
                # Markası olmayan kullanıcılar hiçbir PDF göremez
                return queryset.none()
        
        robot_id = self.request.query_params.get('robot_id', None)
        is_active = self.request.query_params.get('is_active', None)
        pdf_type = self.request.query_params.get('pdf_type', None)
        
        if robot_id is not None:
            queryset = queryset.filter(robot_id=robot_id)
        
        if is_active is not None:
            # is_active parametresi 'true' veya 'false' string olarak gelir
            is_active_bool = is_active.lower() in ['true', '1', 'yes']
            queryset = queryset.filter(is_active=is_active_bool)
        
        if pdf_type is not None:
            # pdf_type filtrelemesi ekle
            if pdf_type in ['bilgi', 'kural', 'rol', 'beyan']:
                queryset = queryset.filter(pdf_type=pdf_type)
        
        return queryset
    
    @action(detail=True, methods=['post'])
    def toggle_active(self, request, pk=None):
        """PDF'in aktif/pasif durumunu değiştir"""
        if not self._can_edit_pdf():
            return Response({
                'detail': 'PDF düzenleme için Pro veya Premium paket gereklidir.'
            }, status=status.HTTP_403_FORBIDDEN)

        instance = self.get_object()
        old_active_status = instance.is_active
        instance.is_active = not instance.is_active
        instance.save()

        # RAG chunks'larının aktiflik durumunu senkronize et
        try:
            rag_service = RAGService()
            if instance.is_active and not old_active_status:
                # Pasif'ten aktif'e geçti - chunk'ları yeniden oluştur
                chunks_processed = rag_service.process_single_pdf(instance)
                logger.info(f"PDF aktif edildi: {chunks_processed} chunk oluşturuldu")
            elif not instance.is_active and old_active_status:
                # Aktif'ten pasif'e geçti - chunk'ları sil
                deleted_chunks = rag_service.delete_chunks_for_pdf(instance.id)
                logger.info(f"PDF pasif edildi: {deleted_chunks} chunk silindi")
        except Exception as e:
            logger.error(f"RAG sync hatası: {e}")

        serializer = self.get_serializer(instance)
        return Response(serializer.data)

    @action(detail=True, methods=['post'])
    def change_type(self, request, pk=None):
        """PDF türünü değiştir"""
        if not self._can_edit_pdf():
            return Response({
                'detail': 'PDF düzenleme için Pro veya Premium paket gereklidir.'
            }, status=status.HTTP_403_FORBIDDEN)

        instance = self.get_object()
        old_type = instance.pdf_type
        new_type = request.data.get('pdf_type')

        if not new_type or new_type not in ['bilgi', 'kural', 'rol', 'beyan']:
            return Response({
                'detail': 'Geçerli bir PDF türü seçiniz (bilgi, kural, rol, beyan)'
            }, status=status.HTTP_400_BAD_REQUEST)

        # PDF türünü güncelle
        instance.pdf_type = new_type
        instance.save()

        # RAG chunks'larında PDF type metadata'sını güncelle
        if instance.is_active and old_type != new_type:
            try:
                rag_service = RAGService()
                updated_chunks = rag_service.update_pdf_type_metadata(instance.id, new_type)
                logger.info(f"PDF türü güncellendi: {updated_chunks} chunk metadata'sı güncellendi")
            except Exception as e:
                logger.error(f"RAG metadata update hatası: {e}")

        serializer = self.get_serializer(instance)
        return Response(serializer.data)

        instance.pdf_type = new_type
        instance.has_rules = new_type == 'kural'
        instance.has_role = new_type == 'rol'
        instance.has_info = new_type == 'bilgi'
        instance.has_declaration = new_type == 'beyan'
        instance.save()

        serializer = self.get_serializer(instance)
        return Response(serializer.data)


class BrandViewSet(viewsets.ModelViewSet):
    """Marka yönetimi - Görüntüleme için markası olan kullanıcılar, düzenleme için admin"""
    queryset = Brand.objects.all()
    serializer_class = None  # Serializer'ı aşağıda oluşturacağız
    permission_classes = [IsAuthenticated, CanAccessBrandData]  # Login olan ve marka erişimi olan kullanıcılar erişebilir
    
    # Sadece okuma ve güncelleme işlemine izin ver - CREATE işlemini engelle
    http_method_names = ['get', 'put', 'patch', 'post', 'head', 'options']
    
    def create(self, request, *args, **kwargs):
        """Yeni marka oluşturmayı engelle"""
        return Response({
            'error': 'Yeni marka oluşturulamaz. Sadece mevcut Sidrex markası düzenlenebilir.',
            'detail': 'Bu endpoint sadece mevcut Sidrex markasının paket türünü değiştirmek için kullanılabilir.',
            'available_actions': [
                'GET /api/brands/ - Mevcut durumu görüntüle',
                'PATCH /api/brands/{id}/ - Paket türünü değiştir',
                'POST /api/brands/{id}/change_package/ - Özel paket değiştirme action'
            ]
        }, status=status.HTTP_405_METHOD_NOT_ALLOWED)
    
    def get_queryset(self):
        """
        Admin kullanıcılar tüm markaları görebilir
        Normal kullanıcılar sadece kendi markalarını görebilir
        """
        # Admin kullanıcılar tüm markaları görebilir
        if self.request.user.is_superuser or self.request.user.is_staff:
            return Brand.objects.all()
        
        # Normal kullanıcılar için marka kontrolü
        if hasattr(self.request.user, 'profil') and self.request.user.profil.brand:
            user_brand = self.request.user.profil.brand
            return Brand.objects.filter(id=user_brand.id)
        
        # Markası olmayan kullanıcılar hiçbir marka göremez
        return Brand.objects.none()
    
    @action(detail=True, methods=['post'])
    def change_package(self, request, pk=None):
        """Paket türünü değiştir"""
        brand = self.get_object()
        new_package_type = request.data.get('paket_turu')
        
        if not new_package_type:
            return Response({
                'error': 'paket_turu alanı gereklidir'
            }, status=status.HTTP_400_BAD_REQUEST)
        
        try:
            result = brand.change_package_type(new_package_type)
            
            # Paket düşürülürse deaktive edilen kullanıcıları kontrol et
            deactivated_users = []
            if result['new_user_limit'] < result['old_user_limit']:
                deactivated_users = brand.deactivate_excess_users()
            
            response_data = {
                'message': f'Paket türü {result["old_package"]} dan {result["new_package"]} e değiştirildi',
                'brand_id': brand.id,
                'old_package': result['old_package'],
                'new_package': result['new_package'],
                'new_limit': result['new_limit'],
                'reset_requests': result['reset_requests'],
                'new_end_date': result['new_end_date'],
                'remaining_requests': brand.remaining_requests(),
                'remaining_days': brand.remaining_days(),
                'package_status': brand.package_status(),
                # Kullanıcı limit bilgileri
                'old_user_limit': result['old_user_limit'],
                'new_user_limit': result['new_user_limit'],
                'active_users_count': brand.active_users_count(),
                'user_status': brand.user_status(),
                'can_add_user': brand.can_add_user(),
                'deactivated_users': deactivated_users,
                'deactivated_count': len(deactivated_users)
            }
            
            # Eğer kullanıcı deaktive edildiyse mesajı güncelle
            if deactivated_users:
                response_data['message'] += f' | {len(deactivated_users)} kullanıcı pasif hale getirildi: {", ".join(deactivated_users)}'
            
            return Response(response_data)
        except ValueError as e:
            return Response({
                'error': str(e),
                'valid_choices': [choice[0] for choice in Brand.PAKET_CHOICES]
            }, status=status.HTTP_400_BAD_REQUEST)
    
    def get_serializer_class(self):
        # Inline serializer tanımlaması
        class BrandSerializer(serializers.ModelSerializer):
            remaining_requests = serializers.SerializerMethodField()
            remaining_days = serializers.SerializerMethodField()
            package_status = serializers.SerializerMethodField()
            is_package_expired = serializers.SerializerMethodField()
            paket_turu_display = serializers.SerializerMethodField()
            
            # Kullanıcı limit bilgileri
            user_limit = serializers.SerializerMethodField()
            active_users_count = serializers.SerializerMethodField()
            user_status = serializers.SerializerMethodField()
            can_add_user = serializers.SerializerMethodField()
            active_users = serializers.SerializerMethodField()
            
            class Meta:
                model = Brand
                fields = ['id', 'name', 'total_api_requests', 'request_limit', 
                         'paket_turu', 'paket_turu_display',
                         'paket_baslangic_tarihi', 'paket_bitis_tarihi',
                         'remaining_requests', 'remaining_days', 'package_status',
                         'is_package_expired', 'user_limit', 'active_users_count',
                         'user_status', 'can_add_user', 'active_users',
                         'created_at', 'updated_at']
                # paket_turu'yu read_only_fields'dan çıkardık - artık yazılabilir
                read_only_fields = ['name', 'total_api_requests', 'request_limit', 'paket_bitis_tarihi', 'created_at', 'updated_at']
            
            def validate_paket_turu(self, value):
                """paket_turu field'ı için özel validation"""
                valid_choices = [choice[0] for choice in Brand.PAKET_CHOICES]
                if value not in valid_choices:
                    raise serializers.ValidationError(
                        f"Geçersiz paket türü: {value}. Geçerli seçenekler: {valid_choices}"
                    )
                return value
            
            def update(self, instance, validated_data):
                """Update metodunu override ederek paket değişikliğini handle et"""
                # Eğer paket_turu değişiyorsa, model'deki change_package_type metodunu kullan
                new_package_type = validated_data.get('paket_turu')
                if new_package_type and new_package_type != instance.paket_turu:
                    try:
                        instance.change_package_type(new_package_type)
                        # change_package_type metodu zaten save() yapıyor, bu yüzden validated_data'dan çıkar
                        validated_data.pop('paket_turu', None)
                    except ValueError as e:
                        raise serializers.ValidationError({'paket_turu': str(e)})
                
                # Diğer alanları normal şekilde güncelle
                return super().update(instance, validated_data)
            
            def to_representation(self, instance):
                # Serializer çıktısını düzenle
                data = super().to_representation(instance)
                return data
            
            def get_remaining_requests(self, obj):
                return obj.remaining_requests()
            
            def get_remaining_days(self, obj):
                return obj.remaining_days()
            
            def get_package_status(self, obj):
                return obj.package_status()
            
            def get_is_package_expired(self, obj):
                return obj.is_package_expired()
            
            def get_paket_turu_display(self, obj):
                return obj.get_paket_turu_display()
            
            # Kullanıcı limit metodları
            def get_user_limit(self, obj):
                return obj.get_user_limit()
            
            def get_active_users_count(self, obj):
                return obj.active_users_count()
            
            def get_user_status(self, obj):
                return obj.user_status()
            
            def get_can_add_user(self, obj):
                return obj.can_add_user()
            
            def get_active_users(self, obj):
                """Aktif kullanıcıların listesini döndür"""
                active_users = obj.users.filter(user__is_active=True).select_related('user')
                return [
                    {
                        'id': profil.user.id,
                        'username': profil.user.username,
                        'email': profil.user.email,
                        'first_name': profil.user.first_name,
                        'last_name': profil.user.last_name,
                        'date_joined': profil.user.date_joined,
                        'is_staff': profil.user.is_staff,
                        'is_superuser': profil.user.is_superuser,
                    }
                    for profil in active_users
                ]
        
        return BrandSerializer


# Robots API Root View
@api_view(['GET'])
@renderer_classes([JSONRenderer, BrowsableAPIRenderer])
@permission_classes([IsAuthenticated])
def robots_root(request, format=None):
    """
    Robot API'sinin ana endpoint'i.
    Mevcut tüm robotların listesini ve endpoint'lerini döndürür.
    """
    robots = Robot.objects.filter(is_active=True)
    
    # Her robot için endpoint'leri oluştur
    robot_endpoints = {}
    for robot in robots:
        # Kullanıcının erişim yetkisi kontrolü
        if request.user.is_staff or request.user.is_superuser:
            has_access = True
        elif hasattr(request.user, 'profil') and request.user.profil.brand:
            has_access = (robot.brand == request.user.profil.brand)
        else:
            has_access = False
            
        if has_access:
            slug = robot.get_slug()
            robot_endpoints[robot.name] = {
                'detail': request.build_absolute_uri(reverse('robot-detail-by-slug', kwargs={'slug': slug})),
                'chat': request.build_absolute_uri(reverse('robot-chat', kwargs={'slug': slug})),
            }
    
    return Response({
        'robots': reverse('robot-list', request=request, format=format),
        'robot_pdfs': reverse('robotpdf-list', request=request, format=format),
        'brands': reverse('brand-list', request=request, format=format),
        'robot_endpoints': robot_endpoints,
    })

@api_view(['GET'])
@renderer_classes([JSONRenderer, BrowsableAPIRenderer])
@permission_classes([AllowAny])  # Login olmayan kullanıcılar da robot bilgilerini görebilir
def robot_detail_by_slug(request, slug, format=None):
    """
    Slug ile robot detayını getir - Public bilgiler ve yetki kontrolü
    """
    try:
        # get_slug() metodunu kullanarak robotu bul
        robot = None
        for r in Robot.objects.all():
            if r.get_slug() == slug:
                robot = r
                break
        
        if not robot:
            raise Robot.DoesNotExist
            
        # Login olmayan kullanıcılar için temel bilgiler
        if not request.user.is_authenticated:
            basic_data = {
                'id': robot.id,
                'name': robot.name,
                'description': robot.description if hasattr(robot, 'description') else '',
                'slug': slug,
                'access_level': 'public'
            }
            return Response(basic_data)
        
        # Admin kullanıcılar için full access
        if request.user.is_staff or request.user.is_superuser:
            serializer = RobotSerializer(robot)
            data = serializer.data
            data['access_level'] = 'admin'
            return Response(data)
        
        # Normal kullanıcılar için marka kontrolü
        has_profil = hasattr(request.user, 'profil')
        
        if has_profil and request.user.profil.brand:
            user_brand = request.user.profil.brand
            
            if robot.brand == user_brand:
                # Marka uyuşuyor - full access
                serializer = RobotSerializer(robot)
                data = serializer.data
                data['access_level'] = 'brand_member'
                return Response(data)
        
        # Kullanıcı login ama yetkisi yok - limited access
        limited_data = {
            'id': robot.id,  # PDF yönetimi için gerekli
            'name': robot.name,
            'description': robot.description if hasattr(robot, 'description') else '',
            'slug': slug,
            'access_level': 'limited',
            'message': 'Bu robota tam erişiminiz bulunmuyor. Lütfen sistem yöneticisiyle iletişime geçin.'
        }
        return Response(limited_data)
        
    except Robot.DoesNotExist:
        return Response(
            {'detail': 'Robot bulunamadı.'},
            status=status.HTTP_404_NOT_FOUND
        )

class ChatThrottle(UserRateThrottle):
    rate = '5/minute'

class RobotChatView(APIView):
    """
    Robot chat endpoint'i
    """
    renderer_classes = [JSONRenderer, BrowsableAPIRenderer]
    permission_classes = [IsAuthenticated]
    throttle_classes = [ChatThrottle]
    serializer_class = ChatMessageSerializer

    def get_robot_by_slug(self, slug):
        try:
            # get_slug() metodunu kullanarak robotu bul
            for robot in Robot.objects.all():
                if robot.get_slug() == slug:
                    return robot
            raise Robot.DoesNotExist
        except Robot.DoesNotExist:
            from django.http import Http404
            raise Http404

    def post(self, request, slug, format=None):
        import subprocess
        import json
        from django.conf import settings
        import logging
        logger = logging.getLogger(__name__)

        robot = self.get_robot_by_slug(slug)
        serializer = self.serializer_class(data=request.data)
        
        if serializer.is_valid():
            message = serializer.validated_data['message']
            history = serializer.validated_data.get('history', [])

            # Markanın API limitini kontrol et
            brand = robot.brand
            if brand.is_limit_exceeded() or brand.is_package_expired():
                return Response(
                    {"answer": "API kullanım limitiniz doldu veya paket süreniz sona erdi. Lütfen yöneticinizle iletişime geçin."},
                    status=status.HTTP_429_TOO_MANY_REQUESTS
                )

            # RAG sistemi ile alakalı context'i al
            rag_service = RAGService()
            
            pdf_context, citations = rag_service.get_relevant_context(
                query=message,
                robot_id=robot.id
            )
            
            # AI'ye gönderilecek 'messages' listesini oluştur
            messages = []
            
            # 🚀 OPTİMİZASYON: Optimizasyon modu kontrol et
            from robots.services import (
                get_robot_system_prompt, 
                is_optimization_enabled,
                get_optimized_robot_pdf_contents_for_ai,
                get_optimized_system_prompt,
                get_robot_pdf_contents_for_ai
            )
            
            optimization_enabled = is_optimization_enabled(robot.id)
            logger.info(f"🔧 Robot {robot.name} optimizasyon modu: {'AÇIK' if optimization_enabled else 'KAPALI'}")
            
            if optimization_enabled:
                # ⚡ OPTİMİZE MOD: Kısa sistem prompt'u + optimize PDF içeriği
                system_prompt_base = get_optimized_system_prompt(robot, message)
                
                # RAG yerine optimize PDF içeriği kullan
                pdf_context = get_optimized_robot_pdf_contents_for_ai(robot)
                logger.info(f"⚡ Optimize PDF içerik kullanıldı: {len(pdf_context)} karakter")
            else:
                # 🔄 STANDART MOD: Normal sistem prompt'u + RAG
                system_prompt_base = get_robot_system_prompt(robot, message)
                logger.info(f"🔄 Standart mod: RAG kullanıldı")
            
            # PDF context'i sistem prompt'una ekle
            system_prompt = f"""{system_prompt_base}

BAĞLAM:
{pdf_context}
"""
            messages.append({"role": "system", "content": system_prompt})

            # 2. Konuşma Geçmişi
            if isinstance(history, list):
                messages.extend(history)

            # 3. Son Kullanıcı Mesajı
            messages.append({"role": "user", "content": message})
            
            try:
                # ai-request.py script'ini çağır
                script_path = settings.BASE_DIR / 'robots' / 'scripts' / 'ai-request.py'
                api_key = settings.OPENROUTER_API_KEY

                if not api_key:
                    logger.error("OPENROUTER_API_KEY ayarlanmamış!")
                    return Response(
                        {"answer": "Sistem hatası: API anahtarı yapılandırılmamış."},
                        status=status.HTTP_500_INTERNAL_SERVER_ERROR
                    )

                process = subprocess.run(
                    [
                        'python', 
                        str(script_path),
                        '--api-key', api_key,
                        '--prompt', json.dumps(messages)
                    ],
                    capture_output=True,
                    text=True,
                    check=True,
                    encoding='utf-8'
                )
                
                answer = process.stdout.strip()

                # RAG bilgilerini logla
                rag_service.log_query(message, robot.id, pdf_context, citations, answer)

                brand.increment_api_count()

                # Citations ile birlikte yanıt döndür
                return Response({
                    "answer": answer,
                    "citations": citations,
                    "context_used": len(citations) > 0
                })

            except FileNotFoundError:
                logger.error(f"AI script dosyası bulunamadı: {script_path}")
                return Response(
                    {"answer": "Yapay zeka betiği bulunamadı. Lütfen sistem yöneticisiyle iletişime geçin."},
                    status=status.HTTP_500_INTERNAL_SERVER_ERROR
                )
            except subprocess.CalledProcessError as e:
                logger.error(f"AI script hatası: {e.stderr}")
                return Response(
                    {"answer": f"Yapay zeka yanıtı alınırken bir komut hatası oluştu: {e.stderr}"},
                    status=status.HTTP_500_INTERNAL_SERVER_ERROR
                )
            except Exception as e:
                logger.error(f"AI handler'da genel hata: {e}")
                return Response(
                    {"answer": "Yapay zeka yanıtı alınırken genel bir hata oluştu."},
                    status=status.HTTP_500_INTERNAL_SERVER_ERROR
                )
        
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


 