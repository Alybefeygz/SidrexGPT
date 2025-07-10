# RAG Optimizasyon ve Geliştirme PRD (Product Requirements Document)

## 1. Genel Bakış ve Amaç

Bu doküman, mevcut SidrexGPT RAG sisteminin performansını, doğruluğunu ve güvenilirliğini artırmak için gereken teknik adımları ve stratejileri tanımlar. Amaç, kullanıcıya daha isabetli, daha hızlı ve kaynaklarla desteklenmiş yanıtlar sunarak sistemin genel kalitesini ve kullanıcı güvenini artırmaktır.

**Ana Hedefler:**
- **🔍 Daha Doğru Retrieval:** Doğru chunk boyutu ve daha iyi embedding modelleri ile anlamsal olarak en alakalı doküman parçalarını bulmak.
- **🧠 Daha Güvenilir Generation:** Kaynak gösterme (citations), olgu kontrolü (fact-checking) ve filtreleme katmanları ile LLM'in ürettiği yanıtlarda "halüsinasyon" riskini minimize etmek.
- **🚀 Daha Hızlı Yanıt:** Vektör veritabanı sorgularını ve LLM'e gönderilen bağlamı (context) optimize ederek uçtan uca yanıt süresini düşürmek.
- **📊 Sürekli İzleme:** RAGAS veya ARES gibi metriklerle sistem performansını sürekli ölçerek proaktif iyileştirmeler yapmak.

---

## 2. Mevcut Durum Tespiti (As-Is)

### ✅ Güçlü Yönler

- **Amaca Hizmet Eden Veri Kaynağı:** Statik ama güncellenebilir PDF tabanlı kaynak kullanımı (marka belgeleri, belediye yönetmelikleri) proje hedefleriyle uyumludur.
- **Yetkilendirme & KVKK Uyumu:** Erken aşamada düşünülen yetkilendirme ve yasal uyumluluk, sistemin ticari sürdürülebilirliği için sağlam bir temel oluşturmaktadır.
- **Mantıklı Sorgu Akışı:** `Embedding -> Retrieval -> Generation` akışı, modern RAG mimarileri için standart ve doğru bir yaklaşımdır.
- **Etkin Vektör DB Entegrasyonu:** `pgvector` kullanımı, başlangıç için basit ve PostgreSQL ile entegre, yönetimi kolay bir çözümdür.
- **Streaming Yanıt:** Yanıtların akış olarak verilmesi, son kullanıcı deneyimini önemli ölçüde iyileştirmektedir.

### ❌ Zayıf Yönler ve Riskler

- **Chunklama Belirsizliği:** Dokümanların hangi boyutta (`chunk_size`) ve ne kadar örtüşme (`overlap`) ile parçalandığı net değildir. Bu durum, anlamsal bütünlüğün kaybolmasına ve isabetsiz retrieval'a yol açabilir.
- **Embedding Kalitesi:** Mevcut embedding modelinin (`text-embedding-ada-002` varsayımıyla) güncel SOTA (State-of-the-Art) modellerle kıyaslandığında geri kalma riski vardır. Bu, arama kalitesini doğrudan etkiler.
- **Fact-Checking Eksikliği:** LLM'den gelen yanıtların, sunulan kaynaklarla tutarlılığını kontrol eden bir doğrulama katmanı yoktur. Bu, "halüsinasyon" riskini artırır.
- **Kaynak Gösterme (Citation) Eksikliği:** Yanıtların hangi dokümanın hangi bölümünden alındığını belirten bir mekanizma olmaması, kullanıcı güvenini zedeler.
- **Performans Ölçümleme Eksikliği:** Yanıt süreleri, `faithfulness` (sadakat), ve `recall` (erişim) gibi kritik metrikler otomatik olarak ölçülmemektedir. Bu, "sessiz hataların" fark edilmesini engeller.
- **Çok Dilli Destek Kısıtı:** Mevcut altyapı sadece Türkçe üzerine kuruludur ve gelecekteki çok dilli talepleri karşılamakta zorlanabilir.

---

## 3. Uygulanacak Geliştirmeler ve Aksiyon Planı

Aşağıdaki adımlar, yukarıda belirtilen zayıf yönleri gidermek ve sistemi optimize etmek için uygulanacaktır.

### ✅ 1) Chunklama Stratejisini Test ve Optimize Etme
**Problem:** Yanlış chunk boyutu, anlamsal bütünlüğü bozarak isabetsiz sonuçlara neden olur.
**Aksiyon:**
- `AI-powered-chatbox/backend/management/commands/populate_pdf_content.py` dosyasını parametrik hale getir. `chunk_size` ve `chunk_overlap` değerlerinin komut satırından veya bir yapılandırma dosyasından okunmasını sağla.
- **Test Senaryoları:**
  - **Senaryo A (Mevcut Durum):** Baseline olarak ölç.
  - **Senaryo B (Daha Küçük Parçalar):** `chunk_size=512`, `chunk_overlap=100` (yaklaşık %20). Spesifik cevaplar için ideal olabilir.
  - **Senaryo C (Daha Büyük Parçalar):** `chunk_size=1024`, `chunk_overlap=200` (yaklaşık %20). Genel paragrafların bütünlüğünü korumak için daha iyi olabilir.
- **Uygulama:** Her senaryo için ayrı bir test veri seti (örnek sorgular ve beklenen yanıtlar) oluştur. Sonuçları `RAGAS` ile değerlendirip en iyi `recall` ve `faithfulness` skorunu veren konfigürasyonu seç.

### ✅ 2) Embedding Modelini Güncelleme ve Test Etme
**Problem:** `text-embedding-ada-002` eski kalmış olabilir. Daha iyi modeller, anlamsal yakınlığı daha iyi bularak retrieval kalitesini artırır.
**Aksiyon:**
- `AI-powered-chatbox/backend/robots/services.py` veya ilgili embedding fonksiyonunu model değiştirilebilecek şekilde refactor et.
- **Test Edilecek Modeller:**
  - **OpenAI:** `text-embedding-3-small`, `text-embedding-3-large` (Maliyet/performans analizi yap).
  - **Açık Kaynak:** `BGE-M3`, `E5-Mistral-7B-instruct` gibi MTEB (Massive Text Embedding Benchmark) lideri modelleri test et. Bunlar Hugging Face üzerinden kullanılabilir.
- **Uygulama:** Farklı embedding modelleri ile oluşturulan indeksler üzerinde aynı test sorgu setini çalıştır. Retrieval metriklerini (`hit rate`, `MRR`) karşılaştır.

### ✅ 3) `RAGAS` ile Otomatik Skorlama Entegrasyonu
**Problem:** Performans metrikleri manuel olarak takip edilemiyor.
**Aksiyon:**
- Projeye `RAGAS` kütüphanesini ekle (`pip install ragas`).
- Yeni bir yönetim komutu oluştur: `python manage.py evaluate_rag`. Bu komut:
  1. Tanımlı bir test setini (`soru`, `beklenen_cevap`, `kaynak_metin` içeren bir CSV/JSON) okur.
  2. Her soru için RAG sisteminden yanıt (`answer`) ve bulunan kaynakları (`contexts`) alır.
  3. Bu verilerle `faithfulness`, `answer_relevancy`, `context_recall` metriklerini hesaplar.
  4. Sonuçları bir raporda (log veya dosya) sunar.
- **Uygulama:** Bu komutu CI/CD pipeline'ına ekleyerek her büyük değişiklikten sonra otomatik çalışmasını sağla.

### ✅ 4) Context Window ve `top_k` Optimizasyonu
**Problem:** LLM'e çok fazla veya alakasız context göndermek maliyeti artırır ve yanıt kalitesini düşürür ("Lost in the Middle" problemi).
**Aksiyon:**
- Vektör aramasının yapıldığı yerde (`pgvector` sorgusu) döndürülen chunk sayısını (`top_k`) ayarlanabilir bir parametre yap.
- **Test Senaryoları:** `top_k=3`, `top_k=5`, `top_k=7` gibi farklı değerleri dene.
- **Uygulama:** `RAGAS` skorlarına bakarak en iyi `faithfulness` / `answer_relevancy` dengesini sunan `top_k` değerini bul. Az sayıda ama çok isabetli chunk genellikle en iyi sonucu verir.

### ✅ 5) Kaynak Gösterme (Citation) Mekanizması Ekleme
**Problem:** Kullanıcı, yanıtın hangi bilgiye dayandığını göremiyor.
**Aksiyon:**
- **Backend:** API yanıtını güncelle. Sadece metin (`answer`) yerine, kaynağı da içeren bir JSON nesnesi döndür.
  ```json
  {
    "answer": "Evet, Mag4Ever günde iki kez kullanılmalıdır.",
    "citations": [
      {
        "source": "Mag4Ever Kullanım Kılavuzu.pdf",
        "content": "...Mag4Ever ürününün sabah ve akşam olmak üzere günde iki kez kullanılması tavsiye edilir...",
        "page": 4
      }
    ]
  }
  ```
- **Frontend:** `FirstRobotChatBox.tsx` ve benzeri bileşenleri bu yeni API yanıtını işleyecek şekilde güncelle. Yanıtın altında, tıklanabilir veya üzerine gelince içeriği gösteren bir "Kaynaklar" bölümü oluştur.

### ✅ 6) LLM Yanıtlarını Filtreleme ve Doğrulama
**Problem:** LLM, istenmeyen (toxic) veya hatalı formatta yanıtlar üretebilir.
**Aksiyon:**
- LLM'den yanıt alındıktan sonra, kullanıcıya gönderilmeden önce çalışacak bir `post-processing` fonksiyonu ekle.
- **Filtreler:**
  1. **Toxicity Filter:** Basit bir anahtar kelime listesi veya `detoxify` gibi bir kütüphane ile temel bir toksisite kontrolü yap.
  2. **Schema Validation:** Eğer LLM'den belirli bir formatta (örn. JSON) yanıt bekleniyorsa, yanıtın bu şemaya uygunluğunu Pydantic gibi bir araçla doğrula.
  3. **Fact-Checking (İleri Seviye):** LLM'den gelen yanıttaki temel iddiaları, `context` olarak sunulan metinle karşılaştıran ikinci bir, daha basit LLM çağrısı yap. ("Bu iddia, verilen metinde geçiyor mu? EVET/HAYIR").

### ✅ 7) Sorgu Ön İşleme (Query Pre-processing)
**Problem:** Kullanıcı sorguları "gürültülü" olabilir (yazım hataları, gereksiz kelimeler).
**Aksiyon:**
- Embedding'e gönderilmeden önce sorguyu temizleyen bir `pre-processing` adımı ekle.
- **Adımlar:**
  1. **Stopword Temizliği:** "ve", "ile", "ama" gibi anlamsal değeri düşük kelimeleri çıkar.
  2. **Lemmatization/Stemming:** Kelimeleri köklerine indirgeyerek anlamsal aramayı güçlendir (Türkçe için `Zemberek` kütüphanesi kullanılabilir).
  3. **Query Expansion (İleri Seviye):** Kullanıcının sorgusuna eş anlamlı kelimeler veya ilgili terimler ekleyerek arama kapsamını genişlet (bunu bir LLM çağrısı ile yapabilirsin).

### ✅ 8) Vector DB Performansını İyileştirme
**Problem:** Veri miktarı arttıkça `pgvector` yavaşlayabilir.
**Aksiyon:**
- `pgvector` indekslerini `HNSW` (Hierarchical Navigable Small World) veya `IVF_FLAT` algoritmalarıyla oluştur. Bu, `exact nearest neighbor` yerine `approximate nearest neighbor` (ANN) araması yaparak hızı ciddi şekilde artırır.
  ```sql
  CREATE INDEX ON items USING hnsw (embedding vector_l2_ops);
  ```
- **Alternatifler:** Eğer `pgvector` yetersiz kalırsa, `Qdrant`, `Weaviate` veya `Pinecone` gibi yönetilen, yüksek performanslı vektör veritabanlarını test et.

### ✅ 9) Sorgu Loglarını Geri Besleme Döngüsü İçin Kullanma
**Problem:** Hatalı yanıtlar tespit edilse bile bu bilgi sisteme geri beslenmiyor.
**Aksiyon:**
- Kullanıcı sorgularını, LLM yanıtlarını, bulunan `context`'leri ve (varsa) kullanıcı geri bildirimlerini (👍/👎) yapısal bir şekilde logla.
- Bu logları düzenli olarak analiz et. Özellikle "beğenilmeyen" yanıtları ve `RAGAS` skorları düşük olanları incele.
- **Fine-tuning:** Bu "zor" örneklerden oluşan bir veri seti oluşturarak, gelecekte embedding modelini veya LLM'i bu verilerle `fine-tune` etmeyi planla.

### ✅ 10) Yedekleme & Felaket Kurtarma Stratejisini Güçlendirme
**Problem:** Veri kaybı veya sistem çökmesi durumunda geri dönüş planı net değil.
**Aksiyon:**
- **S3:** PDF dosyalarının saklandığı S3 bucket için **sürümlemeyi (versioning)** kesin olarak aktive et. Bu, yanlışlıkla silinen veya üzerine yazılan dosyaların kurtarılmasını sağlar.
- **Veritabanı:** PostgreSQL veritabanı için günlük otomatik yedeklemeleri (snapshot) ve Point-in-Time Recovery (PITR) özelliğini etkinleştir. Vektör indekslerini de içeren DB snapshot'ları haftalık olarak güvenli bir yerde saklanmalı.
- **Altyapı:** Mümkünse, altyapıyı `Docker Compose` veya `Terraform` gibi IaC (Infrastructure as Code) araçlarıyla tanımla. Bu, felaket anında tüm sistemi farklı bir ortamda hızla yeniden kurmayı sağlar. 