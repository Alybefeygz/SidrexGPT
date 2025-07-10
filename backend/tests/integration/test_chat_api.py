#!/usr/bin/env python
"""
Frontend Chat API'sini simüle eden test scripti
Gerçek chat endpoint'ini test eder
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

from robots.models import Robot, User
from robots.rag_services import RAGService
from django.contrib.auth.models import User
from django.test import RequestFactory
from robots.api.views import RobotChatView

def test_chat_api():
    """Chat API'sini test et"""
    
    print("🤖 Chat API Test Başlıyor...")
    
    # Robot bul
    robot = Robot.objects.filter(name__icontains='kids').first()
    if not robot:
        print("❌ İmuntus Kids robotu bulunamadı")
        return
    
    print(f"✅ Robot bulundu: {robot.name}")
    
    # Test soruları
    test_queries = [
        "çocuğumun bağşıklık sistemi çok düşük sence bu ürün ona uygun mu?",
        "İmuntus Kids nedir?",
        "C vitamini ne işe yarar?",
        "bağışıklık sistemi için iyi mi?",
        "4 yaşındaki çocuğum kullanabilir mi?"
    ]
    
    # Her soru için RAG test et
    rag_service = RAGService()
    
    for i, query in enumerate(test_queries, 1):
        print(f"\n🔍 Test {i}: '{query}'")
        
        try:
            # RAG context'i al
            context, citations = rag_service.get_relevant_context(
                query=query,
                robot_id=robot.id
            )
            
            if citations:
                print(f"✅ {len(citations)} kaynak bulundu")
                print(f"📝 Context: {len(context)} karakter")
                
                # En iyi sonuçları göster
                for j, citation in enumerate(citations[:2]):
                    similarity = citation.get('similarity', 0)
                    source = citation.get('source', 'Bilinmeyen')
                    print(f"   {j+1}. {source}: %{similarity*100:.1f}")
                
                # Context'te bağışıklık geçiyor mu kontrol et
                if 'bağışıklık' in context.lower() or 'bagisiklik' in context.lower():
                    print("🎯 Context'te bağışıklık bilgisi VAR!")
                else:
                    print("⚠️  Context'te bağışıklık bilgisi YOK")
                    
            else:
                print("❌ Kaynak bulunamadı")
                
        except Exception as e:
            print(f"❌ Hata: {e}")
    
    print("\n✅ Chat API testi tamamlandı!")

if __name__ == "__main__":
    test_chat_api() 