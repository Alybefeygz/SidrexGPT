from rest_framework import viewsets, permissions, status, serializers
from rest_framework.decorators import action, api_view, renderer_classes, permission_classes
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated, IsAdminUser
from rest_framework.renderers import JSONRenderer, BrowsableAPIRenderer
from rest_framework.views import APIView
from rest_framework.reverse import reverse
from robots.models import Robot, RobotPDF, Brand
from .permissions import CanAccessRobotData, CanAccessBrandData
from .serializers import (
    RobotSerializer, RobotPDFSerializer, RobotPDFCreateSerializer,
    ChatMessageSerializer
)
from rest_framework.throttling import UserRateThrottle
from concurrent.futures import ThreadPoolExecutor
import asyncio


class RobotViewSet(viewsets.ModelViewSet):
    queryset = Robot.objects.all()
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
        queryset = Robot.objects.all()
        
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

    @action(detail=True, methods=['post'])
    def upload_pdf(self, request, pk=None):
        """Robot için PDF yükle"""
        robot = self.get_object()
        
        # PDF dosyası kontrolü
        if 'pdf_dosyasi' not in request.FILES:
            return Response({
                'error': 'PDF dosyası gereklidir'
            }, status=status.HTTP_400_BAD_REQUEST)
        
        # PDF türü kontrolü
        pdf_type = request.data.get('pdf_type')
        if not pdf_type or pdf_type not in ['bilgi', 'kural', 'rol', 'beyan']:
            return Response({
                'error': 'Geçerli bir PDF türü seçiniz (bilgi, kural, rol, beyan)'
            }, status=status.HTTP_400_BAD_REQUEST)
        
        # Dosya adı kontrolü
        dosya_adi = request.data.get('dosya_adi')
        if not dosya_adi:
            return Response({
                'error': 'Dosya adı gereklidir'
            }, status=status.HTTP_400_BAD_REQUEST)
        
        try:
            # PDF oluştur
            pdf = RobotPDF.objects.create(
                robot=robot,
                pdf_dosyasi=request.FILES['pdf_dosyasi'],
                dosya_adi=dosya_adi,
                pdf_type=pdf_type,
                is_active=True,
                has_rules=pdf_type == 'kural',
                has_role=pdf_type == 'rol',
                has_info=pdf_type == 'bilgi',
                has_declaration=pdf_type == 'beyan'
            )
            
            # Serializer ile response dön
            serializer = RobotPDFSerializer(pdf)
            return Response(serializer.data, status=status.HTTP_201_CREATED)
            
        except Exception as e:
            return Response({
                'error': f'PDF yüklenirken hata oluştu: {str(e)}'
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


class RobotPDFViewSet(viewsets.ModelViewSet):
    queryset = RobotPDF.objects.all()
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
        queryset = RobotPDF.objects.all()
        
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
        instance.is_active = not instance.is_active
        instance.save()

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
        new_type = request.data.get('pdf_type')

        if not new_type or new_type not in ['bilgi', 'kural', 'rol', 'beyan']:
            return Response({
                'detail': 'Geçerli bir PDF türü seçiniz (bilgi, kural, rol, beyan)'
            }, status=status.HTTP_400_BAD_REQUEST)

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
    
    # Sadece okuma ve güncelleme işlemlerine izin ver - CREATE işlemini engelle
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
@permission_classes([IsAuthenticated])
def robot_detail_by_slug(request, slug, format=None):
    """
    Slug ile robot detayını getir
    """
    try:
        # Slug'dan robotu bul
        robot = Robot.objects.get(
            name__icontains=slug.replace('-', ' ')
        )
        
        # Yetki kontrolü
        if not request.user.is_staff and not request.user.is_superuser:
            if not hasattr(request.user, 'profil') or not request.user.profil.brand:
                return Response(
                    {'detail': 'Bu robota erişim yetkiniz yok.'},
                    status=status.HTTP_403_FORBIDDEN
                )
            if robot.brand != request.user.profil.brand:
                return Response(
                    {'detail': 'Bu robota erişim yetkiniz yok.'},
                    status=status.HTTP_403_FORBIDDEN
                )
        
        serializer = RobotSerializer(robot)
        return Response(serializer.data)
        
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
            return Robot.objects.get(product_name__icontains=slug)
        except Robot.DoesNotExist:
            return None
    
    def post(self, request, slug, format=None):
        try:
            robot = self.get_robot_by_slug(slug)
            if not robot:
                return Response(
                    {'error': 'Robot bulunamadı!'}, 
                    status=status.HTTP_404_NOT_FOUND
                )

            message = request.data.get('message', '')
            if not message:
                return Response(
                    {'error': 'Mesaj boş olamaz!'}, 
                    status=status.HTTP_400_BAD_REQUEST
                )

            # Thread pool ile asenkron işlem
            with ThreadPoolExecutor() as executor:
                future = executor.submit(robot.process_chat_message, request.user, message)
                try:
                    response = future.result(timeout=55)  # 55 saniye timeout
                    return Response(response)
                except TimeoutError:
                    return Response(
                        {'error': 'İşlem zaman aşımına uğradı. Lütfen tekrar deneyin.'}, 
                        status=status.HTTP_504_GATEWAY_TIMEOUT
                    )

        except Exception as e:
            print(f"ERROR in chat: {str(e)}")
            return Response(
                {'error': 'Bir hata oluştu. Lütfen tekrar deneyin.'}, 
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )


 