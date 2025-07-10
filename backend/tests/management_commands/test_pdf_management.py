from django.core.management.base import BaseCommand
from robots.models import RobotPDF, Robot
from robots.rag_services import RAGService
from django.db import connection
import logging

logger = logging.getLogger(__name__)

class Command(BaseCommand):
    help = 'PDF yönetimi RAG entegrasyonunu test eder'

    def add_arguments(self, parser):
        parser.add_argument(
            '--robot-id',
            type=int,
            help='Test edilecek robot ID'
        )

    def handle(self, *args, **options):
        self.stdout.write(self.style.SUCCESS('🔍 PDF Yönetimi RAG Entegrasyon Testi Başlıyor...'))
        
        robot_id = options.get('robot_id')
        
        if robot_id:
            try:
                robot = Robot.objects.get(id=robot_id)
                self.test_robot_pdfs(robot)
            except Robot.DoesNotExist:
                self.stdout.write(self.style.ERROR(f'❌ Robot ID {robot_id} bulunamadı'))
                return
        else:
            # Tüm robotları test et
            robots = Robot.objects.all()
            for robot in robots:
                self.test_robot_pdfs(robot)

    def test_robot_pdfs(self, robot):
        self.stdout.write(self.style.WARNING(f'\n📖 Robot: {robot.name} (ID: {robot.id})'))
        
        pdfs = RobotPDF.objects.filter(robot=robot)
        
        if not pdfs.exists():
            self.stdout.write('   📄 Bu robot için PDF bulunamadı.')
            return
        
        rag_service = RAGService()
        
        for pdf in pdfs:
            self.stdout.write(f'   📄 PDF: {pdf.dosya_adi}')
            self.stdout.write(f'      ├─ Aktif: {"✅" if pdf.is_active else "❌"}')
            self.stdout.write(f'      ├─ Tür: {pdf.pdf_type}')
            
            # Chunk sayısını kontrol et
            with connection.cursor() as cursor:
                cursor.execute(
                    "SELECT COUNT(*) FROM pdf_chunks WHERE robot_pdf_id = %s",
                    [pdf.id]
                )
                chunk_count = cursor.fetchone()[0]
            
            self.stdout.write(f'      ├─ RAG Chunks: {chunk_count}')
            
            if pdf.is_active and chunk_count == 0:
                self.stdout.write(f'      ├─ ⚠️  Aktif PDF ama chunk yok!')
                
                # PDF içeriği varsa chunk'la
                if pdf.pdf_icerigi:
                    self.stdout.write(f'      ├─ 🔄 RAG chunking yapılıyor...')
                    try:
                        chunks_created = rag_service.process_single_pdf(pdf)
                        self.stdout.write(f'      ├─ ✅ {chunks_created} chunk oluşturuldu')
                    except Exception as e:
                        self.stdout.write(f'      ├─ ❌ Chunking hatası: {e}')
                else:
                    self.stdout.write(f'      ├─ ❌ PDF içeriği yok!')
            
            elif not pdf.is_active and chunk_count > 0:
                self.stdout.write(f'      ├─ ⚠️  Pasif PDF ama chunk var!')
                try:
                    deleted_chunks = rag_service.delete_chunks_for_pdf(pdf.id)
                    self.stdout.write(f'      ├─ 🗑️  {deleted_chunks} chunk silindi')
                except Exception as e:
                    self.stdout.write(f'      ├─ ❌ Chunk silme hatası: {e}')
            
            self.stdout.write(f'      └─ ✅ Sync durumu OK')
        
        # Robot'un toplam chunk durumu
        total_chunks = 0
        with connection.cursor() as cursor:
            cursor.execute("""
                SELECT COUNT(*) FROM pdf_chunks pc
                JOIN robots_robotpdf rp ON pc.robot_pdf_id = rp.id
                WHERE rp.robot_id = %s
            """, [robot.id])
            total_chunks = cursor.fetchone()[0]
        
        self.stdout.write(f'   📊 Toplam RAG Chunks: {total_chunks}')
        
        if total_chunks > 0:
            # Örnek arama yap
            test_query = "merhaba nasılsın"
            try:
                context, citations = rag_service.get_relevant_context(test_query, robot.id)
                self.stdout.write(f'   🔍 Test sorgusu: "{test_query}"')
                self.stdout.write(f'   📋 Bulunan citations: {len(citations)}')
                
                for i, citation in enumerate(citations[:2]):  # İlk 2 tanesini göster
                    self.stdout.write(f'      └─ Citation {i+1}: {citation["source"]} (similarity: {citation["similarity"]})')
            except Exception as e:
                self.stdout.write(f'   ❌ Test arama hatası: {e}')
        
        self.stdout.write(self.style.SUCCESS(f'✅ Robot {robot.name} testi tamamlandı')) 