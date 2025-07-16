from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone
from robots.services import download_pdf_content_from_drive, extract_text_from_pdf_stream
import logging

logger = logging.getLogger(__name__)

# Create your models here.

class Brand(models.Model):
    """Marka modeli - API istek sayısını takip etmek için"""
    
    PAKET_CHOICES = [
        ('normal', 'Normal Paket'),
        ('pro', 'Pro Paket'),
        ('premium', 'Premium Paket'),
    ]
    
    name = models.CharField(max_length=100, unique=True, verbose_name="Marka İsmi")
    total_api_requests = models.PositiveIntegerField(default=0, verbose_name="Toplam API İstek Sayısı")
    request_limit = models.PositiveIntegerField(default=500, verbose_name="İstek Sınırı")
    
    # Paket Sistemi
    paket_turu = models.CharField(
        max_length=10, 
        choices=PAKET_CHOICES, 
        default='normal', 
        verbose_name="Paket Türü"
    )
    paket_suresi = models.PositiveIntegerField(default=30, verbose_name="Paket Süresi (Gün)")
    paket_baslangic_tarihi = models.DateTimeField(auto_now_add=True, verbose_name="Paket Başlangıç Tarihi")
    paket_bitis_tarihi = models.DateTimeField(null=True, blank=True, verbose_name="Paket Bitiş Tarihi")
    
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Oluşturulma Tarihi")
    updated_at = models.DateTimeField(auto_now=True, verbose_name="Güncellenme Tarihi")
    
    def __str__(self):
        return f"{self.name} - {self.get_paket_turu_display()} - {self.total_api_requests}/{self.request_limit} istek"
    
    def get_user_limit(self):
        """Paket türüne göre kullanıcı sınırını döndür"""
        user_limits = {
            'normal': 0,
            'pro': 1,
            'premium': 5,
        }
        return user_limits.get(self.paket_turu, 0)
    
    def active_users_count(self):
        """Bu markaya bağlı aktif kullanıcı sayısını döndür"""
        return self.users.filter(user__is_active=True).count()
    
    def is_user_limit_exceeded(self):
        """Kullanıcı sınırı aşıldı mı kontrol et"""
        return self.active_users_count() > self.get_user_limit()
    
    def can_add_user(self):
        """Yeni kullanıcı eklenebilir mi kontrol et"""
        return self.active_users_count() < self.get_user_limit()
    
    def deactivate_excess_users(self):
        """Fazla kullanıcıları pasif hale getir"""
        user_limit = self.get_user_limit()
        active_users = self.users.filter(user__is_active=True).order_by('user__date_joined')
        
        # Eğer limit 0 ise tüm kullanıcıları pasif hale getir
        if user_limit == 0:
            deactivated_users = []
            for profil in active_users:
                profil.user.is_active = False
                profil.user.save()
                deactivated_users.append(profil.user.username)
            return deactivated_users
        
        # Eğer kullanıcı sayısı limiti aşıyorsa, fazla olanları pasif hale getir
        if active_users.count() > user_limit:
            # İlk kayıt olan kullanıcıları aktif bırak, son kayıt olanları pasif hale getir
            users_to_keep = active_users[:user_limit]
            users_to_deactivate = active_users[user_limit:]
            
            deactivated_users = []
            for profil in users_to_deactivate:
                profil.user.is_active = False
                profil.user.save()
                deactivated_users.append(profil.user.username)
            
            return deactivated_users
        
        return []
    
    def save(self, *args, **kwargs):
        """Save metodunu override ederek paket türüne göre limit ayarla"""
        from datetime import timedelta
        from django.utils import timezone
        
        # Paket değişikliğini kontrol et
        paket_changed = False
        old_paket_turu = None
        if self.pk:  # Mevcut kayıt ise
            try:
                original = Brand.objects.get(pk=self.pk)
                if original.paket_turu != self.paket_turu:
                    paket_changed = True
                    old_paket_turu = original.paket_turu
            except Brand.DoesNotExist:
                pass
        
        # Paket türüne göre request_limit ayarla
        if self.paket_turu == 'normal':
            self.request_limit = 500
        elif self.paket_turu == 'pro':
            self.request_limit = 1000
        elif self.paket_turu == 'premium':
            self.request_limit = 5000
        
        # Paket bitiş tarihini hesapla (sadece yeni kayıt veya paket değişikliği durumunda)
        if not self.pk or self._state.adding:  # Yeni kayıt
            self.paket_bitis_tarihi = timezone.now() + timedelta(days=self.paket_suresi)
        elif paket_changed:  # Paket değişti
            self.paket_baslangic_tarihi = timezone.now()
            self.paket_bitis_tarihi = timezone.now() + timedelta(days=self.paket_suresi)
            self.total_api_requests = 0  # Yeni paket ile sayacı sıfırla
        
        super().save(*args, **kwargs)
        
        # Paket değişikliği sonrası kullanıcı sınırını kontrol et
        if paket_changed:
            deactivated = self.deactivate_excess_users()
            if deactivated:
                print(f"⚠️ Paket {old_paket_turu} → {self.paket_turu} değişikliği: {len(deactivated)} kullanıcı pasif hale getirildi: {', '.join(deactivated)}")
    
    def increment_api_count(self):
        """API istek sayısını 1 artır"""
        self.total_api_requests += 1
        self.save(update_fields=['total_api_requests', 'updated_at'])
        return self.total_api_requests
    
    def is_limit_exceeded(self):
        """İstek sınırı aşıldı mı kontrol et"""
        return self.total_api_requests >= self.request_limit
    
    def is_package_expired(self):
        """Paket süresi doldu mu kontrol et"""
        from django.utils import timezone
        if self.paket_bitis_tarihi:
            return timezone.now() > self.paket_bitis_tarihi
        return False
    
    def remaining_requests(self):
        """Kalan istek sayısını döndür"""
        remaining = self.request_limit - self.total_api_requests
        return max(0, remaining)
    
    def remaining_days(self):
        """Paket için kalan gün sayısını döndür"""
        from django.utils import timezone
        if self.paket_bitis_tarihi:
            remaining = self.paket_bitis_tarihi - timezone.now()
            return max(0, remaining.days)
        return 0
    
    def package_status(self):
        """Paket durumunu döndür"""
        if self.is_package_expired():
            return "⏰ Süresi Doldu"
        elif self.is_limit_exceeded():
            return "🚫 Limit Aşıldı"
        elif self.remaining_requests() < 50:
            return "⚠️ Kritik Seviye"
        elif self.remaining_days() < 3:
            return "⏳ Süre Bitiyor"
        else:
            return "✅ Aktif"
    
    def user_status(self):
        """Kullanıcı durumunu döndür"""
        active_count = self.active_users_count()
        user_limit = self.get_user_limit()
        
        if user_limit == 0:
            return "🚫 Kullanıcı Eklenmez"
        elif active_count >= user_limit:
            return f"🔴 Limit Dolu ({active_count}/{user_limit})"
        else:
            return f"✅ Kullanılabilir ({active_count}/{user_limit})"
    
    def change_package_type(self, new_package_type):
        """Paket türünü değiştir ve gerekli ayarlamaları yap"""
        if new_package_type not in [choice[0] for choice in self.PAKET_CHOICES]:
            raise ValueError(f"Geçersiz paket türü: {new_package_type}")
        
        old_package = self.paket_turu
        old_user_limit = self.get_user_limit()
        
        self.paket_turu = new_package_type
        self.save()  # save() metodunda kullanıcı kontrolü yapılacak
        
        new_user_limit = self.get_user_limit()
        
        return {
            'old_package': old_package,
            'new_package': new_package_type,
            'new_limit': self.request_limit,
            'reset_requests': True,
            'new_end_date': self.paket_bitis_tarihi,
            'old_user_limit': old_user_limit,
            'new_user_limit': new_user_limit,
            'active_users_count': self.active_users_count()
        }
    
    @classmethod
    def get_or_create_sidrex(cls):
        """Sidrex markası için Brand nesnesi döndür, yoksa oluştur"""
        brand, created = cls.objects.get_or_create(
            name='Sidrex',
            defaults={'total_api_requests': 0}
        )
        return brand
    
    class Meta:
        verbose_name = 'Marka'
        verbose_name_plural = 'Markalar'
        ordering = ['-total_api_requests', 'name']

class Robot(models.Model):
    name = models.CharField(max_length=100, verbose_name="Robot İsmi")
    product_name = models.CharField(max_length=150, verbose_name="Ürün İsmi")
    brand = models.ForeignKey(Brand, on_delete=models.CASCADE, related_name='robots', verbose_name="Marka")
    yaratilma_zamani = models.DateTimeField(auto_now_add=True)
    guncellenme_zamani = models.DateTimeField(auto_now=True)
    
    def __str__(self):
        return f"{self.name} - {self.product_name}"
    
    @property
    def pdf_sayisi(self):
        """Robot'un toplam PDF sayısını döndürür"""
        return self.pdf_dosyalari.count()
    
    @property
    def aktif_pdf_sayisi(self):
        """Robot'un aktif PDF sayısını döndürür"""
        return self.pdf_dosyalari.filter(is_active=True).count()
    
    @property
    def aktif_pdf_dosyalari(self):
        """Robot'un aktif PDF dosyalarını döndürür"""
        return self.pdf_dosyalari.filter(is_active=True)
    
    def get_slug(self):
        """Robot için URL-friendly slug oluştur"""
        name = self.name.lower()
        # Türkçe karakterleri değiştir
        name = name.replace('ğ', 'g').replace('ü', 'u').replace('ş', 's')
        name = name.replace('ı', 'i').replace('ö', 'o').replace('ç', 'c')
        # Özel durumlar
        if 'sidrexgpt asistani' in name:
            return 'sidrexgpt-asistani'
        elif 'mag' in name:
            return 'sidrexgpt-mag'
        elif 'kids' in name:
            return 'sidrexgpt-kids'
        # Genel durum
        import re
        name = re.sub(r'[^a-z0-9\s]', '', name)
        name = re.sub(r'\s+', '-', name.strip())
        return name
    
    def get_capabilities(self):
        """Robot'un yeteneklerini döndür"""
        capabilities = []
        
        # PDF tipine göre yetenekleri belirle
        pdf_types = self.pdf_dosyalari.filter(is_active=True).values_list('pdf_type', flat=True)
        
        if 'beyan' in pdf_types:
            capabilities.append("Yasal beyanları anlama ve yorumlama")
        if 'rol' in pdf_types:
            capabilities.append("Belirlenmiş role göre davranma")
        if 'kural' in pdf_types:
            capabilities.append("Kurallara uygun cevap verme")
        if 'bilgi' in pdf_types:
            capabilities.append("Bilgi kaynaklarından yararlanma")
        
        # Temel yetenekler
        capabilities.extend([
            "Metin tabanlı sohbet",
            "Soruları anlama ve cevaplama",
            "Bağlam takibi"
        ])
        
        return capabilities
    
    def process_chat_message(self, user, message):
        """
        Chat mesajını işle ve yanıt döndür
        
        Args:
            user: Mesajı gönderen kullanıcı
            message: Gönderilen mesaj
            
        Returns:
            Yanıt dict'i
        """
        from django.conf import settings
        from robots.scripts.ai_request import OpenRouterAIHandler
        from robots.services import get_robot_pdf_contents_for_ai
        import os
        
        # Marka API istek sayısını kontrol et
        if not user.is_staff and not user.is_superuser:
            if not hasattr(user, 'profil') or not user.profil.brand:
                return {
                    'error': 'API erişiminiz yok. Lütfen bir markaya bağlı olduğunuzdan emin olun.'
                }
            
            brand = user.profil.brand
            
            # Paket süresi kontrolü
            if brand.is_package_expired():
                return {
                    'error': f'Paket süreniz dolmuş. Lütfen paketinizi yenileyin. (Son {brand.remaining_days()} gün)'
                }
            
            # İstek limiti kontrolü
            if brand.is_limit_exceeded():
                return {
                    'error': f'API istek limitiniz dolmuş. Lütfen paketinizi yükseltin. ({brand.total_api_requests}/{brand.request_limit})'
                }
            
            # API sayacını artır
            brand.increment_api_count()
            print(f"INFO Sidrex API request count incremented to: {brand.total_api_requests}/{brand.request_limit}")
        
        try:
            # OpenRouter AI Handler'ı başlat
            handler = OpenRouterAIHandler(
                api_key=settings.OPENROUTER_API_KEY,
                app_name="SidrexGPT"
            )
            
            # PDF içeriklerini al (RAG sistemi)
            pdf_contents = get_robot_pdf_contents_for_ai(self)
            
            # Debug: PDF içerik boyutunu logla
            print(f"DEBUG PDF İçerik Uzunluğu: {len(pdf_contents)} karakter")
            print(f"DEBUG PDF İçerik İlk 200 karakter: {pdf_contents[:200]}")
            
            # Sistem promptunu hazırla (PDF içerikleriyle birlikte)
            system_prompt = f"""Sen {self.name} adlı bir yapay zeka asistanısın. 
            Görevin kullanıcılara yardımcı olmak ve sorularını yanıtlamak.
            
            Ürün: {self.product_name}
            
            ÖNEMLİ: Aşağıdaki PDF belgelerindeki bilgileri kullanarak cevap ver. Bu belgeler senin bilgi kaynağın:

{pdf_contents}

            KURALLAR:
            1. Öncelikle yukarıdaki PDF belgelerindeki bilgileri kullan
            2. PDF'lerde yasal beyan varsa ona kesinlikle uy
            3. Rol tanımı varsa o role göre davran
            4. Kurallar varsa onlara sıkı sıkıya bağlı kal
            5. Bilgi PDF'lerindeki teknik detayları kullan
            6. Emin olmadığın konularda "PDF belgelerimde bu bilgi bulunmuyor" de
            7. Her zaman nazik ve profesyonel ol
            8. Yanıtların kısa ve öz olsun
            9. Türkçe karakterleri doğru kullan
            10. Emoji kullanma
            
            Eğer PDF belgelerinde ilgili bilgi yoksa, genel bilgilerinle yardımcı olmaya çalış ama bunun PDF'lerde olmadığını belirt.
            """
            
            # Debug: Sistem promptu boyutunu logla
            print(f"DEBUG Sistem Prompt Uzunluğu: {len(system_prompt)} karakter")
            
            # Mesaj geçmişini hazırla
            messages = [
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": message}
            ]
            
            # Debug: Toplam mesaj boyutunu logla
            total_message_size = len(system_prompt) + len(message)
            print(f"DEBUG Toplam Mesaj Boyutu: {total_message_size} karakter")
            
            # Model döngüsü sistemi ile yanıt al
            response = handler.chat_with_history(messages, max_tokens=6000)
            
            return {
                'message': message,
                'response': response,
                'success': True
            }
            
        except Exception as e:
            print(f"ERROR Error in chat: {str(e)}")
            return {
                'error': 'Üzgünüm, şu anda bir teknik sorun yaşıyorum. Lütfen daha sonra tekrar deneyin.',
                'debug_error': str(e)
            }
    
    class Meta:
        verbose_name = 'Robot'
        verbose_name_plural = 'Robotlar'
        ordering = ['-yaratilma_zamani']


class RobotPDF(models.Model):
    PDF_TYPE_CHOICES = [
        ('bilgi', 'Bilgi'),
        ('kural', 'Kural'),
        ('rol', 'Rol'),
        ('beyan', 'Beyan'),  # İlaç firması yasal compliance için
    ]
    
    robot = models.ForeignKey(Robot, on_delete=models.CASCADE, related_name='pdf_dosyalari')
    
    # Depolama Bilgileri
    pdf_dosyasi = models.URLField(max_length=500, verbose_name="PDF Dosyası (Google Drive Linki)")
    gdrive_file_id = models.CharField(max_length=200, verbose_name="Google Drive Dosya ID", blank=True, null=True)
    supabase_path = models.CharField(max_length=500, verbose_name="Supabase Dosya Yolu", blank=True, null=True)

    dosya_adi = models.CharField(max_length=200, verbose_name="Dosya Adı", blank=True)
    aciklama = models.TextField(blank=True, null=True, verbose_name="Açıklama")
    pdf_icerigi = models.TextField(blank=True, null=True, verbose_name="PDF İçeriği")
    is_active = models.BooleanField(default=True, verbose_name="Aktif mi?")
    pdf_type = models.CharField(
        max_length=10,
        choices=PDF_TYPE_CHOICES,
        default='bilgi',
        verbose_name="PDF Türü"
    )
    has_rules = models.BooleanField(default=False, verbose_name="Kurallar PDF'i mi?")
    has_role = models.BooleanField(default=False, verbose_name="Rol PDF'i mi?")
    has_info = models.BooleanField(default=False, verbose_name="Bilgi PDF'i mi?")
    has_declaration = models.BooleanField(default=False, verbose_name="Beyan PDF'i mi?")  # Yasal beyanlar için
    yukleme_zamani = models.DateTimeField(auto_now_add=True)
    
    def save(self, *args, **kwargs):
        # Önce orijinal 'save' metodunu çağırarak nesnenin kaydedilmesini ve bir pk almasını sağlayalım.
        # Bu, özellikle yeni nesneler için önemlidir.
        is_new = self._state.adding
        
        # Eğer dosya adı boşsa ve bir dosya yolu varsa, dosya adını ayıkla
        if not self.dosya_adi and hasattr(self.pdf_dosyasi, 'name'):
            self.dosya_adi = self.pdf_dosyasi.name
        
        # PDF türüne göre boolean alanları ayarla
        self.has_rules = (self.pdf_type == 'kural')
        self.has_role = (self.pdf_type == 'rol')
        self.has_declaration = (self.pdf_type == 'beyan')
        self.has_info = (self.pdf_type == 'bilgi')

        # Değişiklikleri kaydet
        super().save(*args, **kwargs)

        # Sadece yeni bir PDF eklendiğinde içeriği doldur.
        # Mevcut PDF'lerin içeriğini doldurmak için ayrı bir management command kullanacağız.
        if is_new and self.gdrive_file_id and not self.pdf_icerigi:
            try:
                logger.info(f"Yeni PDF için içerik okunuyor: {self.dosya_adi} (ID: {self.id})")
                pdf_stream = download_pdf_content_from_drive(self.gdrive_file_id)
                if pdf_stream:
                    self.pdf_icerigi = extract_text_from_pdf_stream(pdf_stream)
                    # İçeriği kaydetmek için tekrar save çağırıyoruz ama sinyalleri tetiklememek için
                    # update_fields kullanıyoruz.
                    super().save(update_fields=['pdf_icerigi'])
                    logger.info(f"PDF içeriği başarıyla okundu ve kaydedildi: {self.dosya_adi}")
                else:
                    logger.warning(f"PDF içeriği indirilemedi: {self.dosya_adi}")
            except Exception as e:
                logger.error(f"PDF içeriği okunurken hata oluştu: {self.dosya_adi} - Hata: {e}")
    
    def __str__(self):
        status = "✅" if self.is_active else "❌"
        return f"{self.robot.name} - {self.dosya_adi} {status}"
    
    @property
    def dosya_boyutu(self):
        """Dosya boyutunu MB cinsinden döndürür"""
        if self.pdf_dosyasi:
            try:
                return round(self.pdf_dosyasi.size / (1024 * 1024), 2)
            except (OSError, ValueError):
                return 0
        return 0
    
    def toggle_active(self):
        """PDF'in aktif durumunu değiştirir"""
        self.is_active = not self.is_active
        self.save()
        return self.is_active
    
    class Meta:
        verbose_name = 'Robot PDF Dosyası'
        verbose_name_plural = 'Robot PDF Dosyaları'
        ordering = ['-yukleme_zamani']


class RobotSystemPrompt(models.Model):
    """Robot-bazlı sistem prompt'ları için model"""
    
    PROMPT_TYPE_CHOICES = [
        ('main', 'Ana Sistem Prompt'),
        ('health_claims', 'Sağlık Beyanları'),
        ('product_redirect', 'Ürün Yönlendirme'),
        ('fallback', 'Fallback/Varsayılan'),
    ]
    
    robot = models.ForeignKey(Robot, on_delete=models.CASCADE, related_name='system_prompts', verbose_name="Robot")
    prompt_type = models.CharField(
        max_length=20,
        choices=PROMPT_TYPE_CHOICES,
        default='main',
        verbose_name="Prompt Türü"
    )
    prompt_content = models.TextField(verbose_name="Prompt İçeriği")
    is_active = models.BooleanField(default=True, verbose_name="Aktif mi?")
    priority = models.IntegerField(default=0, verbose_name="Öncelik (Yüksek önce)")
    
    # Konu-bazlı özelleştirmeler
    topic_keywords = models.TextField(
        blank=True, null=True,
        verbose_name="Konu Anahtar Kelimeleri",
        help_text="Virgülle ayrılmış anahtar kelimeler (örn: bağışıklık,yorgunluk,kas)"
    )
    
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Oluşturulma Tarihi")
    updated_at = models.DateTimeField(auto_now=True, verbose_name="Güncellenme Tarihi")
    
    def __str__(self):
        status = "✅" if self.is_active else "❌"
        return f"{self.robot.name} - {self.get_prompt_type_display()} {status}"
    
    def get_keywords_list(self):
        """Anahtar kelimeleri liste olarak döndür"""
        if self.topic_keywords:
            return [keyword.strip().lower() for keyword in self.topic_keywords.split(',')]
        return []
    
    def matches_topic(self, user_message):
        """Kullanıcı mesajının bu prompt'a uygun olup olmadığını kontrol et"""
        if not self.topic_keywords:
            return False  # Topic keywords yoksa match etmez, sadece fallback olarak kullanılır
        
        message_lower = user_message.lower()
        keywords = self.get_keywords_list()
        
        return any(keyword in message_lower for keyword in keywords)
    
    class Meta:
        verbose_name = 'Robot Sistem Prompt'
        verbose_name_plural = 'Robot Sistem Promptları'
        ordering = ['-priority', '-created_at']
        unique_together = [('robot', 'prompt_type')]  # Her robot için her türden sadece bir prompt


class ChatSession(models.Model):
    """Chat oturumu modeli - kullanıcı ile robot arasındaki sohbet oturumu"""
    
    session_id = models.CharField(max_length=100, verbose_name="Oturum ID", help_text="Frontend'den gelen unique session ID")
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='chat_sessions', verbose_name="Kullanıcı", null=True, blank=True)
    robot = models.ForeignKey(Robot, on_delete=models.CASCADE, related_name='chat_sessions', verbose_name="Robot")
    started_at = models.DateTimeField(auto_now_add=True, verbose_name="Başlangıç Zamanı")
    ended_at = models.DateTimeField(null=True, blank=True, verbose_name="Bitiş Zamanı")
    is_active = models.BooleanField(default=True, verbose_name="Aktif mi?")
    total_messages = models.PositiveIntegerField(default=0, verbose_name="Toplam Mesaj Sayısı")
    total_response_time = models.DecimalField(max_digits=10, decimal_places=3, default=0.0, verbose_name="Toplam Yanıt Süresi (saniye)")
    average_response_time = models.DecimalField(max_digits=8, decimal_places=3, default=0.0, verbose_name="Ortalama Yanıt Süresi (saniye)")
    user_ip = models.GenericIPAddressField(null=True, blank=True, verbose_name="Kullanıcı IP")
    user_agent = models.TextField(null=True, blank=True, verbose_name="User Agent")
    
    def __str__(self):
        return f"{self.user.username} - {self.robot.name} - {self.session_id}"
    
    def update_stats(self):
        """Oturum istatistiklerini güncelle"""
        messages = self.chat_messages.all()
        self.total_messages = messages.count()
        
        # Yanıt süreleri var olan mesajları al
        response_times = messages.exclude(response_time__isnull=True).values_list('response_time', flat=True)
        if response_times:
            self.total_response_time = sum(response_times)
            self.average_response_time = self.total_response_time / len(response_times)
        
        self.save(update_fields=['total_messages', 'total_response_time', 'average_response_time'])
    
    def end_session(self):
        """Oturumu sonlandır"""
        self.is_active = False
        self.ended_at = timezone.now()
        self.save(update_fields=['is_active', 'ended_at'])
    
    class Meta:
        verbose_name = 'Chat Oturumu'
        verbose_name_plural = 'Chat Oturumları'
        ordering = ['-started_at']
        indexes = [
            models.Index(fields=['user', 'robot', 'started_at']),
            models.Index(fields=['session_id']),
            models.Index(fields=['started_at']),
        ]


class ChatMessage(models.Model):
    """Chat mesajı modeli - kullanıcı mesajları ve AI yanıtları"""
    
    MESSAGE_TYPE_CHOICES = [
        ('user', 'Kullanıcı Mesajı'),
        ('assistant', 'AI Yanıtı'),
    ]
    
    STATUS_CHOICES = [
        ('processing', 'İşleniyor'),
        ('completed', 'Tamamlandı'),
        ('failed', 'Başarısız'),
        ('timeout', 'Zaman Aşımı'),
    ]
    
    session = models.ForeignKey(ChatSession, on_delete=models.CASCADE, related_name='chat_messages', verbose_name="Chat Oturumu")
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='chat_messages', verbose_name="Kullanıcı", null=True, blank=True)
    robot = models.ForeignKey(Robot, on_delete=models.CASCADE, related_name='chat_messages', verbose_name="Robot")
    message_type = models.CharField(max_length=10, choices=MESSAGE_TYPE_CHOICES, verbose_name="Mesaj Türü")
    user_message = models.TextField(verbose_name="Kullanıcı Mesajı")
    ai_response = models.TextField(null=True, blank=True, verbose_name="AI Yanıtı")
    response_time = models.DecimalField(max_digits=8, decimal_places=3, null=True, blank=True, verbose_name="Yanıt Süresi (saniye)")
    processing_started_at = models.DateTimeField(null=True, blank=True, verbose_name="İşlem Başlangıç Zamanı")
    processing_ended_at = models.DateTimeField(null=True, blank=True, verbose_name="İşlem Bitiş Zamanı")
    status = models.CharField(max_length=15, choices=STATUS_CHOICES, default='processing', verbose_name="Durum")
    ai_model_used = models.CharField(max_length=100, null=True, blank=True, verbose_name="Kullanılan AI Modeli")
    tokens_used = models.PositiveIntegerField(null=True, blank=True, verbose_name="Kullanılan Token Sayısı")
    optimization_enabled = models.BooleanField(default=False, verbose_name="Optimizasyon Açık mıydı?")
    context_used = models.BooleanField(default=False, verbose_name="Context Kullanıldı mı?")
    context_size = models.PositiveIntegerField(null=True, blank=True, verbose_name="Context Boyutu (karakter)")
    citations_count = models.PositiveIntegerField(default=0, verbose_name="Alıntı Sayısı")
    error_message = models.TextField(null=True, blank=True, verbose_name="Hata Mesajı")
    error_type = models.CharField(max_length=50, null=True, blank=True, verbose_name="Hata Türü")
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Oluşturulma Zamanı")
    ip_address = models.GenericIPAddressField(null=True, blank=True, verbose_name="IP Adresi")
    user_feedback = models.IntegerField(
        null=True, blank=True,
        choices=[(1, '👎 Kötü'), (2, '😐 Orta'), (3, '👍 İyi')],
        verbose_name="Kullanıcı Geri Bildirimi"
    )
    admin_notes = models.TextField(null=True, blank=True, verbose_name="Admin Notları")
    
    def __str__(self):
        return f"{self.user.username} - {self.robot.name} - {self.created_at.strftime('%Y-%m-%d %H:%M')}"
    
    def calculate_response_time(self):
        """Yanıt süresini hesapla"""
        if self.processing_started_at and self.processing_ended_at:
            delta = self.processing_ended_at - self.processing_started_at
            self.response_time = delta.total_seconds()
            return self.response_time
        return None
    
    def mark_completed(self, ai_response, citations_count=0, context_used=False):
        """Mesajı tamamlandı olarak işaretle"""
        from django.utils import timezone
        
        self.ai_response = ai_response
        self.citations_count = citations_count
        self.context_used = context_used
        self.status = 'completed'
        self.processing_ended_at = timezone.now()
        self.calculate_response_time()
        self.save()
        
        # Session istatistiklerini güncelle
        self.session.update_stats()
    
    def mark_failed(self, error_message, error_type=None):
        """Mesajı başarısız olarak işaretle"""
        from django.utils import timezone
        
        self.error_message = error_message
        self.error_type = error_type or 'unknown'
        self.status = 'failed'
        self.processing_ended_at = timezone.now()
        self.calculate_response_time()
        self.save()
        
        # Session istatistiklerini güncelle
        self.session.update_stats()
    
    class Meta:
        verbose_name = 'Chat Mesajı'
        verbose_name_plural = 'Chat Mesajları'
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['user', 'robot', 'created_at']),
            models.Index(fields=['session', 'created_at']),
            models.Index(fields=['status']),
            models.Index(fields=['response_time']),
            models.Index(fields=['created_at']),
        ]