# 🚀 SidrexGPT Render.com Deployment Rehberi

Bu rehber, SidrexGPT projesinin Render.com üzerinde nasıl deploy edileceğini adım adım açıklar.

## 📋 İçindekiler

1. [Ön Gereksinimler](#ön-gereksinimler)
2. [Render.com Hesap Kurulumu](#rendercom-hesap-kurulumu)
3. [PostgreSQL Veritabanı Kurulumu](#postgresql-veritabanı-kurulumu)
4. [Backend Deployment](#backend-deployment)
5. [Environment Variables Yapılandırması](#environment-variables-yapılandırması)
6. [Domain ve SSL Yapılandırması](#domain-ve-ssl-yapılandırması)
7. [Hata Ayıklama ve Monitoring](#hata-ayıklama-ve-monitoring)
8. [Bakım ve Güncelleme](#bakım-ve-güncelleme)

## 🔧 Ön Gereksinimler

### 1. Gerekli Hesaplar
- GitHub hesabı
- Render.com hesabı
- OpenRouter.ai API anahtarı

### 2. Yerel Geliştirme Ortamı
- Python 3.11.6 (runtime.txt'de belirtildiği gibi)
- Node.js ve npm
- Git

### 3. Repository Hazırlığı
```bash
# Tüm değişiklikleri commit'leyin
git add .
git commit -m "Render deployment için hazırlık"
git push origin main
```

## 💻 Render.com Hesap Kurulumu

1. [Render.com](https://render.com)'a gidin
2. GitHub hesabınızla kayıt olun
3. Email doğrulamasını tamamlayın
4. Billing bilgilerinizi ekleyin (Free tier ile başlayabilirsiniz)

## 🗄️ PostgreSQL Veritabanı Kurulumu

### 1. Yeni PostgreSQL Servisi Oluşturma
1. Render Dashboard → "New +"
2. "PostgreSQL" seçin
3. Veritabanı Ayarları:
   - **Name**: `sidrexgpt-db`
   - **Database**: `sidrexgpt`
   - **User**: `sidrexgpt_user`
   - **Region**: Frankfurt (EU Central)
   - **Plan**: Free (başlangıç için)

### 2. Veritabanı Bilgilerini Kaydetme
- **Internal Database URL**: postgresql://sidrexgpt_user:srR6gYAMpqpJtByc5wXPAOtzDq4p8Vbk@dpg-d1j7q46r433s73fvii60-a/sidrexgpt
- **External Database URL**: postgresql://sidrexgpt_user:srR6gYAMpqpJtByc5wXPAOtzDq4p8Vbk@dpg-d1j7q46r433s73fvii60-a.frankfurt-postgres.render.com/sidrexgpt
- **PSQL Command**: PGPASSWORD=srR6gYAMpqpJtByc5wXPAOtzDq4p8Vbk psql -h dpg-d1j7q46r433s73fvii60-a.frankfurt-postgres.render.com -U sidrexgpt_user sidrexgpt

## 🚀 Backend Deployment

### 1. Web Service Oluşturma
1. Render Dashboard → "New +" → "Web Service"
2. GitHub repository'nizi bağlayın
3. Repository seçin ve izin verin

### 2. Service Yapılandırması
```yaml
Name: sidrexgpt-backend
Environment: Python 3
Region: Frankfurt (EU Central)
Branch: main
Root Directory: backend
Build Command: ./build.sh
Start Command: gunicorn core.wsgi:application --bind 0.0.0.0:$PORT
```

### 3. Auto-Deploy Ayarları
- [x] Auto-Deploy: Yes
- [x] Pull Request Preview: Enable

## 🔐 Environment Variables Yapılandırması

### 1. Temel Django Ayarları
```bash
PYTHON_VERSION=3.11.6
SECRET_KEY=<güvenli-bir-secret-key-üretin>
DEBUG=False
ALLOWED_HOSTS=.onrender.com
DATABASE_URL=<postgresql-url-from-render>
```

### 2. OpenRouter API Ayarları
```bash
OPENROUTER_API_KEY=<your-api-key>
OPENROUTER_BASE_URL=https://openrouter.ai/api/v1
OPENROUTER_MODEL=meta-llama/llama-3.2-3b-instruct:free
```

### 3. Güvenlik Ayarları
```bash
SECURE_SSL_REDIRECT=True
SECURE_HSTS_SECONDS=31536000
SECURE_HSTS_INCLUDE_SUBDOMAINS=True
SECURE_HSTS_PRELOAD=True
CSRF_COOKIE_SECURE=True
SESSION_COOKIE_SECURE=True
```

## 🌐 Domain ve SSL Yapılandırması

### 1. Custom Domain Ekleme (Opsiyonel)
1. Render Dashboard → Service → Settings → Custom Domain
2. Domain'inizi ekleyin
3. DNS ayarlarını yapın:
   ```
   CNAME record:
   Name: www
   Value: <your-app>.onrender.com
   ```

### 2. SSL Sertifikası
- Render otomatik olarak Let's Encrypt SSL sağlar
- HTTPS yönlendirmesi otomatik aktif

## 🔍 Hata Ayıklama ve Monitoring

### 1. Log İzleme
1. Render Dashboard → Service → Logs
2. Farklı log seviyeleri:
   - Deploy Logs
   - System Logs
   - Custom Logs

### 2. Metrics İzleme
- CPU Kullanımı
- RAM Kullanımı
- Network Traffic
- Response Times

### 3. Yaygın Hataların Çözümü
1. **Build Hataları**
   ```bash
   # requirements.txt güncellemesi
   pip freeze > requirements.txt
   ```

2. **Database Bağlantı Hataları**
   ```bash
   # DATABASE_URL'i kontrol edin
   # Migrations'ları yeniden çalıştırın
   python manage.py migrate
   ```

3. **Static Files Hataları**
   ```bash
   python manage.py collectstatic --no-input
   ```

## 🔄 Bakım ve Güncelleme

### 1. Düzenli Bakım İşlemleri
```bash
# Veritabanı backup
pg_dump -U <username> <database> > backup.sql

# Dependencies güncelleme
pip install --upgrade -r requirements.txt
```

### 2. Güvenlik Güncellemeleri
- Düzenli güvenlik taraması yapın
- Dependencies'leri güncel tutun
- SSL sertifikasını kontrol edin

### 3. Performance İyileştirmeleri
- Cache kullanımını optimize edin
- Database indexleme yapın
- Static dosyaları CDN üzerinden servis edin

## 📞 Yardımcı Kaynaklar

### 1. Önemli Linkler
- Render Status Page: https://status.render.com
- Render Docs: https://render.com/docs
- Django Deployment Docs: https://docs.djangoproject.com/en/5.1/howto/deployment/

### 2. Hata Durumunda
1. Render Logs'u kontrol edin
2. Django error logs'u inceleyin
3. Database bağlantısını test edin
4. Environment variables'ı kontrol edin

## ✅ Deployment Kontrol Listesi

### 1. Ön Kontroller
- [ ] Tüm değişiklikler commit edildi
- [ ] requirements.txt güncel
- [ ] .env.example dosyası mevcut
- [ ] DEBUG=False ayarlandı

### 2. Database Kontrolleri
- [ ] Migrations çalıştırıldı
- [ ] Superuser oluşturuldu
- [ ] Veritabanı bağlantısı test edildi

### 3. Güvenlik Kontrolleri
- [ ] SECRET_KEY güvenli
- [ ] ALLOWED_HOSTS doğru
- [ ] SSL aktif
- [ ] CORS ayarları doğru

### 4. Final Kontroller
- [ ] Admin paneli erişilebilir
- [ ] Static dosyalar yükleniyor
- [ ] API endpoints çalışıyor
- [ ] Error logging aktif

## 🎉 Tebrikler!

Eğer bu rehberdeki tüm adımları başarıyla tamamladıysanız, SidrexGPT uygulamanız artık Render.com üzerinde çalışıyor olmalı. Herhangi bir sorunla karşılaşırsanız, yukarıdaki hata ayıklama bölümüne başvurabilir veya Render.com support ekibiyle iletişime geçebilirsiniz. 