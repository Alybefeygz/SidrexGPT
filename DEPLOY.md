# 🚀 SidrexGPT Deployment Rehberi

Bu doküman SidrexGPT projesinin Render.com (backend) ve Vercel (frontend) üzerinden nasıl deploy edileceğini detaylı şekilde açıklar.

## 📋 Ön Hazırlık

### 1. Gerekli Hesaplar
- [GitHub](https://github.com) hesabı
- [Render.com](https://render.com) hesabı
- [Vercel](https://vercel.com) hesabı
- [OpenRouter.ai](https://openrouter.ai) API key

### 2. Repository Hazırlığı
```bash
git add .
git commit -m "Production ready deployment"
git push origin main
```

## 🗄️ Database Setup (Render PostgreSQL)

### 1. PostgreSQL Service Oluşturma
1. Render dashboard'a gidin
2. "New" → "PostgreSQL" seçin
3. Ayarları yapılandırın:
   - **Name**: `sidrexgpt-db`
   - **Database**: `sidrexgpt_db`
   - **User**: `sidrexgpt_user`
   - **Region**: Yakın bölge seçin

### 2. Database URL'ini Alın
PostgreSQL service oluşturulduktan sonra "Internal Database URL"'i kopyalayın.

## 🔧 Backend Deployment (Render)

### 1. Web Service Oluşturma
1. Render dashboard'da "New" → "Web Service"
2. GitHub repository'nizi bağlayın
3. Ayarları yapılandırın:

```
Name: sidrexgpt-backend
Environment: Python 3
Branch: main
Root Directory: backend
Build Command: pip install -r requirements.txt
Start Command: gunicorn core.wsgi:application --bind 0.0.0.0:$PORT
```

### 2. Environment Variables
Render'da "Environment" sekmesine gidin ve şu değişkenleri ekleyin:

```bash
# Django Core
SECRET_KEY=your-very-long-and-secure-secret-key-here-minimum-50-characters
DEBUG=False
ALLOWED_HOSTS=your-app-name.onrender.com

# Database
DATABASE_URL=postgresql://username:password@host:port/database

# OpenRouter AI
OPENROUTER_API_KEY=your-openrouter-api-key
OPENROUTER_BASE_URL=https://openrouter.ai/api/v1
OPENROUTER_MODEL=meta-llama/llama-3.2-3b-instruct:free

# CORS ve Frontend
FRONTEND_URL=https://your-frontend-domain.vercel.app
CORS_ALLOWED_ORIGINS=https://your-frontend-domain.vercel.app

# Security (Production)
SECURE_SSL_REDIRECT=True
SECURE_HSTS_SECONDS=31536000
SECURE_HSTS_INCLUDE_SUBDOMAINS=True
SECURE_HSTS_PRELOAD=True
```

### 3. Build ve Deploy
"Deploy Latest Commit" butonuna tıklayın. İlk deploy işlemi 5-10 dakika sürebilir.

### 4. Database Migration
Deploy tamamlandıktan sonra Render'ın shell özelliğini kullanarak:

```bash
python manage.py migrate
python manage.py createsuperuser
```

## 🌐 Frontend Deployment (Vercel)

### 1. Vercel'e Repository Bağlama
1. [Vercel Dashboard](https://vercel.com/dashboard)
2. "New Project" → GitHub repository seçin
3. **Root Directory**: `frontend` olarak ayarlayın

### 2. Environment Variables
Vercel'de "Settings" → "Environment Variables":

```bash
NEXT_PUBLIC_API_URL=https://your-backend-domain.onrender.com
NEXT_PUBLIC_API_BASE_URL=https://your-backend-domain.onrender.com/api
NEXT_PUBLIC_FRONTEND_URL=https://your-frontend-domain.vercel.app
NODE_ENV=production
```

### 3. Build Settings
Vercel otomatik olarak algılar, ama manuel kontrol için:

```bash
Build Command: npm run build
Output Directory: .next
Install Command: npm install
```

## 🔗 Domain Configuration

### Backend (Render)
1. Render'da "Settings" → "Custom Domains"
2. Domain ekleyin ve DNS ayarlarını yapın

### Frontend (Vercel)
1. Vercel'de "Settings" → "Domains"
2. Custom domain ekleyin

## ✅ Post-Deployment Checklist

### 1. Backend Kontrolü
- [ ] `https://your-backend-domain.onrender.com/admin/` erişilebilir
- [ ] `https://your-backend-domain.onrender.com/api/` API endpoints çalışıyor
- [ ] Database bağlantısı başarılı
- [ ] Static files yükleniyor

### 2. Frontend Kontrolü
- [ ] `https://your-frontend-domain.vercel.app` açılıyor
- [ ] API calls backend'e ulaşıyor
- [ ] Login/register işlemleri çalışıyor
- [ ] Chat sistemi aktif

### 3. Güvenlik Kontrolü
- [ ] HTTPS zorunlu
- [ ] Environment variables güvenli
- [ ] CORS ayarları doğru
- [ ] Rate limiting aktif

## 🔧 Debugging

### Backend Debug
Render'da "Events" sekmesinden logları kontrol edin:

```bash
# Yaygın hatalar:
# 1. Environment variable eksik
# 2. Database bağlantı hatası
# 3. Static files hatası
```

### Frontend Debug
Vercel'de "Functions" sekmesinden logları kontrol edin:

```bash
# Yaygın hatalar:
# 1. API URL yanlış
# 2. CORS hatası
# 3. Environment variable eksik
```

## 🚀 Automatic Deployments

### GitHub Actions (Opsiyonel)
`.github/workflows/deploy.yml` oluşturarak otomatik deployment:

```yaml
name: Deploy to Render and Vercel

on:
  push:
    branches: [ main ]

jobs:
  deploy:
    runs-on: ubuntu-latest
    steps:
    - uses: actions/checkout@v2
    
    # Backend tests
    - name: Test Backend
      run: |
        cd backend
        pip install -r requirements.txt
        python manage.py test
    
    # Frontend tests
    - name: Test Frontend
      run: |
        cd frontend
        npm install
        npm run build
```

## 📊 Monitoring

### Performance Monitoring
- Render'da Resource Usage kontrol edin
- Vercel'de Analytics kullanın
- Database performance Render PostgreSQL metrics

### Error Tracking
- Django settings'e logging configuration
- Sentry.io entegrasyonu (opsiyonel)

## 🔄 Updates ve Maintenance

### Güncelleme Süreçi
1. Development'da test edin
2. GitHub'a push yapın
3. Render ve Vercel otomatik deploy eder
4. Post-deployment testler yapın

### Backup
- Database backup: Render PostgreSQL otomatik backup
- Code backup: GitHub repository
- Environment variables: Güvenli yerde saklayın

## 📞 Destek

Deployment sırasında sorun yaşarsanız:

1. **Backend sorunları**: Render support
2. **Frontend sorunları**: Vercel support  
3. **Code sorunları**: GitHub Issues
4. **General sorular**: README.md dokümanı

## 🎉 Deployment Tamamlandı!

Tebrikler! SidrexGPT başarıyla deploy edildi. Artık production'da kullanıma hazır.

### Yararlı Linkler
- **Backend**: `https://your-backend-domain.onrender.com`
- **Frontend**: `https://your-frontend-domain.vercel.app`
- **Admin Panel**: `https://your-backend-domain.onrender.com/admin/`
- **API Docs**: `https://your-backend-domain.onrender.com/api/` 