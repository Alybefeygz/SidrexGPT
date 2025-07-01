from django.core.management.base import BaseCommand
from robots.models import Brand


class Command(BaseCommand):
    help = 'Sidrex markasını oluşturur veya kontrol eder'

    def handle(self, *args, **options):
        try:
            # Sidrex markasını al veya oluştur
            brand, created = Brand.objects.get_or_create(
                name='Sidrex',
                defaults={
                    'total_api_requests': 0,
                    'paket_turu': 'normal',
                    'paket_suresi': 30
                }
            )
            
            if created:
                self.stdout.write(
                    self.style.SUCCESS(f'✅ Sidrex markası başarıyla oluşturuldu (ID: {brand.id})')
                )
            else:
                self.stdout.write(
                    self.style.WARNING(f'ℹ️  Sidrex markası zaten var (ID: {brand.id})')
                )
            
            # Mevcut durumu göster
            self.stdout.write('\n--- Sidrex Marka Bilgileri ---')
            self.stdout.write(f'ID: {brand.id}')
            self.stdout.write(f'İsim: {brand.name}')
            self.stdout.write(f'Paket Türü: {brand.paket_turu} ({brand.get_paket_turu_display()})')
            self.stdout.write(f'İstek Limiti: {brand.request_limit}')
            self.stdout.write(f'Toplam İstek: {brand.total_api_requests}')
            self.stdout.write(f'Kalan İstek: {brand.remaining_requests()}')
            self.stdout.write(f'Kalan Gün: {brand.remaining_days()}')
            self.stdout.write(f'Paket Durumu: {brand.package_status()}')
            self.stdout.write(f'Paket Başlangıç: {brand.paket_baslangic_tarihi}')
            self.stdout.write(f'Paket Bitiş: {brand.paket_bitis_tarihi}')
            
            self.stdout.write('\n--- API Kullanım Bilgileri ---')
            self.stdout.write(f'GET /api/brands/ - Mevcut durumu görüntüle')
            self.stdout.write(f'PATCH /api/brands/{brand.id}/ - Paket türünü değiştir')
            self.stdout.write(f'POST /api/brands/{brand.id}/change_package/ - Özel paket değiştirme')
            
        except Exception as e:
            self.stdout.write(
                self.style.ERROR(f'❌ Hata oluştu: {str(e)}')
            ) 