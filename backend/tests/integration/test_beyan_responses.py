#!/usr/bin/env python
"""
Beyan odaklı cevapları test eden script
Gerçek chat API'sini simüle eder
"""

import os
import django
import sys
import json
from pathlib import Path

# Django setup - backend root klasörünü sys.path'e ekle
backend_root = Path(__file__).parent.parent.parent
sys.path.append(str(backend_root))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'core.settings')
django.setup()

from robots.models import Robot
from robots.rag_services import RAGService

def test_beyan_responses():
    """Beyan odaklı cevapları test et"""
    
    print("🧪 Beyan Response Test Başlıyor...")
    
    # Robot bul
    robot = Robot.objects.filter(name__icontains='kids').first()
    if not robot:
        print("❌ İmuntus Kids robotu bulunamadı")
        return
    
    print(f"✅ Robot bulundu: {robot.name}")
    
    # Test soruları - kullanıcının gerçek soruları
    test_queries = [
        {
            "soru": "çocuğumun bağşıklık sistemi çok düşük sence bu ürün ona uygun mu?",
            "beklenen_beyanlar": ["C vitamini bağışıklık", "Çinko bağışıklık"],
            "içermeli": ["katkıda bulunur", "doktor"]
        },
        {
            "soru": "çocuğum çok yoruluyor bu ona iyi olur mu?",
            "beklenen_beyanlar": ["C vitamini yorgunluk", "bitkinliğin azalması"],
            "içermeli": ["yorgunluk", "azalması", "katkıda bulunur"]
        },
        {
            "soru": "vitamin c ne işe yarar?",
            "beklenen_beyanlar": ["C vitamini", "bağışıklık", "kollajen"],
            "içermeli": ["katkıda bulunur"]
        },
        {
            "soru": "4 yaşındaki çocuğum için uygun mu?",
            "beklenen_beyanlar": ["4-6 yaş", "günlük"],
            "içermeli": ["yaş", "kullanım"]
        }
    ]
    
    rag_service = RAGService()
    
    for i, test in enumerate(test_queries, 1):
        soru = test["soru"]
        print(f"\n🔍 Test {i}: '{soru}'")
        
        try:
            # RAG context'i al
            context, citations = rag_service.get_relevant_context(
                query=soru,
                robot_id=robot.id
            )
            
            if citations:
                print(f"✅ {len(citations)} kaynak bulundu")
                
                # Context'te beklenen beyanlar var mı kontrol et
                context_lower = context.lower()
                found_beyanlar = []
                
                for beyan in test["beklenen_beyanlar"]:
                    if beyan.lower() in context_lower:
                        found_beyanlar.append(beyan)
                        print(f"   ✅ Beyan bulundu: '{beyan}'")
                    else:
                        print(f"   ❌ Beyan eksik: '{beyan}'")
                
                # Context'te olması gereken anahtar kelimeler
                for kelime in test["içermeli"]:
                    if kelime.lower() in context_lower:
                        print(f"   ✅ Anahtar kelime var: '{kelime}'")
                    else:
                        print(f"   ⚠️  Anahtar kelime eksik: '{kelime}'")
                
                # Context'in bir kısmını göster
                print(f"📋 Context önizleme: {context[:200]}...")
                
                # Beyan skorlaması
                beyan_score = len(found_beyanlar) / len(test["beklenen_beyanlar"]) * 100
                print(f"📊 Beyan skoru: %{beyan_score:.0f}")
                
            else:
                print("❌ Hiç kaynak bulunamadı")
                
        except Exception as e:
            print(f"❌ Hata: {e}")
    
    print("\n✅ Beyan response testi tamamlandı!")
    print("\n💡 Sonuç: Artık AI bu context'leri kullanarak beyan odaklı cevaplar verebilecek!")

def test_quotes_removal():
    """AI'nin tırnak kullanmamasını test et"""
    
    print("\n🔧 Tırnak Kaldırma Testi Başlatılıyor...")
    print("=" * 60)
    
    # Test soruları
    test_questions = [
        "Çocuğumun diş etleri için nasıl destek olabilir?",
        "C vitamini ne işe yarar?", 
        "Bağışıklık sistemi için iyi mi?",
        "ZZEN hakkında bilgi ver"
    ]
    
    try:
        from django.contrib.auth import get_user_model
        from django.test import RequestFactory
        from robots.api.views import RobotChatView
        
        User = get_user_model()
        
        # Test kullanıcısı ve robot al
        user = User.objects.filter(is_superuser=True).first()
        if not user:
            print("❌ Superuser bulunamadı!")
            return
            
        robot = Robot.objects.filter(name__icontains="imuntus kids").first()
        if not robot:
            print("❌ İmuntus Kids robotu bulunamadı!")
            return
            
        print(f"✅ Test Kullanıcısı: {user.username}")
        print(f"✅ Test Robotu: {robot.name}")
        print()
        
        # Her soru için test
        for i, question in enumerate(test_questions, 1):
            print(f"📝 Test {i}: {question}")
            print("-" * 40)
            
            # Chat view'i test et
            factory = RequestFactory()
            request = factory.post('/api/robots/chat/', {
                'message': question,
                'history': []
            }, content_type='application/json')
            request.user = user
            
            view = RobotChatView()
            view.setup(request)
            
            try:
                response = view.post(request, slug=robot.get_slug())
                
                if response.status_code == 200:
                    answer = response.data.get('answer', '')
                    
                    # Tırnak kontrolü - başında ve sonunda tırnak var mı?
                    starts_with_quote = answer.strip().startswith('"')
                    ends_with_quote = answer.strip().endswith('"')
                    has_quote_wrap = starts_with_quote and ends_with_quote
                    
                    print(f"📤 Yanıt: {answer}")
                    print(f"🔍 Tırnak Sarmalama: {'❌ VAR - PROBLEM!' if has_quote_wrap else '✅ YOK - TEMİZ'}")
                    
                    if has_quote_wrap:
                        print(f"⚠️  UYARI: Yanıt tırnak ile sarmalanmış!")
                    
                else:
                    print(f"❌ API Hatası: {response.status_code}")
                    print(f"Hata: {response.data}")
                    
            except Exception as e:
                print(f"❌ Test Hatası: {e}")
            
            print()
        
        print("=" * 60)
        print("✅ Tırnak Kaldırma Testi Tamamlandı!")
        
    except Exception as e:
        print(f"❌ Genel Test Hatası: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    test_beyan_responses()
    test_quotes_removal() 