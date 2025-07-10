from django.core.management.base import BaseCommand
from robots.models import Robot
from robots.rag_services import RAGService
import time
import json

class Command(BaseCommand):
    help = 'RAG sistemini test eder ve performans ölçümü yapar.'

    def add_arguments(self, parser):
        parser.add_argument(
            '--robot-id',
            type=int,
            help='Test edilecek robot ID'
        )
        
        parser.add_argument(
            '--query',
            type=str,
            help='Test sorgusu'
        )

    def handle(self, *args, **options):
        robot_id = options.get('robot_id')
        query = options.get('query')
        
        self.stdout.write(self.style.NOTICE('🧪 RAG Sistem Testi Başlıyor...'))
        
        # RAG servisi
        rag_service = RAGService()
        
        # Test senaryoları
        test_queries = [
            "Sidrex nedir?",
            "Ürün nasıl kullanılır?", 
            "Güvenlik önlemleri nelerdir?",
            "Yan etkiler var mı?",
            "Çocuklar için güvenli mi?"
        ]
        
        if query:
            test_queries = [query]
        
        if robot_id:
            robots = Robot.objects.filter(id=robot_id)
        else:
            robots = Robot.objects.all()
        
        for robot in robots:
            self.stdout.write(f"\n🤖 Robot: {robot.name}")
            
            for test_query in test_queries:
                self.stdout.write(f"\n❓ Soru: {test_query}")
                
                # Performans ölçümü
                start_time = time.time()
                
                try:
                    context, citations = rag_service.get_relevant_context(
                        query=test_query,
                        robot_id=robot.id
                    )
                    
                    end_time = time.time()
                    response_time = (end_time - start_time) * 1000  # ms
                    
                    # Sonuçları göster
                    self.stdout.write(f"⏱️  Yanıt Süresi: {response_time:.1f}ms")
                    self.stdout.write(f"📚 Bulunan Kaynaklar: {len(citations)}")
                    
                    if citations:
                        self.stdout.write(f"🎯 En Yüksek Benzerlik: %{citations[0]['similarity']*100:.1f}")
                        
                        # Citation'ları listele
                        for i, citation in enumerate(citations[:3], 1):  # İlk 3'ü göster
                            self.stdout.write(
                                f"   {i}. {citation['source']} "
                                f"(%{citation['similarity']*100:.1f}) - "
                                f"{citation['content'][:100]}..."
                            )
                    else:
                        self.stdout.write(self.style.WARNING("⚠️ İlgili kaynak bulunamadı"))
                    
                    # Context uzunluğu
                    context_length = len(context)
                    self.stdout.write(f"📝 Context Uzunluğu: {context_length} karakter")
                    
                    # Performans değerlendirmesi
                    if response_time < 500:
                        performance = "Mükemmel"
                        color = self.style.SUCCESS
                    elif response_time < 1000:
                        performance = "İyi"
                        color = self.style.WARNING
                    else:
                        performance = "Yavaş"
                        color = self.style.ERROR
                    
                    self.stdout.write(color(f"📊 Performans: {performance}"))
                    
                except Exception as e:
                    self.stdout.write(
                        self.style.ERROR(f"❌ Hata: {e}")
                    )
        
        self.stdout.write(self.style.SUCCESS('\n✅ Test tamamlandı!'))
        
        # Genel performans önerileri
        self.stdout.write(self.style.NOTICE('\n💡 Performans Önerileri:'))
        self.stdout.write('  - 500ms altı: Mükemmel kullanıcı deneyimi')
        self.stdout.write('  - 500-1000ms: Kabul edilebilir')
        self.stdout.write('  - 1000ms üstü: Optimizasyon gerekli')
        self.stdout.write('\n🔧 Optimizasyon İpuçları:')
        self.stdout.write('  - top_k değerini azaltın (3-5 arası)')
        self.stdout.write('  - chunk_size\'ı optimize edin')
        self.stdout.write('  - similarity_threshold\'u artırın') 