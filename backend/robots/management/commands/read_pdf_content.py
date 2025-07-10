from django.core.management.base import BaseCommand, CommandError
from robots.models import RobotPDF
from robots.services import download_pdf_content_from_drive, extract_text_from_pdf_stream
import logging

# Logger yapılandırması
logger = logging.getLogger(__name__)

class Command(BaseCommand):
    help = 'Veritabanındaki bir RobotPDF nesnesinin Google Drive linkinden içeriğini okur ve konsola yazar.'

    def add_arguments(self, parser):
        parser.add_argument('robot_pdf_id', type=int, help='İçeriği okunacak olan RobotPDF nesnesinin IDsi.')

    def handle(self, *args, **options):
        robot_pdf_id = options['robot_pdf_id']
        
        self.stdout.write(self.style.NOTICE(f"🤖 {robot_pdf_id} ID'li RobotPDF aranıyor..."))
        
        try:
            pdf_instance = RobotPDF.objects.get(pk=robot_pdf_id)
        except RobotPDF.DoesNotExist:
            raise CommandError(f"🚨 {robot_pdf_id} ID'li RobotPDF bulunamadı.")
            
        self.stdout.write(self.style.SUCCESS(f"✅ RobotPDF bulundu: '{pdf_instance.dosya_adi}'"))
        
        if not pdf_instance.gdrive_file_id:
            self.stderr.write(self.style.ERROR("🚨 Bu PDF nesnesinin bir Google Drive dosya ID'si yok."))
            return

        self.stdout.write(self.style.NOTICE(f"📄 Google Drive'dan dosya içeriği indiriliyor... (ID: {pdf_instance.gdrive_file_id})"))
        
        pdf_stream = download_pdf_content_from_drive(pdf_instance.gdrive_file_id)
        
        if not pdf_stream:
            self.stderr.write(self.style.ERROR("🚨 Google Drive'dan dosya içeriği indirilemedi. Detaylar için logları kontrol edin."))
            return
            
        self.stdout.write(self.style.SUCCESS("✅ Dosya içeriği başarıyla indirildi."))
        self.stdout.write(self.style.NOTICE("✍️ PDF içeriği metne dönüştürülüyor..."))
        
        text_content = extract_text_from_pdf_stream(pdf_stream)
        
        if not text_content:
            self.stderr.write(self.style.WARNING("⚠️ PDF'ten metin çıkarılamadı. Dosya boş veya taranmış bir resim olabilir."))
            return
            
        self.stdout.write(self.style.SUCCESS("✅ Metin başarıyla çıkarıldı."))
        self.stdout.write("\n" + "="*50 + "\n")
        self.stdout.write(self.style.HTTP_INFO("PDF İÇERİĞİ:"))
        self.stdout.write("="*50 + "\n")
        self.stdout.write(text_content)
        self.stdout.write("\n" + "="*50)
        self.stdout.write(self.style.SUCCESS("\nİşlem tamamlandı.")) 