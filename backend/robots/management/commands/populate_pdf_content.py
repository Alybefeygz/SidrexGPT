from django.core.management.base import BaseCommand
from robots.models import RobotPDF
from robots.services import download_pdf_content_from_drive, extract_text_from_pdf_stream
import logging

logger = logging.getLogger(__name__)

class Command(BaseCommand):
    help = 'Mevcut RobotPDF nesnelerinin boş olan pdf_icerigi alanlarını Google Drive dan okuyarak doldurur.'

    def handle(self, *args, **options):
        self.stdout.write(self.style.NOTICE('🤖 PDF içerik doldurma işlemi başlıyor...'))

        # Sadece pdf_icerigi boş olan ve gdrive_file_id'si olan PDF'leri al
        pdfs_to_process = RobotPDF.objects.filter(pdf_icerigi__isnull=True, gdrive_file_id__isnull=False).exclude(gdrive_file_id='')

        if not pdfs_to_process.exists():
            self.stdout.write(self.style.SUCCESS('✅ İçeriği doldurulacak yeni PDF bulunamadı. Tüm PDFler güncel.'))
            return

        self.stdout.write(f'{pdfs_to_process.count()} adet PDF işlenecek.')

        processed_count = 0
        failed_count = 0

        for pdf in pdfs_to_process:
            self.stdout.write(f"  - İşleniyor: '{pdf.dosya_adi}' (ID: {pdf.id})")
            try:
                pdf_stream = download_pdf_content_from_drive(pdf.gdrive_file_id)
                if pdf_stream:
                    content = extract_text_from_pdf_stream(pdf_stream)
                    if content:
                        pdf.pdf_icerigi = content
                        pdf.save(update_fields=['pdf_icerigi'])
                        self.stdout.write(self.style.SUCCESS(f"    ✅ Başarılı: İçerik okundu ve kaydedildi."))
                        processed_count += 1
                    else:
                        self.stdout.write(self.style.WARNING(f"    ⚠️ Uyarı: PDF'ten metin çıkarılamadı (belki boştur)."))
                        failed_count += 1
                else:
                    self.stdout.write(self.style.ERROR(f"    ❌ Hata: Google Drive'dan dosya indirilemedi."))
                    failed_count += 1
            except Exception as e:
                logger.error(f"'{pdf.dosya_adi}' işlenirken hata oluştu: {e}")
                self.stdout.write(self.style.ERROR(f"    ❌ Hata: {e}"))
                failed_count += 1

        self.stdout.write(self.style.NOTICE('\n🎉 İşlem tamamlandı!'))
        self.stdout.write(self.style.SUCCESS(f'  - Başarıyla işlenen PDF sayısı: {processed_count}'))
        if failed_count > 0:
            self.stdout.write(self.style.WARNING(f'  - Başarısız olan PDF sayısı: {failed_count}'))
        else:
            self.stdout.write(f'  - Başarısız olan PDF sayısı: 0') 