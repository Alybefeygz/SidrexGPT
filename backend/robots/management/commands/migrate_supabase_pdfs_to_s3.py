import os
import requests
from django.core.files.base import ContentFile
from django.core.management.base import BaseCommand
from robots.models import RobotPDF

# Supabase Storage ayarları
SUPABASE_BUCKET = os.getenv('SUPABASE_BUCKET', 'robotpdfs')  # Supabase bucket adı
SUPABASE_URL = os.getenv('SUPABASE_URL')
SUPABASE_SERVICE_ROLE_KEY = os.getenv('SUPABASE_SERVICE_ROLE_KEY')

class Command(BaseCommand):
    help = 'Supabase Storage PDF dosyalarını indirip S3 (Django FileField) ile kaydeder.'

    def handle(self, *args, **options):
        if not SUPABASE_URL or not SUPABASE_SERVICE_ROLE_KEY:
            self.stderr.write(self.style.ERROR('Supabase bağlantı bilgileri eksik!'))
            return

        pdfs = RobotPDF.objects.all()
        for pdf in pdfs:
            if not pdf.pdf_dosyasi:
                self.stdout.write(f"[SKIP] {pdf.id} - Dosya yok")
                continue
            # Supabase'daki dosya yolu
            supabase_path = str(pdf.pdf_dosyasi)
            # Eğer dosya zaten S3'te ise atla
            if supabase_path.startswith('robot_pdfs/'):
                self.stdout.write(f"[OK] {pdf.id} - Zaten S3'te: {supabase_path}")
                continue
            # Supabase public URL oluştur
            file_url = f"{SUPABASE_URL}/storage/v1/object/public/{SUPABASE_BUCKET}/{supabase_path}"
            headers = {"apikey": SUPABASE_SERVICE_ROLE_KEY}
            self.stdout.write(f"[GET] {file_url}")
            r = requests.get(file_url, headers=headers)
            if r.status_code != 200:
                self.stderr.write(self.style.ERROR(f"[ERROR] {pdf.id} - Dosya indirilemedi: {file_url}"))
                continue
            # S3'e upload et
            file_name = os.path.basename(supabase_path)
            django_file = ContentFile(r.content, name=file_name)
            pdf.pdf_dosyasi.save(f"robot_pdfs/{file_name}", django_file, save=True)
            self.stdout.write(self.style.SUCCESS(f"[OK] {pdf.id} - S3'e yüklendi: robot_pdfs/{file_name}")) 