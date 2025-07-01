from django.urls import path, include
from robots.api.views import RobotViewSet, RobotPDFViewSet, BrandViewSet, robots_root, robot_detail_by_slug, RobotChatView
from rest_framework.routers import DefaultRouter
from rest_framework.response import Response
from rest_framework.decorators import api_view, renderer_classes, permission_classes
from rest_framework.reverse import reverse
from rest_framework.renderers import JSONRenderer, BrowsableAPIRenderer
from rest_framework.views import APIView
from rest_framework.generics import GenericAPIView
from rest_framework import status
from rest_framework.permissions import IsAuthenticated, IsAdminUser
from robots.models import Robot, Brand
from robots.api.serializers import ChatMessageSerializer

# Router oluştur
router = DefaultRouter()
router.register(r'robots', RobotViewSet)
router.register(r'brands', BrandViewSet)

# URL patterns
urlpatterns = [
    path('', include(router.urls)),
    path('robots-root/', robots_root, name='robots-root'),
    path('robots/<str:slug>/', robot_detail_by_slug, name='robot-detail-by-slug'),
    path('robots/<str:slug>/chat/', RobotChatView.as_view(), name='robot-chat'),
]

# RobotPDF için özel router
pdf_router = DefaultRouter()
pdf_router.register(r'robot-pdfs', RobotPDFViewSet, basename='robot-pdfs')

# RobotPDF URL'lerini ana URL'lere ekle
urlpatterns += pdf_router.urls

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
    
    def get_robot_by_slug(self, slug):
        """Slug'a göre robot bul"""
        if slug == 'sidrexgpt':
            return Robot.objects.filter(name__icontains='SidrexGPT Asistanı').first()
        elif slug == 'sidrexgpt-mag':
            return Robot.objects.filter(name__icontains='Mag').first()
        elif slug == 'sidrexgpt-kids':
            return Robot.objects.filter(name__icontains='Kids').first()
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
        # Sidrex markası için API istek kontrolü ve sayaç artışı
        try:
            sidrex_brand = Brand.get_or_create_sidrex()
            
            # Paket süresi kontrolü - süre dolmuşsa özel mesaj döndür
            if sidrex_brand.is_package_expired():
                logger.warning(f"Package expired for Sidrex: {sidrex_brand.paket_turu} package")
                return Response({
                    'robot_name': 'SidrexGPT',
                    'robot_id': 1,
                    'user_message': request.data.get('message', ''),
                    'robot_response': "Paket sürem doldu maalesef sana cevap veremeyeceğim... ⏰ Lütfen paketinizi yenileyin.",
                    'conversation_id': f'package_expired_{int(time.time())}',
                    'package_expired': True,
                    'remaining_days': sidrex_brand.remaining_days(),
                    'paket_turu': sidrex_brand.paket_turu,
                    'package_status': sidrex_brand.package_status(),
                    'timestamp': '2025-01-11T12:00:00Z'
                })
            
            # İstek sınırı kontrolü - sınır aşılmışsa özel mesaj döndür
            if sidrex_brand.is_limit_exceeded():
                logger.warning(f"API request limit exceeded for Sidrex: {sidrex_brand.total_api_requests}/{sidrex_brand.request_limit}")
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
        
        robot = self.get_robot_by_slug(slug)
        if not robot:
            return Response({'error': 'Robot bulunamadı'}, status=status.HTTP_404_NOT_FOUND)
        
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
                # AI handler oluştur - Settings'ten API key ile
                OpenRouterAIHandlerClass = get_ai_handler()
                ai_handler = OpenRouterAIHandlerClass()
                
                # Robot'un aktif PDF içeriklerini al (kurallar PDF'i öncelikli)
                pdf_contents = get_robot_pdf_contents(robot)
                
                # PDF türlerini kontrol et (Beyan > Rol > Kurallar > Bilgi öncelik sırası)
                declaration_pdf = robot.pdf_dosyalari.filter(is_active=True, pdf_type='beyan').first()
                role_pdf = robot.pdf_dosyalari.filter(is_active=True, pdf_type='rol').first()
                rules_pdf = robot.pdf_dosyalari.filter(is_active=True, pdf_type='kural').first()
                info_pdf = robot.pdf_dosyalari.filter(is_active=True, pdf_type='bilgi').first()
                
                # RAG sistemi için system prompt oluştur (Beyan PDF'i en öncelikli - yasal compliance)
                if declaration_pdf:
                    system_prompt = f"""🚨 YASAL COMPLIANCE TALİMATLARI - KESSİNLİKLE UYULMASI ZORUNLU 🚨

🔥 EN ÖNCELİKLİ: YASAL BEYAN PDF'İ
Bu ilaç firması için yasal compliance zorunludur. BEYAN PDF'inde yazan cümlelerin dışına asla çıkamazsınız!

📋 ÖNCELIK SIRASI:
1. 🚨 YASAL BEYAN PDF'İ → Kesinlikle uyulması gereken yasal ifadeler (EN ÖNCELİKLİ)
2. 🔴 ROL PDF'İ → Karakter ve davranış belirleme  
3. 🔴 KURALLAR PDF'İ → Genel kurallar ve sınırlar
4. 📘 BİLGİ PDF'İ → Bilgi kaynağı

⚠️ YASAL UYARI: 
- Beyan PDF'indeki ifadelerin tamamen dışına çıkmak yasaktır
- İlaç endüstrisi düzenlemelerine uymak zorundasınız
- Sadece beyan PDF'inde belirtilen ifadeleri kullanabilirsiniz

PDF İÇERİKLERİ:
{pdf_contents}

Kullanıcı sorusu: {message}

ŞİMDİ YANIT VER: Önce beyan PDF'indeki yasal ifadeleri kontrol et, sonra rol belirleme yap, kuralları uygula ve bilgilerle destekle."""

                elif rules_pdf and role_pdf:
                    system_prompt = f"""KRİTİK TALİMATLAR - MUTLAKA UYULMASI ZORUNLU:

🔴 1. KURALLAR PDF'İ (İLK PDF): Bu PDF'de senin NASIL cevap vermen gerektiği yazılı. Bu kurallara MUTLAKA uy:
   - Karakter sınırları varsa kesinlikle aşma
   - Yanıt formatı belirtilmişse tam uy
   - Yasaklanan davranışlar varsa asla yapma
   - Bu kurallar her şeyden öncelikli!

🔴 2. ROL PDF'İ (İKİNCİ PDF): Bu PDF'de senin KİM olman gerektiği yazılı. Bu role TAMAMEN bürün:
   - Belirtilen kişiliği %100 benimse
   - O kişinin konuşma tarzıyla yanıtla
   - O kişinin bakış açısıyla değerlendir
   - Rol dışına çıkma!

🔴 3. MUTLAK ÖNCELIK SIRASI:
   1. KURALLAR PDF'İ → Her yanıtta kontrol et ve uy
   2. ROL PDF'İ → Her yanıtta bu kişilik olarak davran
   3. DİĞER PDF'LER → Bilgi kaynağı olarak kullan

⚠️ UYARI: Kurallar veya rol ihlali yapma! Bu PDF'lerdeki direktifler diğer her şeyden önemli!

PDF İÇERİKLERİ:
{pdf_contents}

Kullanıcı sorusu: {message}

ŞİMDİ YANIT VER: Önce kurallar PDF'ini kontrol et, sonra rol PDF'indeki kişiliği benimse, son olarak diğer PDF'lerden bilgi kullanarak soruyu yanıtla."""
                elif rules_pdf:
                    system_prompt = f"""KRİTİK TALİMATLAR - MUTLAKA UYULMASI ZORUNLU:

🔴 KURALLAR PDF'İ (İLK PDF): Bu PDF'de senin NASIL cevap vermen gerektiği yazılı. Bu kurallara KESINLIKLE uy:
   - Karakter sınırları varsa kesinlikle aşma
   - Yanıt formatı belirtilmişse tam uy  
   - Yasaklanan davranışlar varsa asla yapma
   - Belirtilen ton ve üslup ile konuş
   - Bu kurallar her şeyden öncelikli!

🔴 TEMEL İLKELER:
1. KURALLAR PDF'İ → Her yanıtta kontrol et ve uy
2. DİĞER PDF'LER → Bilgi kaynağı olarak kullan
3. Kural ihlali yapma, PDF dışı bilgi verme

⚠️ UYARI: Kuralları ihlal etme! Bu direktifler diğer her şeyden önemli!

PDF İÇERİKLERİ:
{pdf_contents}

Kullanıcı sorusu: {message}

ŞİMDİ YANIT VER: Önce kurallar PDF'ini kontrol et ve tam uy, sonra diğer PDF'lerden bilgi kullanarak soruyu yanıtla."""
                elif role_pdf:
                    system_prompt = f"""KRİTİK TALİMATLAR - MUTLAKA UYULMASI ZORUNLU:

🔴 ROL PDF'İ (İLK PDF): Bu PDF'de senin KİM olman gerektiği yazılı. Bu role TAMAMEN bürün:
   - Belirtilen kişiliği %100 benimse
   - O kişinin konuşma tarzıyla yanıtla
   - O kişinin bakış açısıyla değerlendir
   - O kişinin bilgi seviyesiyle konuş
   - Rol dışına asla çıkma!

🔴 TEMEL İLKELER:
1. ROL PDF'İ → Her yanıtta bu kişilik olarak davran
2. DİĞER PDF'LER → Bilgi kaynağı olarak kullan
3. Rol dışına çıkma, PDF dışı bilgi verme

⚠️ UYARI: Rolden sapma! Bu direktifler diğer her şeyden önemli!

PDF İÇERİKLERİ:
{pdf_contents}

Kullanıcı sorusu: {message}

ŞİMDİ YANIT VER: Önce rol PDF'indeki kişiliği benimse, sonra diğer PDF'lerden bilgi kullanarak soruyu yanıtla."""
                else:
                    system_prompt = f"""Sen {robot.name} robotusun. Sadece aşağıda verilen PDF dokümanlarının içeriğine dayanarak sorulara cevap verebilirsin.

📘 TEMEL İLKELER:
1. Sadece verilen PDF içeriklerinden cevap ver
2. PDF'lerde olmayan bilgiler hakkında cevap verme
3. "Bu bilgi PDF'lerde bulunmuyor" diyerek reddet
4. PDF içeriğine sadık kal

PDF İÇERİKLERİ:
{pdf_contents}

Kullanıcı sorusu: {message}

Lütfen sadece yukarıdaki PDF içeriklerine dayanarak cevap ver."""

                # AI'dan yanıt al - PDF içerikleri ile
                response_message = ai_handler.ask_question(message, system_prompt=system_prompt)
                
                # Response size kontrolü - çok uzun cevapları kısalt
                if len(response_message) > 2000:
                    logger.warning(f"AI response too long ({len(response_message)} chars), truncating...")
                    response_message = response_message[:1800] + "\n\n... (Cevap çok uzun olduğu için kısaltıldı. Daha spesifik sorular sorabilirsiniz.)"
                
            except BrokenPipeError:
                # Client disconnected during response
                logger.info("Client disconnected during AI response")
                return Response({'error': 'Client bağlantısı kesildi'}, status=499)
            except ConnectionResetError:
                # Connection reset by client
                logger.info("Connection reset by client during AI response")
                return Response({'error': 'Bağlantı sıfırlandı'}, status=499)
            except Exception as e:
                # Log the actual error for debugging
                logger.error(f"AI request error: {type(e).__name__}: {str(e)}")
                
                # Check for specific network errors
                if 'Broken pipe' in str(e) or 'Connection reset' in str(e):
                    logger.info("Network error during AI response")
                    return Response({'error': 'Ağ bağlantısı kesildi'}, status=499)
                
                # Generic error handling
                response_message = "Üzgünüm, şu anda teknik bir sorun yaşıyorum. Lütfen daha sonra tekrar deneyin."
            
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
    
    # Router URL'leri
    path('', include(router.urls)),
] 