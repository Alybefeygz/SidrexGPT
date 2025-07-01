# SidrexGPT

SidrexGPT, markalara özel yapay zeka destekli bir soru-cevap platformudur. Her marka kendi özel robotlarını ve PDF belgelerini yönetebilir, kullanıcılarını kontrol edebilir ve özelleştirilmiş deneyimler sunabilir.

## 🚀 Özellikler

### 🤖 Robot Sistemi
- Üç farklı robot tipi ile özelleştirilmiş deneyimler
- PDF tabanlı akıllı soru-cevap sistemi
- Marka bazlı özelleştirilebilir robotlar
- Iframe entegrasyonu ile kolay kullanım

### 👥 Marka Yönetimi
- Paket türüne göre özelleştirilebilir kullanıcı limitleri
- Marka bazlı kullanıcı yönetimi
- Özelleştirilebilir PDF belge yönetimi
- Aktif/Pasif kullanıcı kontrolü

### 🛡️ Güvenlik
- Token tabanlı kimlik doğrulama
- Rate limiting koruması
- CORS güvenliği
- Rol tabanlı yetkilendirme sistemi

### 💅 Modern UI/UX
- Responsive tasarım
- Dark/Light tema desteği
- Toast bildirimleri
- Form validasyonları
- Yükleme durumu göstergeleri

## 🛠️ Teknoloji Stack'i

### Frontend
- **Framework**: Next.js 15.2.4
- **UI Kütüphaneleri**: 
  - Radix UI
  - TailwindCSS
  - React Hook Form
  - Zod
  - Axios
- **State Management**: React Context API
- **Tema**: next-themes

### Backend
- **Framework**: Django 5.1.6
- **API**: Django REST Framework 3.15.2
- **Veritabanı**: PostgreSQL
- **Authentication**: 
  - dj-rest-auth
  - django-allauth
  - django-rest-knox
- **PDF İşleme**: PyPDF2

## 📋 Gereksinimler

### Backend
- Python 3.x
- PostgreSQL
- Virtual Environment

### Frontend
- Node.js 18+
- npm veya yarn veya pnpm

## 🚀 Kurulum

### Backend Kurulumu

1. Virtual Environment Oluşturma:
```bash
python -m venv venv
source venv/bin/activate  # Linux/Mac
venv\Scripts\activate     # Windows
```

2. Bağımlılıkları Yükleme:
```bash
cd backend
pip install -r requirements.txt
```

3. Veritabanı Ayarları:
```bash
# .env dosyası oluştur
cp env.example .env
# .env dosyasını düzenle ve veritabanı bilgilerini gir
```

4. Veritabanı Migrasyonları:
```bash
python manage.py migrate
```

5. Superuser Oluşturma:
```bash
python manage.py createsuperuser
```

### Frontend Kurulumu

1. Bağımlılıkları Yükleme:
```bash
cd frontend
npm install   # veya yarn install veya pnpm install
```

2. Ortam Değişkenleri:
```bash
cp env.example .env
# .env dosyasını düzenle
```

## 🚀 Geliştirme Ortamını Başlatma

### Backend
```bash
cd backend
python manage.py runserver
```

### Frontend
```bash
cd frontend
npm run dev   # veya yarn dev veya pnpm dev
```

## 📚 API Endpointleri

### Kullanıcı Yönetimi
```
POST /api/auth/login/           # Kullanıcı girişi
POST /api/auth/logout/          # Çıkış
POST /api/auth/register/        # Kayıt
GET  /api/profile/profilleri/   # Profil listesi
```

### Profil Yönetimi
```
GET    /api/profile/profilleri/{id}/        # Profil detayı
PUT    /api/profile/profilleri/{id}/        # Profil güncelleme
DELETE /api/profile/profilleri/{id}/        # Profil silme
POST   /api/profile/profilleri/{id}/toggle_active/  # Aktif/Pasif yapma
```

### Marka Yönetimi
```
GET    /api/robots/brands/      # Marka listesi
POST   /api/robots/brands/      # Yeni marka oluşturma
PUT    /api/robots/brands/{id}/ # Marka güncelleme
DELETE /api/robots/brands/{id}/ # Marka silme
```

## 📁 Proje Yapısı

```
SidrexGPT/
├── backend/
│   ├── core/            # Ana Django uygulaması
│   ├── profiller/       # Kullanıcı profil yönetimi
│   └── robots/          # Robot ve PDF yönetimi
└── frontend/
    ├── app/
    │   ├── api-test/    # API test sayfası
    │   ├── brands/      # Marka yönetim sayfası
    │   ├── iframe/      # Robot iframe'leri
    │   ├── iletisim/    # İletişim sayfası
    │   ├── product/     # Ürün sayfaları
    │   ├── users/       # Kullanıcı yönetim sayfası
    │   └── yonetim/     # Admin yönetim paneli
    └── components/      # React komponentleri
```

## 🔒 Güvenlik Özellikleri

- Token tabanlı kimlik doğrulama
- Rate limiting koruması
- CORS güvenliği
- Rol tabanlı yetkilendirme
- Kullanıcı limiti kontrolü
- PDF dosya güvenliği

## 🎨 UI Komponentleri

- Özelleştirilmiş form elemanları
- Modal ve Dialog komponentleri
- Toast bildirimleri
- Loading states
- Responsive tasarım
- Dark/Light tema desteği

## 📄 Lisans

Bu proje özel lisans altında lisanslanmıştır. Tüm hakları saklıdır.

## 👥 Katkıda Bulunanlar

- Swifty Yazılım Ekibi

## 📞 İletişim

Sorularınız veya geri bildirimleriniz için:
- Email: [iletisim@swifty.com.tr](mailto:iletisim@swifty.com.tr)
- Website: [https://swifty.com.tr](https://swifty.com.tr) 