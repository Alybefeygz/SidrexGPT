# AI-Powered Brand Chatbox 🤖

Markalara özel, yapay zeka destekli akıllı sohbet robotu platformu. RAG (Retrieval-Augmented Generation) metodolojisi kullanılarak geliştirilmiş bu sistem, markaların kendi dokümanları üzerinden özelleştirilmiş AI asistanlar oluşturmasına olanak sağlar.

## 🎯 Proje Hakkında

Bu platform, markaların kendi dokümanlarını kullanarak özelleştirilmiş yapay zeka chatbot'ları oluşturmasına olanak tanır. İlk olarak Sidrex markası için geliştirilen ve test edilen sistem, başarılı sonuçlar elde edildikten sonra diğer markalar için de kullanıma açılmıştır.

### 🧠 RAG (Retrieval-Augmented Generation) Metodolojisi

Sistemimiz, modern RAG metodolojisini kullanarak çalışır:

1. **Doküman İndeksleme**: 
   - Marka dokümanları yüklenir ve vektör veritabanında indekslenir
   - Her doküman, semantik arama için optimize edilmiş vektörlere dönüştürülür
   - Dokümanlar chunk'lara bölünerek detaylı analiz yapılır

2. **Akıllı Retrieval**:
   - Kullanıcı soruları semantik olarak analiz edilir
   - En alakalı doküman parçaları vektör veritabanından çekilir
   - Bağlam-bilinçli yanıtlar için çoklu doküman parçaları birleştirilir

3. **Yapay Zeka Entegrasyonu**:
   - OpenRouter API üzerinden gelişmiş dil modelleri kullanılır
   - Dokümanlardan alınan bilgiler ile zenginleştirilmiş yanıtlar üretilir
   - Marka tone-of-voice'una uygun yanıtlar sağlanır

## 🌟 Paket Seçenekleri

### 🎯 Normal Paket
- Tek robot desteği
- 5 PDF doküman limiti
- Aylık 1000 soru hakkı
- Temel analitikler

### 💫 Pro Paket
- 2 robot desteği
- 15 PDF doküman limiti
- Aylık 5000 soru hakkı
- Gelişmiş analitikler
- Özelleştirilmiş robot kişiliği

### 👑 Premium Paket
- Sınırsız robot desteği
- Sınırsız PDF doküman
- Sınırsız soru hakkı
- Detaylı analitikler ve raporlama
- Tam özelleştirme seçenekleri
- Öncelikli destek

## 🛠️ Teknik Detaylar

### Backend Teknolojileri
- **Ana Framework**: Django 5.1.6
- **API Framework**: Django REST Framework 3.15.2
- **Veritabanı**: PostgreSQL
- **Kimlik Doğrulama**: 
  - dj-rest-auth
  - django-allauth
  - django-rest-knox
- **PDF İşleme**: PyPDF2
- **Vektör Veritabanı**: pgvector
- **Cache**: Redis
- **Task Queue**: Celery
- **WebSocket**: Django Channels

### Frontend Teknolojileri
- **Framework**: Next.js 15.2.4
- **UI Kütüphaneleri**: 
  - Radix UI (Temel komponentler)
  - TailwindCSS (Styling)
  - Shadcn UI (Hazır komponentler)
- **Form Yönetimi**: 
  - React Hook Form
  - Zod (Validasyon)
- **State Yönetimi**: 
  - React Context API
  - Zustand
- **HTTP Client**: Axios
- **WebSocket Client**: Socket.IO Client
- **Tema**: next-themes

## 📚 API Endpoints

### 🔐 Kimlik Doğrulama
```
POST   /api/auth/login/           # Kullanıcı girişi
POST   /api/auth/logout/          # Çıkış
POST   /api/auth/register/        # Yeni kullanıcı kaydı
POST   /api/auth/token/refresh/   # Token yenileme
GET    /api/auth/user/           # Aktif kullanıcı bilgisi
```

### 👤 Profil Yönetimi
```
GET    /api/profile/profilleri/                    # Profil listesi
GET    /api/profile/profilleri/{id}/              # Profil detayı
PUT    /api/profile/profilleri/{id}/              # Profil güncelleme
DELETE /api/profile/profilleri/{id}/              # Profil silme
POST   /api/profile/profilleri/{id}/toggle_active/ # Aktif/Pasif yapma
```

### 🤖 Robot Yönetimi
```
GET    /api/robots/                # Robot listesi
POST   /api/robots/               # Yeni robot oluşturma
GET    /api/robots/{id}/          # Robot detayı
PUT    /api/robots/{id}/          # Robot güncelleme
DELETE /api/robots/{id}/          # Robot silme
POST   /api/robots/{id}/train/    # Robot eğitimi başlatma
GET    /api/robots/{id}/status/   # Eğitim durumu kontrolü
```

### 📄 PDF Yönetimi
```
GET    /api/robots/pdfs/          # PDF listesi
POST   /api/robots/pdfs/          # PDF yükleme
DELETE /api/robots/pdfs/{id}/     # PDF silme
GET    /api/robots/pdfs/{id}/     # PDF detayı ve analiz
POST   /api/robots/pdfs/analyze/  # PDF analizi başlatma
```

### 🏢 Marka Yönetimi
```
GET    /api/robots/brands/         # Marka listesi
POST   /api/robots/brands/         # Yeni marka oluşturma
GET    /api/robots/brands/{id}/    # Marka detayı
PUT    /api/robots/brands/{id}/    # Marka güncelleme
DELETE /api/robots/brands/{id}/    # Marka silme
```

### 💬 Sohbet
```
POST   /api/chat/message/         # Mesaj gönderme
GET    /api/chat/history/         # Sohbet geçmişi
DELETE /api/chat/history/         # Geçmiş temizleme
WS     /ws/chat/{room_id}/       # WebSocket sohbet bağlantısı
```

## 📦 Kurulum

### Backend Kurulumu

1. **Gereksinimler**:
```bash
# Python 3.x ve PostgreSQL gereklidir
python -m venv venv
source venv/bin/activate  # Linux/Mac
venv\Scripts\activate     # Windows
```

2. **Bağımlılıkları Yükleme**:
```bash
cd backend
pip install -r requirements.txt
```

3. **Veritabanı Ayarları**:
```bash
# .env dosyası oluştur
cp env.example .env
# Veritabanı bilgilerini düzenle
```

4. **Migrasyonlar**:
```bash
python manage.py migrate
python manage.py createsuperuser
```

### Frontend Kurulumu

1. **Node.js Bağımlılıkları**:
```bash
cd frontend
npm install   # veya yarn install veya pnpm install
```

2. **Ortam Değişkenleri**:
```bash
cp env.example .env.local
# .env.local dosyasını düzenle
```

## 🚀 Geliştirme Ortamı

### Backend Başlatma
```bash
cd backend
python manage.py runserver
```

### Frontend Başlatma
```bash
cd frontend
npm run dev   # veya yarn dev veya pnpm dev
```

## 📁 Proje Yapısı

```
project/
├── backend/
│   ├── core/            # Ana Django uygulaması
│   │   ├── settings/    # Ortam bazlı ayarlar
│   │   ├── urls.py      # Ana URL yapılandırması
│   │   └── wsgi.py      # WSGI yapılandırması
│   ├── profiller/       # Kullanıcı profil yönetimi
│   │   ├── api/         # Profile API endpoints
│   │   ├── models.py    # Profil modelleri
│   │   └── services.py  # İş mantığı servisleri
│   └── robots/          # Robot ve PDF yönetimi
│       ├── api/         # Robot API endpoints
│       ├── models.py    # Robot modelleri
│       └── services.py  # Robot servisleri
└── frontend/
    ├── app/            # Next.js sayfa yapısı
    │   ├── api-test/   # API test sayfası
    │   ├── brands/     # Marka yönetimi
    │   ├── iframe/     # Robot iframe'leri
    │   └── product/    # Ürün sayfaları
    ├── components/     # React komponentleri
    │   ├── common/     # Genel komponentler
    │   ├── forms/      # Form komponentleri
    │   └── robots/     # Robot komponentleri
    └── lib/           # Yardımcı fonksiyonlar
```

## 🔒 Güvenlik Özellikleri

- Token tabanlı JWT kimlik doğrulama
- Rate limiting ve DDoS koruması
- CORS güvenlik yapılandırması
- SQL injection koruması
- XSS ve CSRF koruması
- Rol tabanlı yetkilendirme
- Veri şifreleme
- Güvenli dosya yükleme kontrolleri

## 🎨 UI/UX Özellikleri

- Responsive tasarım (Mobile-first yaklaşım)
- Dark/Light tema desteği
- Özelleştirilebilir marka renkleri
- Erişilebilirlik (WCAG 2.1 uyumlu)
- Yükleme durumu göstergeleri
- Form validasyonları
- Toast bildirimleri
- Modal ve Dialog komponentleri
- Sürükle-bırak dosya yükleme
- Real-time chat arayüzü

## 🚀 Başarı Hikayesi: Sidrex

Platform ilk olarak Sidrex markası için geliştirildi ve test edildi. Bu süreçte:
- 10,000+ başarılı kullanıcı etkileşimi
- %95 doğruluk oranı
- Müşteri hizmetleri yükünde %40 azalma
- Kullanıcı memnuniyetinde belirgin artış

Bu başarılı pilot uygulamadan sonra sistem diğer markalar için de kullanıma açıldı.

## 🔒 Güvenlik ve Gizlilik

- Her marka için izole edilmiş veri ortamı
- End-to-end şifreleme
- GDPR uyumlu veri işleme
- Düzenli güvenlik güncellemeleri
- Veri sızıntısı koruması

