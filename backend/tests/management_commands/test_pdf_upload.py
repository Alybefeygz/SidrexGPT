import os
from django.core.management.base import BaseCommand
import argparse
from django.conf import settings
from robots.models import Robot, RobotPDF

# Google API ve Supabase client kütüphaneleri
from google.oauth2.service_account import Credentials
from googleapiclient.discovery import build
from googleapiclient.http import MediaFileUpload
from supabase import create_client, Client

class Command(BaseCommand):
    help = 'Belirtilen bir robot ID si için test PDF dosyasını ("Belgeler/İmuntus Kids/Beyan Imuntus Kids.pdf") yükler.'

    def add_arguments(self, parser):
        parser.add_argument('robot_id', type=int, help='PDF in ilişkilendirileceği Robotun ID si.')

    def handle(self, *args, **options):
        # manage.py'nin bulunduğu 'backend' dizinini al
        backend_dir = settings.BASE_DIR
        # 'AI-powered-chatbox' dizinine çık
        ai_chatbox_dir = backend_dir.parent
        
        # Dosya yolu betik içine sabitlendi
        relative_path = "Belgeler/İmuntus Kids/Beyan Imuntus Kids.pdf"
        
        # Mutlak dosya yolunu 'AI-powered-chatbox' dizininden başlayarak oluştur
        file_path = os.path.join(ai_chatbox_dir, relative_path)

        robot_id = options['robot_id']

        if not os.path.exists(file_path):
            self.stderr.write(self.style.ERROR(f"Dosya bulunamadı: {file_path}"))
            self.stderr.write(self.style.NOTICE(f"Hesaplanan başlangıç dizini: {ai_chatbox_dir}"))
            return

        self.stdout.write(self.style.SUCCESS(f"'{file_path}' dosyası yükleniyor..."))
        
        gdrive_link = None

        # ======================================================================
        # 1. Google Drive'a Yükleme
        # ======================================================================
        self.stdout.write("Adım 1: Google Drive'a yükleniyor...")
        try:
            SCOPES = ['https://www.googleapis.com/auth/drive.file']
            PARENT_FOLDER_ID = '1HdOnnvWo6eccfsGJtwhYuN_jGbcWgHe4'
            
            # Environment variables'tan service account bilgilerini al
            if all(settings.GOOGLE_SERVICE_ACCOUNT_INFO.values()):
                # Environment variables'tan credentials oluştur
                creds = Credentials.from_service_account_info(
                    settings.GOOGLE_SERVICE_ACCOUNT_INFO, scopes=SCOPES
                )
            else:
                # Fallback: JSON dosyasından oku (backward compatibility)
                SERVICE_ACCOUNT_FILE = r'c:\Users\ygzef\OneDrive\Masaüstü\Yazılım\SidrexGPT\AI-powered-chatbox\backend\sidrexgpts-4f64e5e46ab0.json'
                
                if not os.path.exists(SERVICE_ACCOUNT_FILE):
                    self.stdout.write(self.style.WARNING("Google Drive hizmet hesabı JSON dosyası bulunamadı ve environment variables da eksik."))
                    self.stdout.write(self.style.WARNING(f"Beklenen dosya yolu: {SERVICE_ACCOUNT_FILE}"))
                    return
                
                creds = Credentials.from_service_account_file(
                    SERVICE_ACCOUNT_FILE, scopes=SCOPES)
            
            service = build('drive', 'v3', credentials=creds)
            
            file_metadata = {
                'name': os.path.basename(file_path),
                'parents': [PARENT_FOLDER_ID]
            }
            media = MediaFileUpload(file_path, mimetype='application/pdf')
            file = service.files().create(body=file_metadata,
                                            media_body=media,
                                            fields='id, webViewLink').execute()
        
            gdrive_file_id = file.get('id')
            gdrive_link = file.get('webViewLink')
            self.stdout.write(self.style.SUCCESS(f"Google Drive'a başarıyla yüklendi!"))
            self.stdout.write(f"  -> Dosya ID: {gdrive_file_id}")
            self.stdout.write(f"  -> Dosya Linki: {gdrive_link}")
        except Exception as e:
            self.stderr.write(self.style.ERROR(f"Google Drive yüklemesi başarısız: {e}"))
            return

        # ======================================================================
        # 2. Supabase Storage'a Yükleme
        # ======================================================================
        self.stdout.write("Adım 2: Supabase Storage'a yükleniyor...")
        try:
            url: str = os.environ.get("SUPABASE_URL")
            key: str = os.environ.get("SUPABASE_SERVICE_ROLE_KEY")

            if not url or not key:
                self.stderr.write(self.style.ERROR("Supabase URL veya KEY ortam değişkenleri bulunamadı."))
                return

            supabase: Client = create_client(url, key)
            bucket_name = os.getenv('SUPABASE_BUCKET', 'sidrexgpt-bucket')
            
            # Dosya adını markaya ve robota özel hale getirelim
            dosya_adi = os.path.basename(file_path)
            supabase_path = f"robot_{robot_id}/{dosya_adi}"

            with open(file_path, 'rb') as f:
                # Dosyanın zaten var olup olmadığını kontrol et ve üzerine yaz
                try:
                    supabase.storage.from_(bucket_name).remove([supabase_path])
                except Exception:
                    # Dosya yoksa hata verir, sorun değil.
                    pass
                
                supabase.storage.from_(bucket_name).upload(
                    path=supabase_path,
                    file=f,
                    file_options={"content-type": "application/pdf", "upsert": "true"}
                )

            self.stdout.write(self.style.SUCCESS(f"Supabase'e başarıyla yüklendi!"))
            self.stdout.write(f"  -> Bucket: {bucket_name}")
            self.stdout.write(f"  -> Dosya Yolu: {supabase_path}")

        except Exception as e:
            self.stderr.write(self.style.ERROR(f"Supabase yüklemesi başarısız: {e}"))
            return

        # ======================================================================
        # 3. Veritabanına Kaydetme
        # ======================================================================
        if gdrive_link:
            self.stdout.write("Adım 3: Veritabanına kaydediliyor...")
            try:
                robot = Robot.objects.get(id=robot_id)
                pdf_record, created = RobotPDF.objects.update_or_create(
                    robot=robot,
                    dosya_adi=os.path.basename(file_path),
                    defaults={
                        'pdf_dosyasi': gdrive_link,
                        'aciklama': f"{os.path.basename(file_path)} için test yüklemesi.",
                        'is_active': True,
                        'pdf_type': 'beyan'
                    }
                )
                if created:
                    self.stdout.write(self.style.SUCCESS(f"Veritabanına yeni kayıt oluşturuldu! PDF ID: {pdf_record.id}"))
                else:
                    self.stdout.write(self.style.SUCCESS(f"Mevcut veritabanı kaydı güncellendi! PDF ID: {pdf_record.id}"))

            except Robot.DoesNotExist:
                self.stderr.write(self.style.ERROR(f"Robot bulunamadı: ID={robot_id}"))
            except Exception as e:
                self.stderr.write(self.style.ERROR(f"Veritabanına kaydetme başarısız: {e}"))
        else:
            self.stdout.write(self.style.WARNING("Google Drive linki olmadığı için veritabanı kaydı atlandı."))
        
        self.stdout.write(self.style.SUCCESS("Test betiği tamamlandı.")) 