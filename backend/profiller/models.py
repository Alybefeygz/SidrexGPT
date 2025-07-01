from django.db import models

from django.contrib.auth.models import User
from robots.models import Brand

from PIL import Image
from django.core.exceptions import ValidationError
# Create your models here.

class Profil(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='profil', unique=True)
    bio = models.CharField(max_length=300, blank=True, null=True)
    bio = models.CharField(max_length=120, blank=True, null=True)
    foto = models.ImageField(null=True, blank=True, upload_to='profil_fotolari/%Y/%m/')
    brand = models.ForeignKey(Brand, on_delete=models.SET_NULL, null=True, blank=True, related_name='users', verbose_name="Marka")
    
    def __str__(self):
        brand_name = self.brand.name if self.brand else "Marksız"
        return f"{self.user.username} ({brand_name})"
    
    class Meta:
        verbose_name_plural = 'Profiller'
        constraints = [
            models.UniqueConstraint(fields=['user'], name='unique_user_profile')
        ]
    
    def clean(self):
        """Model validation - marka değişikliği sırasında limit kontrolü"""
        # Brand'in None olmadığını ve valid olduğunu kontrol et
        if self.brand and hasattr(self.brand, 'id'):
            # Eğer bu yeni bir profil ise veya marka değişiyorsa
            if not self.pk or (self.pk and Profil.objects.get(pk=self.pk).brand != self.brand):
                # Kullanıcı aktif ise ve marka kullanıcı eklemeye izin vermiyorsa hata ver
                if self.user.is_active and not self.brand.can_add_user():
                    user_limit = self.brand.get_user_limit()
                    active_count = self.brand.active_users_count()
                    
                    if user_limit == 0:
                        raise ValidationError(
                            f"'{self.brand.name}' markası Normal paket kullanıyor. "
                            f"Normal pakette kullanıcı tanımlanamaz. "
                            f"Paketi Pro veya Premium'a yükseltin."
                        )
                    else:
                        raise ValidationError(
                            f"'{self.brand.name}' markasının kullanıcı sınırı aşıldı! "
                            f"Mevcut: {active_count}/{user_limit}. "
                            f"Yeni kullanıcı eklemek için paketi yükseltin."
                        )
    
    def save(self, *args, **kwargs):
        # Model validation çalıştır
        self.full_clean()
        
        #IMAGE RESIZE
        super().save( *args, **kwargs)
        if self.foto:
            img = Image.open(self.foto.path)
            if img.height > 600 or img.width > 600:
                output_size = (600,600)
                img.thumbnail(output_size)
                img.save(self.foto.path)
                
    
    
class ProfilDurum(models.Model):
    user_profil = models.ForeignKey(Profil, on_delete=models.CASCADE)
    durum_mesaji = models.CharField(max_length=240)
    yaratilma_zamani = models.DateTimeField(auto_now_add=True)
    guncellenme_zamani = models.DateTimeField(auto_now=True)
    
    def __str__(self):
        return str(self.user_profil)
    
    class Meta:
        verbose_name_plural = 'Profil Mesajları'
    
    
