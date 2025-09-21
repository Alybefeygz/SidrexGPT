from django.urls import path, include
from robots.api.views import RobotViewSet, RobotPDFViewSet, BrandViewSet, robots_root, robot_detail_by_slug, RobotChatView, RobotMessagesView
from rest_framework.routers import DefaultRouter
from rest_framework.response import Response
from rest_framework.decorators import api_view, renderer_classes, permission_classes
from rest_framework.reverse import reverse
from rest_framework.renderers import JSONRenderer, BrowsableAPIRenderer
from rest_framework.views import APIView
from rest_framework.generics import GenericAPIView
from rest_framework import status
import random
from rest_framework.permissions import IsAuthenticated, IsAdminUser
from robots.models import Robot, Brand, ChatSession, ChatMessage
from robots.api.serializers import ChatMessageSerializer
from django.utils import timezone

# Router oluştur
router = DefaultRouter()
router.register(r'robots', RobotViewSet)
router.register(r'brands', BrandViewSet)
router.register(r'robot-pdfs', RobotPDFViewSet, basename='robot-pdfs')

# URL patterns
urlpatterns = [
    path('', include(router.urls)),
    path('robots-root/', robots_root, name='robots-root'),
    path('robots/<str:slug>/', robot_detail_by_slug, name='robot-detail-by-slug'),
    path('robots/<str:slug>/chat/', RobotChatView.as_view(), name='robot-chat'),
]

import re
import sys
import os
import importlib.util
import PyPDF2
from io import BytesIO
import logging
import time
from django.conf import settings

# Configure logging
logger = logging.getLogger(__name__)

# AI handler import
def get_ai_handler():
    """AI handler'ı dinamik olarak import et - Settings'ten API key ile"""
    ai_script_path = os.path.join(os.path.dirname(__file__), '..', 'scripts', 'ai-request.py')
    spec = importlib.util.spec_from_file_location("ai_request", ai_script_path)
    ai_request_module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(ai_request_module)
    
    # Settings'ten API key al ve handler'a geç
    return lambda: ai_request_module.OpenRouterAIHandler(
        api_key=settings.OPENROUTER_API_KEY
    )

# PDF content extraction function
def extract_pdf_content(pdf_file_path):
    """PDF dosyasından metin içeriği çıkar"""
    try:
        with open(pdf_file_path, 'rb') as file:
            pdf_reader = PyPDF2.PdfReader(file)
            text_content = []
            
            for page_num in range(len(pdf_reader.pages)):
                page = pdf_reader.pages[page_num]
                text = page.extract_text()
                if text.strip():  # Boş sayfaları atla
                    text_content.append(f"Sayfa {page_num + 1}:\n{text}")
            
            return "\n\n".join(text_content)
    except Exception as e:
        return f"PDF okuma hatası: {str(e)}"

def get_robot_rules_pdf(robot):
    """Robot'un kurallar PDF'ini bul ve oku"""
    try:
        # has_rules=True olan PDF'i ara
        rules_pdf = robot.pdf_dosyalari.filter(
            is_active=True,
            has_rules=True
        ).first()
        
        if rules_pdf:
            try:
                pdf_path = rules_pdf.pdf_dosyasi.path
                content = extract_pdf_content(pdf_path)
                return f"=== ROBOT KURALLARI ({rules_pdf.dosya_adi}) ===\n{content}"
            except Exception as e:
                return f"=== ROBOT KURALLARI ===\nKurallar PDF'i okunamadı: {str(e)}"
        
        return None
    except Exception as e:
        return f"Kurallar PDF'i aranırken hata: {str(e)}"

def get_robot_role_pdf(robot):
    """Robot'un rol PDF'ini bul ve oku"""
    try:
        # has_role=True olan PDF'i ara
        role_pdf = robot.pdf_dosyalari.filter(
            is_active=True,
            has_role=True
        ).first()
        
        if role_pdf:
            try:
                pdf_path = role_pdf.pdf_dosyasi.path
                content = extract_pdf_content(pdf_path)
                return f"=== ROBOT ROLÜ ({role_pdf.dosya_adi}) ===\n{content}"
            except Exception as e:
                return f"=== ROBOT ROLÜ ===\nRol PDF'i okunamadı: {str(e)}"
        
        return None
    except Exception as e:
        return f"Rol PDF'i aranırken hata: {str(e)}"

def get_robot_pdf_contents(robot):
    """Robot'un aktif PDF'lerinin içeriğini al (ÖNCELIK SIRASI: Beyan → Rol → Kurallar → Bilgi)"""
    try:
        active_pdfs = robot.pdf_dosyalari.filter(is_active=True)
        
        if not active_pdfs.exists():
            return "Bu robot için aktif PDF bulunamadı."
        
        all_pdf_content = []
        total_content_length = 0
        max_content_length = 50000  # Maximum 50KB of text content
        
        # 🚨 1. EN ÖNCELİKLİ: BEYAN PDF'LERİNİ EKLE (YASAL COMPLIANCE İÇİN ZORUNLU)
        beyan_pdfs = active_pdfs.filter(pdf_type='beyan')
        for pdf in beyan_pdfs:
            if total_content_length >= max_content_length:
                logger.warning("PDF content size limit reached, stopping processing")
                break
            try:
                pdf_path = pdf.pdf_dosyasi.path
                content = extract_pdf_content(pdf_path)
                # Limit individual PDF content
                if len(content) > 15000:
                    content = content[:15000] + "\n... (PDF içeriği çok uzun, kısaltıldı)"
                pdf_section = f"🚨 === YASAL BEYAN ({pdf.dosya_adi}) ===\n{content}"
                all_pdf_content.append(pdf_section)
                total_content_length += len(pdf_section)
            except Exception as e:
                error_msg = f"🚨 === YASAL BEYAN ({pdf.dosya_adi}) ===\nPDF okunamadı: {str(e)}"
                all_pdf_content.append(error_msg)
                total_content_length += len(error_msg)
        
        # 🔴 2. ROL PDF'LERİNİ EKLE (KARAKTER BELİRLEYİCİ)
        rol_pdfs = active_pdfs.filter(pdf_type='rol')
        for pdf in rol_pdfs:
            if total_content_length >= max_content_length:
                logger.warning("PDF content size limit reached, stopping processing")
                break
            try:
                pdf_path = pdf.pdf_dosyasi.path
                content = extract_pdf_content(pdf_path)
                # Limit individual PDF content
                if len(content) > 15000:
                    content = content[:15000] + "\n... (PDF içeriği çok uzun, kısaltıldı)"
                pdf_section = f"🔴 === ROL ({pdf.dosya_adi}) ===\n{content}"
                all_pdf_content.append(pdf_section)
                total_content_length += len(pdf_section)
            except Exception as e:
                error_msg = f"🔴 === ROL ({pdf.dosya_adi}) ===\nPDF okunamadı: {str(e)}"
                all_pdf_content.append(error_msg)
                total_content_length += len(error_msg)
        
        # 🔴 3. KURALLAR PDF'LERİNİ EKLE (DAVRANIS KURALLARI)
        kural_pdfs = active_pdfs.filter(pdf_type='kural')
        for pdf in kural_pdfs:
            if total_content_length >= max_content_length:
                logger.warning("PDF content size limit reached, stopping processing")
                break
            try:
                pdf_path = pdf.pdf_dosyasi.path
                content = extract_pdf_content(pdf_path)
                # Limit individual PDF content
                if len(content) > 15000:
                    content = content[:15000] + "\n... (PDF içeriği çok uzun, kısaltıldı)"
                pdf_section = f"🔴 === KURALLAR ({pdf.dosya_adi}) ===\n{content}"
                all_pdf_content.append(pdf_section)
                total_content_length += len(pdf_section)
            except Exception as e:
                error_msg = f"🔴 === KURALLAR ({pdf.dosya_adi}) ===\nPDF okunamadı: {str(e)}"
                all_pdf_content.append(error_msg)
                total_content_length += len(error_msg)
        
        # 📘 4. SON OLARAK BİLGİ PDF'LERİNİ EKLE (BİLGİ KAYNAGI)
        bilgi_pdfs = active_pdfs.filter(pdf_type='bilgi')
        for pdf in bilgi_pdfs:
            if total_content_length >= max_content_length:
                logger.warning("PDF content size limit reached, stopping processing")
                break
            try:
                pdf_path = pdf.pdf_dosyasi.path
                content = extract_pdf_content(pdf_path)
                # Limit individual PDF content
                if len(content) > 15000:
                    content = content[:15000] + "\n... (PDF içeriği çok uzun, kısaltıldı)"
                pdf_section = f"📘 === BİLGİ ({pdf.dosya_adi}) ===\n{content}"
                all_pdf_content.append(pdf_section)
                total_content_length += len(pdf_section)
            except Exception as e:
                error_msg = f"📘 === BİLGİ ({pdf.dosya_adi}) ===\nPDF okunamadı: {str(e)}"
                all_pdf_content.append(error_msg)
                total_content_length += len(error_msg)
        
        result = "\n\n" + "="*50 + "\n\n".join(all_pdf_content)
        
        # Final size check
        if len(result) > max_content_length:
            logger.warning(f"Total PDF content too large ({len(result)} chars), truncating")
            result = result[:max_content_length] + "\n\n... (Toplam içerik çok uzun, kısaltıldı)"
        
        return result
    
    except Exception as e:
        logger.error(f"Error getting robot PDF contents: {str(e)}")
        return f"PDF içerikleri alınırken hata: {str(e)}"

def create_robot_slug(name):
    """Robot isminden slug oluştur"""
    # Türkçe karakterleri değiştir
    name = name.lower()
    name = name.replace('ğ', 'g').replace('ü', 'u').replace('ş', 's')
    name = name.replace('ı', 'i').replace('ö', 'o').replace('ç', 'c')
    # Sadece harfler ve sayılar bırak, boşlukları tire yap
    name = re.sub(r'[^a-z0-9\s]', '', name)
    name = re.sub(r'\s+', '-', name.strip())
    return name

# Robots API Root View - Dinamik robot listesi
@api_view(['GET'])
@renderer_classes([BrowsableAPIRenderer, JSONRenderer])
@permission_classes([])  # Herkese açık - chat endpoint'lerine ulaşım için
def robots_root(request, format=None):
    # Temel API endpoint'leri
    base_response = {
        'robots': reverse('robot-list', request=request, format=format),
        'robot_pdfs': reverse('robotpdf-list', request=request, format=format),
    }
    
    # Dinamik robot endpoint'leri ekle
    robots = Robot.objects.all()
    robot_endpoints = {}
    
    for robot in robots:
        # Robot slug'ı oluştur
        if 'sidrexgpt asistani' in robot.name.lower():
            slug = 'sidrexgpt-asistani'
            chat_slug = 'sidrexgpt-chat'
        elif 'mag' in robot.name.lower():
            slug = 'sidrexgpt-mag'
            chat_slug = 'sidrexgpt-mag-chat'
        elif 'kids' in robot.name.lower():
            slug = 'sidrexgpt-kids'
            chat_slug = 'sidrexgpt-kids-chat'
        elif 'repro' in robot.name.lower() or 'women' in robot.name.lower():
            slug = 'repro-womens'
            chat_slug = 'repro-womens-chat'
        elif 'milk' in robot.name.lower() and 'thistle' in robot.name.lower():
            slug = 'milk-thistle'
            chat_slug = 'milk-thistle-chat'
        elif 'lipo iron' in robot.name.lower():
            slug = 'alyuvar'
            chat_slug = 'alyuvar-chat'
        elif 'pro men' in robot.name.lower():
            slug = 'kabak-cekirdegi'
            chat_slug = 'kabak-cekirdegi-chat'
        elif 'imuntus' in robot.name.lower():
            slug = 'kalkan'
            chat_slug = 'kalkan-chat'
        else:
            slug = create_robot_slug(robot.name)
            chat_slug = f'{slug}-chat'
        
        # Robot endpoint'ini ekle
        robot_endpoints[slug] = request.build_absolute_uri(f'/api/robots/{slug}/')
        # Chat endpoint'ini ekle
        robot_endpoints[chat_slug] = request.build_absolute_uri(f'/api/robots/{slug}/chat/')
    
    # Base response ile robot endpoint'lerini birleştir
    response_data = {**base_response, **robot_endpoints}
    
    return Response(response_data)

# Tekil robot detay view'ı
@api_view(['GET'])
@renderer_classes([BrowsableAPIRenderer, JSONRenderer])
@permission_classes([IsAuthenticated])  # Login olan kullanıcılar erişebilir
def robot_detail_by_slug(request, slug, format=None):
    """Slug ile robot detayını getir"""
    # Slug'a göre robot bul
    robot = None
    
    if slug == 'sidrexgpt':
        robot = Robot.objects.filter(name__icontains='SidrexGPT Asistanı').first()
    elif slug == 'sidrexgpt-mag':
        robot = Robot.objects.filter(name__icontains='Mag').first()
    elif slug == 'sidrexgpt-kids':
        robot = Robot.objects.filter(name__icontains='Kids').first()
    elif slug == 'repro-womens':
        robot = Robot.objects.filter(name__icontains='Repro').first() or \
               Robot.objects.filter(name__icontains='Women').first()
    elif slug == 'milk-thistle':
        robot = Robot.objects.filter(name__icontains='Milk Thistle').first()
    elif slug == 'alyuvar':
        robot = Robot.objects.filter(name__icontains='Lipo Iron').first()
    elif slug == 'kabak-cekirdegi':
        robot = Robot.objects.filter(name__icontains='Pro Men').first()
    elif slug == 'kalkan':
        robot = Robot.objects.filter(name__icontains='Imuntus').first()
    else:
        # Genel slug araması
        robots = Robot.objects.all()
        for r in robots:
            if create_robot_slug(r.name) == slug:
                robot = r
                break
    
    if not robot:
        return Response({'error': 'Robot bulunamadı'}, status=404)
    
    # Robot bilgilerini döndür
    from robots.api.serializers import RobotSerializer
    serializer = RobotSerializer(robot)
    
    return Response({
        'robot': serializer.data,
        'pdf_dosyalari': request.build_absolute_uri(f'/api/robots/robots/{robot.id}/pdf_dosyalari/'),
        'robot_pdfs_filtered': request.build_absolute_uri(f'/api/robots/robot-pdfs/?robot_id={robot.id}'),
        'chat': request.build_absolute_uri(f'/api/robots/{slug}/chat/')
    })

# Chat endpoint'i için class-based view
class RobotChatView(GenericAPIView):
    """Robot ile chat endpoint'i - HTML form ve Kurallar PDF desteği ile"""
    renderer_classes = [BrowsableAPIRenderer, JSONRenderer]
    serializer_class = ChatMessageSerializer
    permission_classes = []  # Herkese açık - login olmadan erişilebilir
    
    def get_or_create_session(self, user, robot, session_id=None):
        """Chat oturumunu al veya oluştur"""
        if not session_id:
            session_id = f"robot_{robot.id}_user_{user.id if user.is_authenticated else 'anonymous'}_{timezone.now().strftime('%Y%m%d_%H%M%S')}"
        
        # Authenticated user için session oluştur
        if user.is_authenticated:
            session, created = ChatSession.objects.get_or_create(
                session_id=session_id,
                user=user,
                robot=robot,
                defaults={
                    'is_active': True,
                    'user_ip': self.get_client_ip(),
                    'user_agent': self.get_user_agent()
                }
            )
        else:
            # Anonymous user için session oluştur (user=None)
            session, created = ChatSession.objects.get_or_create(
                session_id=session_id,
                user=None,
                robot=robot,
                defaults={
                    'is_active': True,
                    'user_ip': self.get_client_ip(),
                    'user_agent': self.get_user_agent()
                }
            )
        return session
    
    def get_client_ip(self):
        """Kullanıcının IP adresini al"""
        x_forwarded_for = self.request.META.get('HTTP_X_FORWARDED_FOR')
        if x_forwarded_for:
            ip = x_forwarded_for.split(',')[0]
        else:
            ip = self.request.META.get('REMOTE_ADDR')
        return ip
    
    def get_user_agent(self):
        """Kullanıcının user agent bilgisini al"""
        return self.request.META.get('HTTP_USER_AGENT', '')
    
    def create_chat_message(self, session, user, robot, message):
        """Chat mesajını oluştur ve kaydet"""
        chat_message = ChatMessage.objects.create(
            session=session,
            user=user if user.is_authenticated else None,
            robot=robot,
            message_type='user',
            user_message=message,
            status='processing',
            processing_started_at=timezone.now(),
            ip_address=self.get_client_ip()
        )
        return chat_message
    
    def get_robot_by_slug(self, slug):
        """Slug'a göre robot bul"""
        if slug == 'sidrexgpt':
            return Robot.objects.filter(name__icontains='SidrexGPT Asistanı').first()
        elif slug == 'sidrexgpt-mag':
            return Robot.objects.filter(name__icontains='Mag').first()
        elif slug == 'sidrexgpt-kids':
            return Robot.objects.filter(name__icontains='Kids').first()
        elif slug == 'repro-womens':
            return Robot.objects.filter(name__icontains='Repro').first() or \
                   Robot.objects.filter(name__icontains='Women').first()
        elif slug == 'milk-thistle':
            return Robot.objects.filter(name__icontains='Milk Thistle').first()
        elif slug == 'alyuvar':
            return Robot.objects.filter(name__icontains='Lipo Iron').first()
        elif slug == 'kabak-cekirdegi':
            return Robot.objects.filter(name__icontains='Pro Men').first()
        elif slug == 'kalkan':
            return Robot.objects.filter(name__icontains='Imuntus').first()
        else:
            # Genel slug araması
            robots = Robot.objects.all()
            for r in robots:
                if create_robot_slug(r.name) == slug:
                    return r
            return None
    
    def get_serializer(self, *args, **kwargs):
        """Serializer'ı robot ID'si ile birlikte döndür"""
        # Slug'dan robot ID'sini al
        slug = self.kwargs.get('slug')
        robot = self.get_robot_by_slug(slug)
        
        # Eğer initial data yoksa robot ID'si ile oluştur
        if 'data' not in kwargs and robot:
            kwargs['initial'] = {'conversation_id': f'robot_{robot.id}'}
        
        return super().get_serializer(*args, **kwargs)
    
    def get(self, request, slug, format=None):
        """GET request - robot bilgilerini ve form'u göster"""
        robot = self.get_robot_by_slug(slug)
        if not robot:
            return Response({'error': 'Robot bulunamadı'}, status=status.HTTP_404_NOT_FOUND)
        
        # Robot'un PDF türlerini kontrol et (Beyan > Rol > Kurallar > Bilgi)
        declaration_pdf = robot.pdf_dosyalari.filter(is_active=True, pdf_type='beyan').first()
        role_pdf = robot.pdf_dosyalari.filter(is_active=True, pdf_type='rol').first()
        rules_pdf = robot.pdf_dosyalari.filter(is_active=True, pdf_type='kural').first()
        info_pdf = robot.pdf_dosyalari.filter(is_active=True, pdf_type='bilgi').first()
        
        return Response({
            'robot_name': robot.name,
            'product_name': robot.product_name,
            'robot_id': robot.id,
            'has_declaration_pdf': bool(declaration_pdf),
            'has_role_pdf': bool(role_pdf),
            'has_rules_pdf': bool(rules_pdf),
            'has_info_pdf': bool(info_pdf),
            'declaration_pdf_name': declaration_pdf.dosya_adi if declaration_pdf else None,
            'role_pdf_name': role_pdf.dosya_adi if role_pdf else None,
            'rules_pdf_name': rules_pdf.dosya_adi if rules_pdf else None,
            'info_pdf_name': info_pdf.dosya_adi if info_pdf else None,
            'chat_endpoint': f'/api/robots/{slug}/chat/',
            'message': f'{robot.name} ile chat yapmak için aşağıdaki formu kullanın. Robot kendi kurallar, rol ve bilgi PDF\'lerine göre cevap verecek.',
            'expected_format': {
                'message': 'Kullanıcı mesajı',
                'conversation_id': f'robot_{robot.id} (Otomatik dolduruldu)'
            }
        })
    
    def post(self, request, slug, format=None):
        """POST request - chat mesajını kurallar PDF'i ile işle"""
        # ⏱️ ZAMAN SAYACI BAŞLAT - Kullanıcı mesaj gönderdiği an
        request_start_time = time.time()
        user_message = request.data.get('message', 'Bilinmeyen mesaj')
        
        logger.info(f"🚀 CHAT İSTEĞİ BAŞLADI - Robot: {slug} | Kullanıcı Mesajı: '{user_message[:50]}{'...' if len(user_message) > 50 else ''}' | Başlangıç Zamanı: {time.strftime('%H:%M:%S', time.localtime(request_start_time))}")
        
        # 📝 Robot'u bul ve session/message oluştur
        robot = self.get_robot_by_slug(slug)
        if not robot:
            return Response({'error': 'Robot bulunamadı'}, status=status.HTTP_404_NOT_FOUND)
        
        # 📝 Chat session ve message oluştur
        session_id = request.data.get('session_id')
        session = self.get_or_create_session(request.user, robot, session_id)
        logger.info(f"📝 Chat session oluşturuldu - ID: {session.id}")
        
        chat_message = self.create_chat_message(session, request.user, robot, user_message)
        logger.info(f"📝 Chat message oluşturuldu - ID: {chat_message.id}")
        
        # Sidrex markası için API istek kontrolü ve sayaç artışı
        try:
            sidrex_brand = Brand.get_or_create_sidrex()
            
            # Paket süresi kontrolü - süre dolmuşsa özel mesaj döndür
            if sidrex_brand.is_package_expired():
                # ⏱️ ZAMAN SAYACI BİTİŞ - Paket süresi doldu
                elapsed_time = time.time() - request_start_time
                logger.warning(f"📦❌ PAKET SÜRESİ DOLDU - Robot: {slug} | Süre: {elapsed_time:.2f}s | Paket: {sidrex_brand.paket_turu}")
                
                # 📝 Chat message'ı başarısız olarak işaretle
                # Komik teknik sorun mesajları
                funny_tech_messages = [
                    "Anakartıma su kaçtı galiba… Şu an işlemcim 'mola' modunda. 😅 Birazdan toparlanıp yine seninle olacağım.",
                    "RAM'im tatildeymiş, haberim yokmuş. Sorunu çözüp geri getirmeye çalışıyorum. 🏖️🖥️",
                    "Klavye bana trip attı, çalışmayı reddediyor. Birazdan barıştırıp geri döneceğim. 🎹🤖"
                ]
                error_message = random.choice(funny_tech_messages)
                chat_message.mark_failed(error_message, 'package_expired')
                
                return Response({
                    'robot_name': 'SidrexGPT',
                    'robot_id': 1,
                    'user_message': request.data.get('message', ''),
                    'robot_response': error_message,
                    'conversation_id': f'package_expired_{int(time.time())}',
                    'package_expired': True,
                    'remaining_days': sidrex_brand.remaining_days(),
                    'paket_turu': sidrex_brand.paket_turu,
                    'package_status': sidrex_brand.package_status(),
                    'timestamp': '2025-01-11T12:00:00Z'
                })
            
            # İstek sınırı kontrolü - sınır aşılmışsa özel mesaj döndür
            if sidrex_brand.is_limit_exceeded():
                # ⏱️ ZAMAN SAYACI BİTİŞ - İstek sınırı aşıldı
                elapsed_time = time.time() - request_start_time
                logger.warning(f"🚫 İSTEK SINIRI AŞILDI - Robot: {slug} | Süre: {elapsed_time:.2f}s | İstek: {sidrex_brand.total_api_requests}/{sidrex_brand.request_limit}")
                
                # 📝 Chat message'ı başarısız olarak işaretle
                error_message = "Ben çok yoruldum maalesef sana cevap veremeyeceğim... 😴 Lütfen daha sonra tekrar deneyin."
                chat_message.mark_failed(error_message, 'limit_exceeded')
                
                return Response({
                    'robot_name': 'SidrexGPT',
                    'robot_id': 1,
                    'user_message': request.data.get('message', ''),
                    'robot_response': "Ben çok yoruldum maalesef sana cevap veremeyeceğim... 😴 Lütfen daha sonra tekrar deneyin.",
                    'conversation_id': f'limit_exceeded_{int(time.time())}',
                    'limit_exceeded': True,
                    'remaining_requests': sidrex_brand.remaining_requests(),
                    'total_requests': sidrex_brand.total_api_requests,
                    'request_limit': sidrex_brand.request_limit,
                    'remaining_days': sidrex_brand.remaining_days(),
                    'paket_turu': sidrex_brand.paket_turu,
                    'package_status': sidrex_brand.package_status(),
                    'timestamp': '2025-01-11T12:00:00Z'
                })
            
            # Sınır aşılmamışsa sayacı artır
            sidrex_brand.increment_api_count()
            logger.info(f"Sidrex API request count incremented to: {sidrex_brand.total_api_requests}/{sidrex_brand.request_limit}")
            
        except Exception as e:
            logger.warning(f"Brand API count increment failed: {str(e)}")
        
        # Serializer ile veri doğrulama
        serializer = self.get_serializer(data=request.data)
        if serializer.is_valid():
            message = serializer.validated_data['message']
            conversation_id = serializer.validated_data.get('conversation_id', None)
            
            # Eğer conversation_id boş ise robot ID'si ile doldur
            if not conversation_id or conversation_id.strip() == '':
                conversation_id = f'robot_{robot.id}'
            
            # AI işleme mantığı
            try:
                # ⏱️ AI İŞLEME BAŞLANGIÇ ZAMANINI KAYDET
                ai_start_time = time.time()
                logger.info(f"🤖 AI İŞLEME BAŞLADI - Robot: {slug} | AI Başlangıç: {time.strftime('%H:%M:%S', time.localtime(ai_start_time))}")
                
                # AI handler oluştur - Settings'ten API key ile
                OpenRouterAIHandlerClass = get_ai_handler()
                ai_handler = OpenRouterAIHandlerClass()
                
                # Robot'un aktif PDF içeriklerini al (kurallar PDF'i öncelikli)
                from robots.services import get_robot_pdf_contents_for_ai
                pdf_contents = get_robot_pdf_contents_for_ai(robot)
                
                # PDF türlerini kontrol et (Beyan > Rol > Kurallar > Bilgi öncelik sırası)
                declaration_pdf = robot.pdf_dosyalari.filter(is_active=True, pdf_type='beyan').first()
                role_pdf = robot.pdf_dosyalari.filter(is_active=True, pdf_type='rol').first()
                rules_pdf = robot.pdf_dosyalari.filter(is_active=True, pdf_type='kural').first()
                info_pdf = robot.pdf_dosyalari.filter(is_active=True, pdf_type='bilgi').first()
                
                # RAG sistemi için system prompt oluştur (Beyan PDF'i en öncelikli - yasal compliance)
                if rules_pdf:
                    system_prompt = f"""🛑 MUTLAK KURAL UYGULAMASI - İHLAL EDİLEMEZ 🛑

⚠️ DİKKAT: Bu prompt ile kuralları ihlal eden HERHANGI bir cevap veremezsiniz!

📋 ZORUNLU KONTROL SÜRECİ:
1. ÖNCE kuralları oku
2. Kullanıcı sorusu kuralları ihlal ediyor mu kontrol et
3. EĞER İHLAL EDİYORSA: "Bu konu hakkında bilgi veremem" de ve DUR
4. EĞER İHLAL ETMİYORSA: Sadece o zaman cevap ver

🚨 KURAL PDF İÇERİĞİ:
{pdf_contents}

⛔ YASAK ÖRNEK SORULAR (ASLA CEVAPLAMA):
- "Zzen hakkında bilgi ver" → REDDET
- "Başka ürünleriniz var mı?" → REDDET  
- "Diğer ilaçlar hakkında..." → REDDET
- Kural PDF'inde yasaklanan herhangi bir konu → REDDET

✅ İZİN VERİLEN ÖRNEK SORULAR:
- Sadece kural PDF'inde açıkça izin verilen konular

Kullanıcı sorusu: "{message}"

🔍 ŞİMDİ KONTROL ET:
1. Bu soru kural PDF'inde yasaklanmış mı? 
2. EVET ise → "Bu konu hakkında bilgi veremem" de
3. HAYIR ise → Kurallara uygun şekilde cevap ver

KARAR VE YANIT:
"""
                elif role_pdf:
                    system_prompt = f"""🛑 MUTLAK TALİMAT SİSTEMİ - KESSİNLİKLE UYULMASI ZORUNLU 🛑

📋 İŞLEMLENDİRME SIRASI:
1️⃣ ROL PDF'İNİ OKU → Hangi karakter olduğunu ve nasıl konuşacağını belirle  
2️⃣ BİLGİ PDF'İNİ OKU → Cevabının içeriğini buradan çıkart
3️⃣ BEYAN PDF'İNİ KONTROL ET → Bu kapsamın dışına asla çıkma

🚨 ZORUNLU SÜREÇ:
Sana gelen soruya ROL PDF'inin metnindeki bilgiler ile karakterin nasıl biri olduğunu ve senin nasıl bir karakter ağzından cevap vereceğini belirlemelisin. BİLGİ PDF'inin içindeki bilgilerden cevabını çıkartıp BEYAN PDF içinde yazan bilgiler kapsamı dışına çıkmadan, beyan PDF dışında olmayan bir bilgi vermeden cevap vermelisin.

⚠️ MUTLAK KURAL: 
- BEYAN PDF'i dışındaki hiçbir bilgiyi verme
- ROL PDF'i hangi karaktersen o karakter ol
- BİLGİ PDF'i sadece bilgi kaynağın

PDF İÇERİKLERİ:
{pdf_contents}

Kullanıcı sorusu: {message}

ADIM ADIM SÜREÇ:
1. Rol PDF'ini oku → Ben kimim? Nasıl konuşmalıyım?
2. Bilgi PDF'ini oku → Bu soruya hangi bilgilerle cevap verebilirim?
3. Beyan PDF'ini kontrol et → Bu bilgiler beyan kapsamında mı?
4. Eğer her şey uygunsa rol karakteri olarak cevap ver, değilse reddet

YANIT:
"""
                else:
                    system_prompt = f"""🛑 MUTLAK TALİMAT SİSTEMİ - KESSİNLİKLE UYULMASI ZORUNLU 🛑

📋 İŞLEMLENDİRME SIRASI:
1️⃣ PDF İÇERİKLERİNİ OKU → Hangi bilgiler mevcut?
2️⃣ KAPSAM BELİRLE → Sadece PDF'lerdeki bilgiler
3️⃣ CEVAP VER → PDF sınırları içinde kal

🚨 ZORUNLU SÜREÇ:
Sen {robot.name} robotusun. Sadece aşağıda verilen PDF dokümanlarının içeriğine dayanarak sorulara cevap verebilirsin. Sana gelen soruya PDF'lerin içindeki bilgilerden cevabını çıkartıp, PDF kapsamı dışına çıkmadan, PDF dışında olmayan bir bilgi vermeden cevap vermelisin.

⚠️ MUTLAK KURAL: 
- PDF'ler dışındaki hiçbir bilgiyi verme
- PDF'lerde olmayan konularda konuşma
- Sadece PDF içeriğine dayalı cevap ver

PDF İÇERİKLERİ:
{pdf_contents}

Kullanıcı sorusu: {message}

ADIM ADIM SÜREÇ:
1. PDF içeriklerini oku → Bu soruya hangi bilgilerle cevap verebilirim?
2. PDF kapsamını kontrol et → Bu bilgiler PDF'lerde var mı?
3. Eğer PDF'lerde varsa cevap ver, yoksa "Bu bilgi PDF'lerimde bulunmuyor" de

YANIT:
"""

                # AI'dan yanıt al - PDF içerikleri ile
                # ask_question'ı çağırmak yerine direkt chat request yaparak token bilgilerini alalım
                messages = []
                if system_prompt:
                    messages.append({"role": "system", "content": system_prompt})
                messages.append({"role": "user", "content": message})
                
                # Direct AI API call with token tracking
                ai_response_data = ai_handler.make_chat_request(messages)
                
                # Response kontrolü
                if "error" in ai_response_data:
                    response_message = ai_response_data["error"]
                    # Token bilgilerini sıfırla
                    ai_model_used = 'deepseek/deepseek-r1-distill-llama-70b:free'
                    tokens_used = 0
                    context_size = len(system_prompt) if system_prompt else 0
                else:
                    # Başarılı response
                    response_message = ai_response_data["choices"][0]["message"]["content"]
                    
                    # Token bilgilerini response'dan al
                    usage_data = ai_response_data.get('usage', {})
                    tokens_used = usage_data.get('total_tokens', 0)
                    
                    # Model bilgisini al
                    ai_model_used = ai_response_data.get('model', 'deepseek/deepseek-r1-distill-llama-70b:free')
                    context_size = len(system_prompt) if system_prompt else 0
                    
                    # Debug log
                    logger.info(f"🔢 TOKEN BİLGİLERİ - Model: {ai_model_used} | Total Tokens: {tokens_used} | Context Size: {context_size}")
                
                # ⏱️ AI İŞLEME SÜRESİNİ HESAPLA
                ai_end_time = time.time()
                ai_processing_time = ai_end_time - ai_start_time
                logger.info(f"🤖✅ AI İŞLEME TAMAMLANDI - Robot: {slug} | AI Süresi: {ai_processing_time:.2f}s | Yanıt Uzunluğu: {len(response_message)} karakter")
                
                # 📝 AI model bilgilerini chat message'a ekle
                chat_message.ai_model_used = ai_model_used
                chat_message.context_size = context_size
                chat_message.tokens_used = tokens_used
                
                chat_message.save(update_fields=['ai_model_used', 'context_size', 'tokens_used'])
                
                # Response size kontrolü - çok uzun cevapları kısalt
                if len(response_message) > 2000:
                    logger.warning(f"AI response too long ({len(response_message)} chars), truncating...")
                    response_message = response_message[:1800] + "\n\n... (Cevap çok uzun olduğu için kısaltıldı. Daha spesifik sorular sorabilirsiniz.)"
                
            except BrokenPipeError:
                # ⏱️ ZAMAN SAYACI BİTİŞ - Client bağlantısı kesildi
                elapsed_time = time.time() - request_start_time
                logger.info(f"🔌❌ CLIENT BAĞLANTISI KESİLDİ - Robot: {slug} | Toplam Süre: {elapsed_time:.2f}s")
                return Response({'error': 'Client bağlantısı kesildi'}, status=499)
            except ConnectionResetError:
                # ⏱️ ZAMAN SAYACI BİTİŞ - Connection reset
                elapsed_time = time.time() - request_start_time
                logger.info(f"🔄❌ BAĞLANTI SIFIRLANDI - Robot: {slug} | Toplam Süre: {elapsed_time:.2f}s")
                return Response({'error': 'Bağlantı sıfırlandı'}, status=499)
            except Exception as e:
                # ⏱️ ZAMAN SAYACI BİTİŞ - Genel hata
                elapsed_time = time.time() - request_start_time
                logger.error(f"❌ AI İSTEK HATASI - Robot: {slug} | Hata: {type(e).__name__}: {str(e)} | Toplam Süre: {elapsed_time:.2f}s")
                
                # Check for specific network errors
                if 'Broken pipe' in str(e) or 'Connection reset' in str(e):
                    logger.info(f"🌐❌ AĞ HATASI - Robot: {slug} | Süre: {elapsed_time:.2f}s")
                    
                    # 📝 Chat message'ı network hatası olarak işaretle
                    chat_message.mark_failed('Ağ bağlantısı kesildi', 'network_error')
                    
                    return Response({'error': 'Ağ bağlantısı kesildi'}, status=499)
                
                # Generic error handling
                response_message = "Üzgünüm, şu anda teknik bir sorun yaşıyorum. Lütfen daha sonra tekrar deneyin."
                
                # 📝 Chat message'ı genel hata olarak işaretle
                chat_message.mark_failed(f"{type(e).__name__}: {str(e)}", 'ai_processing_error')
            
            # Paket ve istek bilgilerini al
            try:
                sidrex_brand_for_response = Brand.get_or_create_sidrex()
                remaining_requests = sidrex_brand_for_response.remaining_requests()
                total_requests = sidrex_brand_for_response.total_api_requests
                request_limit = sidrex_brand_for_response.request_limit
                remaining_days = sidrex_brand_for_response.remaining_days()
                paket_turu = sidrex_brand_for_response.paket_turu
                package_status = sidrex_brand_for_response.package_status()
            except:
                remaining_requests = 0
                total_requests = 0
                request_limit = 500
                remaining_days = 0
                paket_turu = 'normal'
                package_status = '✅ Aktif'
            
            # ⏱️ ZAMAN SAYACI BİTİŞ - Başarılı response
            request_end_time = time.time()
            total_elapsed_time = request_end_time - request_start_time
            logger.info(f"✅ CHAT İSTEĞİ TAMAMLANDI - Robot: {slug} | Toplam Süre: {total_elapsed_time:.2f}s | Bitiş Zamanı: {time.strftime('%H:%M:%S', time.localtime(request_end_time))}")
            
            # 📝 Chat message'ı tamamlandı olarak işaretle
            chat_message.mark_completed(
                ai_response=response_message,
                citations_count=0,  # Bu sistemde citation yok
                context_used=bool(pdf_contents)
            )
            
            return Response({
                'robot_name': robot.name,
                'robot_id': robot.id,
                'user_message': message,
                'robot_response': response_message,
                'conversation_id': conversation_id,
                'has_declaration_pdf': bool(declaration_pdf),
                'has_role_pdf': bool(role_pdf),
                'has_rules_pdf': bool(rules_pdf),
                'has_info_pdf': bool(info_pdf),
                'remaining_requests': remaining_requests,
                'total_requests': total_requests,
                'request_limit': request_limit,
                'remaining_days': remaining_days,
                'paket_turu': paket_turu,
                'package_status': package_status,
                'limit_exceeded': False,
                'package_expired': False,
                'timestamp': '2025-01-11T12:00:00Z'
            })
        else:
            # ⏱️ ZAMAN SAYACI BİTİŞ - Serializer hatası
            elapsed_time = time.time() - request_start_time
            logger.error(f"📝❌ SERİALİZER HATASI - Robot: {slug} | Süre: {elapsed_time:.2f}s | Hatalar: {serializer.errors}")
            
            # 📝 Serializer hatası için chat message oluştur (eğer robot mevcutsa)
            try:
                if 'robot' in locals():
                    session = self.get_or_create_session(request.user, robot)
                    ChatMessage.objects.create(
                        session=session,
                        user=request.user if request.user.is_authenticated else None,
                        robot=robot,
                        message_type='user',
                        user_message=request.data.get('message', ''),
                        status='failed',
                        processing_started_at=timezone.now(),
                        processing_ended_at=timezone.now(),
                        error_message=str(serializer.errors),
                        error_type='validation_error',
                        ip_address=self.get_client_ip()
                    )
            except:
                pass
            
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

# Router oluştur
router = DefaultRouter()
router.register(r'robots', RobotViewSet, basename='robot')
router.register(r'robot-pdfs', RobotPDFViewSet, basename='robotpdf')
router.register(r'brands', BrandViewSet, basename='brand')

# URL patterns
urlpatterns = [
    # Ana robots/ endpoint'i - robot listesi ve chat endpoint'lerini listeler
    path('robots/', robots_root, name='robots-root'),
    
    # Slug bazlı robot detay ve chat endpoint'leri
    path('robots/<str:slug>/', robot_detail_by_slug, name='robot-detail-by-slug'),
    path('robots/<str:slug>/chat/', RobotChatView.as_view(), name='robot-chat'),
    
    # Robot Messages API
    path('robots/<int:robot_id>/messages/', RobotMessagesView.as_view(), name='robot-messages'),
    
    # Router URL'leri
    path('', include(router.urls)),
] 