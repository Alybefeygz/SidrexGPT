from django.db import models
from django.contrib.auth.models import User

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
        """Chat mesajını işle ve cevap döndür"""
        try:
            # Kullanıcının marka kontrolü
            if not user.is_staff and not user.is_superuser:
                if not hasattr(user, 'profil') or not user.profil.brand:
                    return {
                        'error': 'Bu robota erişim yetkiniz yok.',
                        'status': 403
                    }
                if self.brand != user.profil.brand:
                    return {
                        'error': 'Bu robota erişim yetkiniz yok.',
                        'status': 403
                    }
            
            # Basit bir echo cevabı - gerçek implementasyonda AI entegrasyonu olacak
            response = {
                'message': f"Mesajınızı aldım: {message}",
                'status': 200
            }
            
            return response
            
        except Exception as e:
            return {
                'error': str(e),
                'status': 500
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
    pdf_dosyasi = models.FileField(upload_to='robot_pdfs/%Y/%m/', verbose_name="PDF Dosyası")
    dosya_adi = models.CharField(max_length=200, verbose_name="Dosya Adı", blank=True)
    aciklama = models.TextField(blank=True, null=True, verbose_name="Açıklama")
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
        if not self.dosya_adi and self.pdf_dosyasi:
            self.dosya_adi = self.pdf_dosyasi.name
        
        # PDF türüne göre has_rules, has_role, has_info ve has_declaration değerlerini otomatik ayarla
        if self.pdf_type == 'kural':
            self.has_rules = True
            self.has_role = False
            self.has_info = False
            self.has_declaration = False
        elif self.pdf_type == 'rol':
            self.has_rules = False
            self.has_role = True
            self.has_info = False
            self.has_declaration = False
        elif self.pdf_type == 'beyan':
            self.has_rules = False
            self.has_role = False
            self.has_info = False
            self.has_declaration = True
        else:  # bilgi
            self.has_rules = False
            self.has_role = False
            self.has_info = True
            self.has_declaration = False
            
        super().save(*args, **kwargs)
    
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