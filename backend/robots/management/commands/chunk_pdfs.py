from django.core.management.base import BaseCommand
from robots.models import RobotPDF
from robots.rag_services import RAGService
from robots.rag_config import CHUNK_SCENARIOS
import logging

logger = logging.getLogger(__name__)

class Command(BaseCommand):
    help = 'Mevcut PDF dosyalarını chunk\'lar ve embeddingler oluşturur.'

    def add_arguments(self, parser):
        parser.add_argument(
            '--scenario',
            type=str,
            choices=['small', 'medium', 'large'],
            default='medium',
            help='Chunklama senaryosu (small/medium/large)'
        )
        
        parser.add_argument(
            '--robot-id',
            type=int,
            help='Sadece belirli bir robot\'un PDF\'lerini işle'
        )
        
        parser.add_argument(
            '--pdf-id',
            type=int,
            help='Sadece belirli bir PDF\'i işle'
        )
        
        parser.add_argument(
            '--force',
            action='store_true',
            help='Mevcut chunk\'ları sil ve yeniden oluştur'
        )
        
        parser.add_argument(
            '--test-all-scenarios',
            action='store_true',
            help='Tüm senaryoları test et ve karşılaştır'
        )

    def handle(self, *args, **options):
        scenario = options['scenario']
        robot_id = options.get('robot_id')
        pdf_id = options.get('pdf_id')
        force = options.get('force', False)
        test_all = options.get('test_all_scenarios', False)
        
        self.stdout.write(self.style.NOTICE('🤖 PDF chunklama işlemi başlıyor...'))
        
        # RAG servisi
        rag_service = RAGService()
        
        # PDF'leri filtrele
        queryset = RobotPDF.objects.filter(is_active=True)
        
        if pdf_id:
            queryset = queryset.filter(id=pdf_id)
        elif robot_id:
            queryset = queryset.filter(robot_id=robot_id)
        
        # Sadece içeriği olan PDF'ler
        queryset = queryset.exclude(pdf_icerigi__isnull=True).exclude(pdf_icerigi='')
        
        if not queryset.exists():
            self.stdout.write(self.style.WARNING('⚠️ İşlenecek PDF bulunamadı.'))
            return
        
        total_pdfs = queryset.count()
        self.stdout.write(f'📚 {total_pdfs} adet PDF işlenecek.')
        
        if test_all:
            self.test_all_scenarios(queryset, rag_service)
        else:
            self.process_pdfs(queryset, rag_service, scenario, force)

    def process_pdfs(self, queryset, rag_service, scenario, force):
        """PDF'leri belirli bir senaryo ile işle"""
        scenario_config = CHUNK_SCENARIOS.get(scenario, CHUNK_SCENARIOS['medium'])
        
        self.stdout.write(f"📋 Senaryo: {scenario_config['name']}")
        self.stdout.write(f"   Chunk Size: {scenario_config['chunk_size']}")
        self.stdout.write(f"   Chunk Overlap: {scenario_config['chunk_overlap']}")
        
        processed_count = 0
        failed_count = 0
        total_chunks = 0
        
        for pdf in queryset:
            self.stdout.write(f"  📄 İşleniyor: '{pdf.dosya_adi}' (Robot: {pdf.robot.name})")
            
            try:
                # Chunk kontrolü (force yoksa atla)
                if not force:
                    from django.db import connection
                    with connection.cursor() as cursor:
                        cursor.execute(
                            "SELECT COUNT(*) FROM pdf_chunks WHERE robot_pdf_id = %s",
                            [pdf.id]
                        )
                        existing_chunks = cursor.fetchone()[0]
                        
                        if existing_chunks > 0:
                            self.stdout.write(f"    ⏭️ Atlandı: {existing_chunks} chunk zaten var (--force ile zorla)")
                            continue
                
                result = rag_service.process_pdf(pdf, scenario)
                
                if result['success']:
                    chunks_count = result['chunks_count']
                    total_chunks += chunks_count
                    processed_count += 1
                    self.stdout.write(
                        self.style.SUCCESS(f"    ✅ Başarılı: {chunks_count} chunk oluşturuldu")
                    )
                else:
                    failed_count += 1
                    self.stdout.write(
                        self.style.ERROR(f"    ❌ Hata: {result['error']}")
                    )
                    
            except Exception as e:
                failed_count += 1
                self.stdout.write(
                    self.style.ERROR(f"    ❌ Beklenmedik hata: {e}")
                )
                logger.error(f"PDF chunklama hatası ({pdf.id}): {e}")
        
        # Özet
        self.stdout.write(self.style.NOTICE('\n🎉 İşlem tamamlandı!'))
        self.stdout.write(f'  ✅ Başarılı: {processed_count} PDF')
        self.stdout.write(f'  ❌ Başarısız: {failed_count} PDF')
        self.stdout.write(f'  📊 Toplam Chunk: {total_chunks}')
        
        if processed_count > 0:
            avg_chunks = total_chunks / processed_count
            self.stdout.write(f'  📈 Ortalama Chunk/PDF: {avg_chunks:.1f}')

    def test_all_scenarios(self, queryset, rag_service):
        """Tüm senaryoları test et ve karşılaştır"""
        self.stdout.write(self.style.NOTICE('🧪 Tüm senaryolar test ediliyor...'))
        
        # İlk PDF'i al (test için)
        test_pdf = queryset.first()
        if not test_pdf:
            self.stdout.write(self.style.ERROR('Test için PDF bulunamadı.'))
            return
        
        self.stdout.write(f"🎯 Test PDF: {test_pdf.dosya_adi}")
        
        results = {}
        
        for scenario_key, scenario_config in CHUNK_SCENARIOS.items():
            self.stdout.write(f"\n📋 Test Ediliyor: {scenario_config['name']}")
            
            try:
                result = rag_service.process_pdf(test_pdf, scenario_key)
                
                if result['success']:
                    results[scenario_key] = {
                        'chunks_count': result['chunks_count'],
                        'config': scenario_config,
                        'success': True
                    }
                    self.stdout.write(
                        self.style.SUCCESS(f"  ✅ {result['chunks_count']} chunk oluşturuldu")
                    )
                else:
                    results[scenario_key] = {
                        'error': result['error'],
                        'config': scenario_config,
                        'success': False
                    }
                    self.stdout.write(
                        self.style.ERROR(f"  ❌ {result['error']}")
                    )
                    
            except Exception as e:
                results[scenario_key] = {
                    'error': str(e),
                    'config': scenario_config,
                    'success': False
                }
                self.stdout.write(
                    self.style.ERROR(f"  ❌ Hata: {e}")
                )
        
        # Sonuçları karşılaştır
        self.stdout.write(self.style.NOTICE('\n📊 SENARYO KARŞILAŞTIRMASI:'))
        self.stdout.write('=' * 60)
        
        for scenario_key, result in results.items():
            config = result['config']
            if result['success']:
                chunks = result['chunks_count']
                self.stdout.write(
                    f"{config['name']:<20} | "
                    f"Size: {config['chunk_size']:<4} | "
                    f"Overlap: {config['chunk_overlap']:<3} | "
                    f"Chunks: {chunks}"
                )
            else:
                self.stdout.write(
                    f"{config['name']:<20} | HATA: {result['error']}"
                )
        
        self.stdout.write('\n💡 Öneriler:')
        self.stdout.write('  - Küçük chunk\'lar: Spesifik sorular için iyi')
        self.stdout.write('  - Büyük chunk\'lar: Genel context için iyi')
        self.stdout.write('  - RAGAS test komutuyla kalite ölçümü yapın') 