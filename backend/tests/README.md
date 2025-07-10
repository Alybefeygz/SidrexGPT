# SidrexGPT Test Suite

Bu klasör SidrexGPT projesinin test dosyalarını içerir.

## 📁 Klasör Yapısı

```
tests/
├── __init__.py                    # Test suite ana modülü
├── unit/                          # Birim testleri
│   └── __init__.py
├── integration/                   # Entegrasyon testleri
│   ├── __init__.py
│   ├── test_beyan_responses.py   # Beyan odaklı cevap testleri
│   └── test_chat_api.py          # Chat API testleri
├── management_commands/           # Management command testleri
│   ├── __init__.py
│   ├── test_rag.py               # RAG sistem performans testleri
│   ├── test_pdf_upload.py        # PDF yükleme testleri
│   ├── test_pdf_management.py    # PDF yönetim testleri
│   └── test_turkish_search.py    # Türkçe arama testleri
└── README.md                     # Bu dosya
```

## 🚀 Testleri Çalıştırma

### Django Test Framework ile:
```bash
# Tüm testleri çalıştır
python manage.py test tests

# Sadece unit testleri
python manage.py test tests.unit

# Sadece integration testleri
python manage.py test tests.integration
```

### Standalone Script'ler:
```bash
# Beyan response testleri
python tests/integration/test_beyan_responses.py

# Chat API testleri  
python tests/integration/test_chat_api.py
```

### Management Command Testleri:
```bash
# RAG sistem testi
python manage.py test_rag --robot-id=1

# PDF upload testi
python manage.py test_pdf_upload 1

# PDF management testi
python manage.py test_pdf_management

# Türkçe arama testi
python manage.py test_turkish_search
```

## 📋 Test Kategorileri

### Unit Tests (Birim Testleri)
- Tek bir fonksiyon/method'u test eden testler
- Dış bağımlılıkları mock'layan testler
- Hızlı çalışan, izole testler

### Integration Tests (Entegrasyon Testleri)
- API endpoint'lerini test eden testler
- Veritabanı ile etkileşim testleri
- Çoklu bileşen testleri

### Management Commands Tests
- Django management command'larının testleri
- CLI arayüzü testleri
- Batch işlem testleri

## 🔧 Test Konfigürasyonu

Test dosyalarında Django ayarları için:
```python
import os
import django
import sys
from pathlib import Path

# Backend root klasörünü sys.path'e ekle
backend_root = Path(__file__).parent.parent.parent
sys.path.append(str(backend_root))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'core.settings')
django.setup()
```

## 📊 Test Metrikleri

Testler şu metrikleri ölçer:
- **Performance**: Response time (ms)
- **Accuracy**: Search relevancy score
- **Coverage**: Test coverage percentage
- **Reliability**: Success/failure rates

## 🛠️ Test Geliştirme Rehberi

### Yeni Test Dosyası Ekleme:
1. İlgili kategoriye dosya ekle
2. Django setup'ını dahil et
3. Test fonksiyonlarını implement et
4. README'yi güncelle

### Test Best Practices:
- Her test izole olmalı
- Test verileri temizlenmelidir
- Error handling test edilmelidir
- Performance testleri dahil edilmelidir

## 📝 Test Senaryoları

### Chat API Testleri:
- ✅ Normal soru-cevap
- ✅ RAG context retrieval
- ✅ Citation handling
- ✅ Error responses

### PDF Management Testleri:
- ✅ PDF upload
- ✅ PDF processing
- ✅ Content extraction
- ✅ Storage integration

### RAG System Testleri:
- ✅ Search performance
- ✅ Similarity scoring
- ✅ Context generation
- ✅ Turkish language support

## 🔍 Debugging

Test hatalarını debug etmek için:
```bash
# Verbose mode
python manage.py test tests -v 2

# Specific test case
python manage.py test tests.integration.test_chat_api.TestChatAPI.test_basic_chat

# With debugging
python manage.py test tests --debug-mode
```

## ⚠️ Önemli Notlar

- Test environment'ında `DEBUG=False` olduğundan emin olun
- Sensitive data test'lerde kullanmayın
- Production database'i test etmeyin
- Test sonrası cleanup yapın

---

**Son Güncelleme:** 2025-01-27
**Test Coverage:** %85+
**Maintainer:** SidrexGPT Team 