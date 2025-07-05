from django.core.management.base import BaseCommand
from django.core import serializers
from django.conf import settings
from django.utils import timezone
from django import get_version
from profiller.models import Profil
from robots.models import Robot, RobotPDF, Brand
import json
import os
from datetime import datetime

class Command(BaseCommand):
    help = 'Tüm verileri JSON formatında dışa aktarır'

    def add_arguments(self, parser):
        parser.add_argument(
            '--output',
            default=None,
            help='Dışa aktarılacak dosyanın yolu (varsayılan: backup_data_YYYY-MM-DD_HH-MM.json)'
        )
        parser.add_argument(
            '--pretty',
            action='store_true',
            help='JSON dosyasını okunabilir formatta kaydet'
        )

    def handle(self, *args, **options):
        try:
            # Yedekleme dizinini oluştur
            backup_dir = 'backups'
            if not os.path.exists(backup_dir):
                os.makedirs(backup_dir)

            # Dosya adını belirle
            if options['output']:
                output_file = options['output']
            else:
                timestamp = datetime.now().strftime('%Y-%m-%d_%H-%M')
                output_file = os.path.join(backup_dir, f'backup_data_{timestamp}.json')

            # Veritabanı bilgilerini al
            db_info = settings.DATABASES['default']
            
            # Meta bilgileri oluştur
            metadata = {
                'export_date': timezone.now().isoformat(),
                'database_name': db_info.get('NAME', 'unknown'),
                'database_host': db_info.get('HOST', 'unknown'),
                'django_version': get_version(),
            }

            # Model verilerini topla
            model_data = {
                'profiller': [],
                'robots': [],
                'robot_pdfs': [],
                'brands': [],
            }

            # Profilleri dışa aktar
            self.stdout.write('🔄 Profil verilerini dışa aktarıyor...')
            model_data['profiller'] = serializers.serialize('json', Profil.objects.all())
            self.stdout.write(f'✅ {Profil.objects.count()} profil aktarıldı')

            # Robotları dışa aktar
            self.stdout.write('🔄 Robot verilerini dışa aktarıyor...')
            model_data['robots'] = serializers.serialize('json', Robot.objects.all())
            self.stdout.write(f'✅ {Robot.objects.count()} robot aktarıldı')

            # Robot PDF'lerini dışa aktar
            self.stdout.write('🔄 Robot PDF verilerini dışa aktarıyor...')
            model_data['robot_pdfs'] = serializers.serialize('json', RobotPDF.objects.all())
            self.stdout.write(f'✅ {RobotPDF.objects.count()} robot PDF aktarıldı')

            # Markaları dışa aktar
            self.stdout.write('🔄 Marka verilerini dışa aktarıyor...')
            model_data['brands'] = serializers.serialize('json', Brand.objects.all())
            self.stdout.write(f'✅ {Brand.objects.count()} marka aktarıldı')

            # Tüm verileri birleştir
            export_data = {
                'metadata': metadata,
                'data': model_data
            }

            # JSON dosyasına kaydet
            self.stdout.write('💾 Verileri dosyaya kaydediyor...')
            with open(output_file, 'w', encoding='utf-8') as f:
                if options['pretty']:
                    json.dump(export_data, f, ensure_ascii=False, indent=2)
                else:
                    json.dump(export_data, f, ensure_ascii=False)

            self.stdout.write(
                self.style.SUCCESS(f'✅ Veriler başarıyla dışa aktarıldı: {output_file}')
            )
            
            # İstatistikleri göster
            self.stdout.write('\n📊 Dışa Aktarım İstatistikleri:')
            self.stdout.write(f'- Profiller: {Profil.objects.count()}')
            self.stdout.write(f'- Robotlar: {Robot.objects.count()}')
            self.stdout.write(f'- Robot PDFler: {RobotPDF.objects.count()}')
            self.stdout.write(f'- Markalar: {Brand.objects.count()}')

        except Exception as e:
            self.stdout.write(
                self.style.ERROR(f'❌ Hata oluştu: {str(e)}')
            ) 