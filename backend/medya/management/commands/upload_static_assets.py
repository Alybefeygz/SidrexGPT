import os
from django.core.management.base import BaseCommand
from django.conf import settings
from supabase import create_client, Client
from medya.models import StatikVarlik
import mimetypes

class Command(BaseCommand):
    help = 'frontend/public klasöründeki statik varlıkları Supabase Storage\'a yükler.'

    def handle(self, *args, **options):
        self.stdout.write(self.style.SUCCESS('Statik varlıkları Supabase\'e yükleme işlemi başlıyor...'))

        # Supabase ayarlarını kontrol et
        if not settings.SUPABASE_URL or not settings.SUPABASE_KEY:
            self.stderr.write(self.style.ERROR('SUPABASE_URL veya SUPABASE_KEY ayarları eksik!'))
            return

        supabase: Client = create_client(settings.SUPABASE_URL, settings.SUPABASE_KEY)
        bucket_name = settings.SUPABASE_STATIC_BUCKET
        
        # Proje kök dizininden frontend/public klasörüne giden yol
        public_folder_path = os.path.join(settings.BASE_DIR, '..', 'frontend', 'public')
        
        if not os.path.exists(public_folder_path):
            self.stderr.write(self.style.ERROR(f'Frontend public klasörü bulunamadı: {public_folder_path}'))
            return

        self.stdout.write(f'Taranacak klasör: {public_folder_path}')
        
        dosya_sayisi = 0
        basarili_yuklemeler = 0

        for root, dirs, files in os.walk(public_folder_path):
            for filename in files:
                file_path = os.path.join(root, filename)
                
                # Supabase'deki yolu, 'public' klasör yapısını koruyacak şekilde oluştur
                relative_path = os.path.relpath(file_path, public_folder_path)
                supabase_path = relative_path.replace('\\', '/')  # Windows yollarını düzelt

                # Anahtar oluştur (örn: images/hands.png -> images_hands_png)
                anahtar = supabase_path.replace('/', '_').replace('.', '_')

                dosya_sayisi += 1

                # Dosyayı oku ve yükle
                try:
                    with open(file_path, 'rb') as f:
                        content_type, _ = mimetypes.guess_type(file_path)
                        if content_type is None:
                            content_type = 'application/octet-stream'

                        self.stdout.write(f"Yükleniyor: {supabase_path}")
                        
                        # Dosyayı Supabase'e yükle (upsert=true üzerine yazar)
                        supabase.storage.from_(bucket_name).upload(
                            path=supabase_path,
                            file=f.read(),
                            file_options={"content-type": content_type, "upsert": "true"}
                        )

                        # Veritabanına kaydet
                        varlik, created = StatikVarlik.objects.update_or_create(
                            anahtar=anahtar,
                            defaults={
                                'supabase_path': supabase_path,
                                'aciklama': f'{filename} dosyasından otomatik olarak oluşturuldu.'
                            }
                        )
                        
                        basarili_yuklemeler += 1
                        if created:
                            self.stdout.write(self.style.SUCCESS(f' -> Veritabanına eklendi: {anahtar}'))
                        else:
                            self.stdout.write(self.style.WARNING(f' -> Veritabanında güncellendi: {anahtar}'))

                except Exception as e:
                    self.stderr.write(self.style.ERROR(f'Hata: {filename} yüklenemedi. Sebep: {e}'))

        self.stdout.write(self.style.SUCCESS(f'İşlem tamamlandı! {basarili_yuklemeler}/{dosya_sayisi} dosya başarıyla yüklendi.')) 