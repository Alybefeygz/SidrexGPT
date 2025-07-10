import uuid
from django.db import models
from django.conf import settings
from supabase import create_client, Client

class Medya(models.Model):
    adi = models.CharField(max_length=255, help_text="Medyanın adı")
    # Veritabanında Supabase'deki dosyanın yolunu tutacağız.
    supabase_path = models.CharField(max_length=1024, blank=True)
    yuklenme_tarihi = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = "Medya Dosyası"
        verbose_name_plural = "Medya Dosyaları"

    def __str__(self):
        return self.adi

    # Model kaydedildiğinde dosyayı Supabase'e yükleme mantığı
    def save(self, *args, **kwargs):
        # Bu, `dosya` attribute'ünün sadece yükleme için geçici olarak eklendiğini varsayar.
        if hasattr(self, 'dosya_gecici'):
            
            supabase: Client = create_client(settings.SUPABASE_URL, settings.SUPABASE_KEY)
            bucket_name = settings.SUPABASE_BUCKET_NAME
            
            # Eğer bu obje daha önce kaydedilmişse ve eski bir dosyası varsa, onu silelim.
            if self.pk and self.supabase_path:
                try:
                    supabase.storage.from_(bucket_name).remove([self.supabase_path])
                except Exception as e:
                    print(f"Eski dosya silinemedi: {e}")

            # Benzersiz bir dosya adı oluşturma
            dosya_adi = f"fotograflar/{uuid.uuid4()}-{self.dosya_gecici.name}"
            
            try:
                # Dosyayı yükleme
                supabase.storage.from_(bucket_name).upload(
                    path=dosya_adi,
                    file=self.dosya_gecici.read(),
                    file_options={"content-type": self.dosya_gecici.content_type}
                )
                self.supabase_path = dosya_adi
            except Exception as e:
                print(f"Supabase'e yükleme başarısız: {e}")
        
        # Geçici dosyayı siliyoruz ki bir daha kullanılmasın
        if hasattr(self, 'dosya_gecici'):
            delattr(self, 'dosya_gecici')

        super().save(*args, **kwargs)

    # Dosyanın public URL'ini oluşturan property
    @property
    def public_url(self):
        if not self.supabase_path:
            return None
        return f"{settings.SUPABASE_URL}/storage/v1/object/public/{settings.SUPABASE_BUCKET_NAME}/{self.supabase_path}"


class StatikVarlik(models.Model):
    # 'logo_header', 'banner_anasayfa' gibi benzersiz bir anahtar
    anahtar = models.CharField(max_length=100, unique=True, db_index=True, help_text="Varlığı kod içinde çağırmak için kullanılacak benzersiz anahtar.")
    supabase_path = models.CharField(max_length=1024, help_text="Supabase bucket içindeki tam dosya yolu.")
    aciklama = models.TextField(blank=True, null=True, help_text="Bu varlığın nerede ve ne için kullanıldığı.")

    class Meta:
        verbose_name = "Statik Varlık"
        verbose_name_plural = "Statik Varlıklar"

    def __str__(self):
        return self.anahtar

    @property
    def public_url(self):
        if not self.supabase_path:
            return None
        return f"{settings.SUPABASE_URL}/storage/v1/object/public/{settings.SUPABASE_STATIC_BUCKET}/{self.supabase_path}"
