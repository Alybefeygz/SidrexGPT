from django.core.management.base import BaseCommand
from django.core import serializers
from profiller.models import Profil
from robots.models import Robot, RobotPDF, Brand
import json

class Command(BaseCommand):
    help = 'Tüm verileri JSON formatında dışa aktarır'

    def handle(self, *args, **kwargs):
        try:
            # Modelleri ve verilerini dışa aktar
            data = {
                'profiller': serializers.serialize('json', Profil.objects.all()),
                'robots': serializers.serialize('json', Robot.objects.all()),
                'robot_pdfs': serializers.serialize('json', RobotPDF.objects.all()),
                'brands': serializers.serialize('json', Brand.objects.all()),
            }
            
            # JSON dosyasına kaydet
            with open('backup_data.json', 'w', encoding='utf-8') as f:
                json.dump(data, f, ensure_ascii=False, indent=2)
            
            self.stdout.write(
                self.style.SUCCESS('✅ Veriler başarıyla dışa aktarıldı: backup_data.json')
            )
        except Exception as e:
            self.stdout.write(
                self.style.ERROR(f'❌ Hata oluştu: {str(e)}')
            ) 