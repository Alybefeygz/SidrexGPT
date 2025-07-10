from django.core.management.base import BaseCommand
from robots.rag_services import RAGService, normalize_text
from robots.models import Robot, RobotPDF
import logging

logger = logging.getLogger(__name__)

class Command(BaseCommand):
    help = 'Türkçe karakter desteğini test eder'

    def add_arguments(self, parser):
        parser.add_argument(
            '--robot-id',
            type=int,
            help='Test edilecek robot ID\'si'
        )

    def handle(self, *args, **options):
        self.stdout.write(self.style.NOTICE('🔍 Türkçe karakter testi başlıyor...'))
        
        robot_id = options.get('robot_id')
        if not robot_id:
            # İmuntus Kids robotunu bul
            try:
                robots = Robot.objects.all()
                self.stdout.write(f"📋 Mevcut robotlar: {[(r.id, r.name) for r in robots]}")
                
                robot = Robot.objects.filter(name__icontains='kids').first()
                if not robot:
                    robot = Robot.objects.first()
                    
                if robot:
                    robot_id = robot.id
                    pdf_count = robot.pdf_dosyalari.filter(is_active=True).count()
                    self.stdout.write(f"🤖 Robot seçildi: {robot.name} (ID: {robot_id}, PDF: {pdf_count})")
                else:
                    self.stdout.write(self.style.ERROR('❌ Hiç robot bulunamadı'))
                    return
            except Exception as e:
                self.stdout.write(self.style.ERROR(f'❌ Robot arama hatası: {e}'))
                return
        
        # Test senaryoları
        test_queries = [
            'imuntus kids',      # Doğru yazım
            'ımuntus kids',      # Türkçe ı
            'IMUNTUS KIDS',      # Büyük harf
            'İmuntus Kids',      # Türkçe İ
            'imuntüs kids',      # Türkçe ü
            'vitamin c',         # Normal
            'vitaminç',          # Türkçe ç
            'bağışıklık',        # Tam Türkçe
            'bagisiklik',        # Normalize
            'bağşıklık',         # Yanlış yazım (gerçek kullanıcı hatası)
            'bagsiklik',         # Tam yanlış
            'çocuğun bağışıklık sistemi',  # Gerçek soru parçası
            'çocuk bağışıklık',  # Kısa
            'bağışıklık sistemi uygun mu',  # Gerçek kullanıcı sorusu benzeri
        ]
        
        rag_service = RAGService()
        
        for query in test_queries:
            self.stdout.write(f"\n🔍 Test sorgusu: '{query}'")
            
            # Normalizasyon testi
            normalized = normalize_text(query)
            self.stdout.write(f"📝 Normalize: '{normalized}'")
            
            # RAG arama testi
            try:
                # Önce düşük threshold ile test et
                similar_chunks = rag_service.vector_service.search_with_fallback(
                    query=query,
                    robot_pdf_ids=[pdf.id for pdf in Robot.objects.get(id=robot_id).pdf_dosyalari.filter(is_active=True)],
                    top_k=5,
                    similarity_threshold=0.1  # Çok düşük threshold
                )
                
                if similar_chunks:
                    self.stdout.write(f"✅ {len(similar_chunks)} sonuç bulundu")
                    for i, chunk in enumerate(similar_chunks[:2]):  # İlk 2 sonuç
                        similarity = chunk.get('similarity', 0)
                        chunk_text = chunk.get('chunk_text', '')[:100]
                        self.stdout.write(f"   {i+1}. Benzerlik: {similarity:.3f} - '{chunk_text}...'")
                else:
                    self.stdout.write("❌ Sonuç bulunamadı (düşük threshold ile)")
                    
                    # Fuzzy search deneme
                    fuzzy_results = rag_service.vector_service.search_fuzzy_chunks(
                        query=query,
                        robot_pdf_ids=[pdf.id for pdf in Robot.objects.get(id=robot_id).pdf_dosyalari.filter(is_active=True)],
                        top_k=3,
                        similarity_threshold=0.1
                    )
                    
                    if fuzzy_results:
                        self.stdout.write(f"📝 Fuzzy search: {len(fuzzy_results)} sonuç")
                        for i, result in enumerate(fuzzy_results[:1]):
                            sim = result.get('similarity', 0)
                            text = result.get('chunk_text', '')[:50]
                            self.stdout.write(f"   Fuzzy {i+1}: {sim:.3f} - '{text}...'")
                    else:
                        self.stdout.write("❌ Fuzzy search'te de sonuç yok")
                    
            except Exception as e:
                self.stdout.write(self.style.ERROR(f"❌ Hata: {e}"))
        
        self.stdout.write(self.style.SUCCESS('\n✅ Türkçe karakter testi tamamlandı!'))
        self.stdout.write(self.style.NOTICE('💡 Sonuçları karşılaştırarak normalize_text fonksiyonunu optimize edebilirsiniz')) 