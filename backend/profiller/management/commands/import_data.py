from django.core.management.base import BaseCommand
from django.core import serializers
from profiller.models import Profil
from robots.models import Robot, RobotPDF, Brand
import json

class Command(BaseCommand):
    help = 'JSON dosyasından verileri içe aktarır'

    def handle(self, *args, **kwargs):
        try:
            self.stdout.write('📦 Verileri içe aktarma işlemi başlıyor...')
            
            # JSON dosyasını oku
            with open('backup_data.json', 'r', encoding='utf-8') as f:
                data = json.load(f)
            
            # Verileri sırayla içe aktar
            model_order = ['brands', 'profiller', 'robots', 'robot_pdfs']
            
            for model_name in model_order:
                if model_name not in data:
                    self.stdout.write(self.style.WARNING(f'⚠️ {model_name} verisi bulunamadı'))
                    continue
                    
                self.stdout.write(f'🔄 {model_name} verilerini içe aktarıyor...')
                model_data = data[model_name]
                
                # Mevcut kayıtları say
                if model_name == 'profiller':
                    before_count = Profil.objects.count()
                elif model_name == 'robots':
                    before_count = Robot.objects.count()
                elif model_name == 'robot_pdfs':
                    before_count = RobotPDF.objects.count()
                elif model_name == 'brands':
                    before_count = Brand.objects.count()
                
                # Verileri içe aktar
                for obj in serializers.deserialize('json', model_data):
                    try:
                        obj.save()
                    except Exception as e:
                        self.stdout.write(
                            self.style.WARNING(f'⚠️ Kayıt atlandı: {str(e)}')
                        )
                
                # Yeni kayıt sayısını kontrol et
                if model_name == 'profiller':
                    after_count = Profil.objects.count()
                elif model_name == 'robots':
                    after_count = Robot.objects.count()
                elif model_name == 'robot_pdfs':
                    after_count = RobotPDF.objects.count()
                elif model_name == 'brands':
                    after_count = Brand.objects.count()
                
                new_records = after_count - before_count
                self.stdout.write(
                    self.style.SUCCESS(f'✅ {model_name}: {new_records} yeni kayıt eklendi')
                )
            
            self.stdout.write(
                self.style.SUCCESS('✅ Tüm veriler başarıyla içe aktarıldı!')
            )
        
        except FileNotFoundError:
            self.stdout.write(
                self.style.ERROR('❌ backup_data.json dosyası bulunamadı!')
            )
        except Exception as e:
            self.stdout.write(
                self.style.ERROR(f'❌ Hata oluştu: {str(e)}')
            ) 