# SidrexGPT Projesini Render.com'da Canlıya Alma Kılavuzu (Detaylı Sürüm)

Bu kılavuz, SidrexGPT projesini (Django backend ve Next.js frontend) `Render.com` platformunda, her adımı ayrıntılı bir şekilde açıklayarak nasıl başarılı bir şekilde canlıya alacağınızı gösterir.

---

## İçindekiler
1.  [Ön Hazırlıklar ve Kontroller](#1-ön-hazırlıclar-ve-kontroller)
2.  [Adım 1: Veritabanı Bağlantı Bilgilerini Hazırlama](#2-adım-1-veritabanı-bağlantı-bilgilerini-hazırlama)
    *   [Seçenek A: Render PostgreSQL Kullanımı](#seçenek-a-render-postgresql-kullanımı-yeni-başlayanlar-için-önerilir)
    *   [Seçenek B: Mevcut Supabase Veritabanını Kullanma](#seçenek-b-mevcut-supabase-veritabanını-kullanma)
3.  [Adım 2: Django Backend'in Kurulumu](#3-adım-2-django-backendin-kurulumu)
    *   [2.1: Web Servisi Oluşturma](#31-web-servisi-olusturma)
    *   [2.2: Backend Ortam Değişkenleri (Çok Önemli)](#32-backend-ortam-degiskenleri-cok-önemli)
4.  [Adım 3: Next.js Frontend'in Kurulumu](#4-adım-3-nextjs-frontendin-kurulumu)
    *   [4.1: Statik Site Oluşturma](#41-statik-site-olusturma)
    *   [4.2: Frontend Ortam Değişkeni](#42-frontend-ortam-degiskeni)
5.  [Adım 4: Canlıya Alma ve Sonrası Kontroller](#5-adım-4-canlıya-alma-ve-sonrası-kontroller)
    *   [5.1: Dağıtım Sürecini İzleme](#51-dagıtım-sürecini-izleme)
    *   [5.2: Yönetici (Superuser) Hesabı Oluşturma](#52-yönetici-superuser-hesabı-olusturma)
    *   [5.3: Fonksiyonel Testler](#53-fonksiyonel-testler)
6.  [Ek Bilgiler ve Sorun Giderme](#6-ek-bilgiler-ve-sorun-giderme)

---

## 1. Ön Hazırlıklar ve Kontroller

Dağıtıma başlamadan önce projenizin hazır olduğundan emin olalım.

-   **Render.com Hesabı:** Eğer yoksa, [Render.com](https://render.com/) adresinden ücretsiz bir hesap oluşturun.
-   **GitHub Hesabı:** Proje kodunuzun tamamının bir GitHub (veya GitLab/Bitbucket) deposunda olduğundan emin olun. Render, kodunuzu buradan çekecektir.
-   **Kodun Güncel Olması:** Canlıya almak istediğiniz en son ve çalışan kodun `main` (veya varsayılan) branch'inizde olduğundan emin olun.
-   **Backend Bağımlılıkları:** `backend/requirements.txt` dosyasını kontrol edin. Canlı ortam için şu paketlerin ekli olduğundan emin olun:
    -   `django`
    -   `gunicorn` (Render'da uygulamayı çalıştırmak için kullanılır)
    -   `psycopg2-binary` (PostgreSQL veritabanı ile bağlantı için)
    -   `dj-database-url` (Veritabanı URL'ini Django formatına çevirmek için)
-   **Frontend Bağımlılıkları:** `frontend/package.json` dosyanızın projenin ihtiyaç duyduğu tüm paketleri içerdiğinden emin olun.

---

## 2. Adım 1: Veritabanı Bağlantı Bilgilerini Hazırlama

Bu projede veritabanı olarak Render'ın kendi PostgreSQL hizmeti veya Supabase gibi harici bir sağlayıcı kullanılabilir. **Lütfen durumunuza uygun olan SADECE BİR seçeneği takip edin.**

### Seçenek A: Render PostgreSQL Kullanımı (Yeni Başlayanlar İçin Önerilir)

Eğer yeni bir veritabanı oluşturmak isterseniz, Render'ın kendi hizmetini kullanmak en kolay yoldur.

1.  Render Dashboard'una gidin. Sol üst köşedeki **New +** butonuna tıklayın ve açılan menüden **PostgreSQL**'i seçin.
2.  **Yapılandırma Ekranı:**
    -   **Name:** Veritabanınız için akılda kalıcı bir isim girin (örn: `sidrexgpt-db`).
    -   **Region:** `Frankfurt (EU Central)` seçin.
    -   **Instance Type:** `Free` (Ücretsiz planı seçin).
3.  **Create Database** butonuna tıklayın.
4.  **Bağlantı URL'ini Kopyalama:**
    -   Veritabanınızın yönetim paneli açıldığında, **Info** sekmesi altında **Connections** bölümünü bulun.
    -   `Internal Database URL`'i kopyalayın. Bu değeri bir sonraki adımda kullanacağız.

### Seçenek B: Mevcut Supabase Veritabanını Kullanma

Eğer projeniz zaten Supabase'e bağlıysa, bu adımları izleyin.

1.  **Supabase Proje Panelinize Gidin:** `supabase.com` adresinden projenize giriş yapın.
2.  **Veritabanı Ayarlarını Bulun:**
    -   Sol menüden dişli ikonu olan **Project Settings**'e tıklayın.
    -   Açılan menüden **Database**'i seçin.
3.  **Bağlantı Bilgilerini Kopyalayın:**
    -   **Connection string** başlığı altında, `URI` etiketli bir bağlantı adresi göreceksiniz. Bu, sizin veritabanı bağlantı adresinizdir.
    -   Genellikle şu formattadır: `postgres://postgres.[proje-referansınız]:[şifreniz]@aws-0-bolge.pooler.supabase.com:6543/postgres`.
    -   Bu **URI**'yi kopyalayın. Bu değeri bir sonraki adımda kullanacağız.

---

## 3. Adım 2: Django Backend'in Kurulumu

### 3.1: Web Servisi Oluşturma

1.  Render Dashboard'una geri dönün. **New +** > **Web Service**'e tıklayın.
2.  **Repository Seçimi:** Projenizin bulunduğu GitHub deposunu seçin ve **Connect** deyin.
3.  **Temel Ayarlar:**
    -   **Name:** Backend servisiniz için bir isim girin (örn: `sidrexgpt-backend`). Bu isim, servisinizin genel URL'sini oluşturacaktır (`sidrexgpt-backend.onrender.com` gibi).
    -   **Region:** `Frankfurt (EU Central)` (Eğer Render veritabanı kullanıyorsanız, veritabanı ile aynı bölgeyi seçin).
    -   **Branch:** `main` (veya kodunuzun bulunduğu ana branch).
    -   **Root Directory:** `backend`. Bu çok önemlidir! Render'a build ve çalıştırma komutlarını projenin `backend` klasörü içinde çalıştırmasını söyler.
    -   **Runtime:** `Python 3`.
4.  **Komut Ayarları:**
    -   **Build Command:** `pip install -r requirements.txt; python manage.py collectstatic --no-input; python manage.py migrate`
        -   Bu komut üç iş yapar: `pip` ile paketleri kurar, `collectstatic` ile statik dosyaları (CSS, JS, admin arayüzü) tek bir yere toplar ve `migrate` ile veritabanı tablolarınızı oluşturur.
    -   **Start Command:** `gunicorn core.wsgi:application`
        -   Bu, projenizi üretim (production) için uygun olan `Gunicorn` sunucusu ile başlatır.
    -   **Instance Type:** `Free`.

**Henüz "Create Web Service" butonuna TIKLAMAYIN!** Önce ortam değişkenlerini ayarlamalıyız.

### 3.2: Backend Ortam Değişkenleri (Çok Önemli)

Aynı sayfada aşağıya inerek **Advanced** bölümünü açın. **Add Environment Variable** butonuna tıklayarak aşağıdaki değişkenleri teker teker ekleyin. Bunlar projenizin hassas bilgilerini güvenli bir şekilde saklar.

-   **Key:** `DATABASE_URL`
    -   **Value:** **Adım 1**'de seçtiğiniz seçeneğe göre kopyaladığınız veritabanı bağlantı URL'ini (Render'ın `Internal Database URL`'i veya Supabase'den aldığınız `URI`) buraya yapıştırın.
-   **Key:** `SECRET_KEY`
    -   **Value:** Güçlü ve rastgele yeni bir anahtar oluşturun. **Kesinlikle projedeki anahtarı kullanmayın.** Yeni bir anahtar için [bu siteyi](https://djecrety.ir/) kullanabilirsiniz.
-   **Key:** `DEBUG`
    -   **Value:** `False`. Canlı ortamda bu her zaman `False` olmalıdır.
-   **Key:** `DJANGO_ALLOWED_HOSTS`
    -   **Value:** Şimdilik backend servisinizin adını girin: `sidrexgpt-backend.onrender.com`. Eğer özel bir domain bağlarsanız, onu da virgülle eklemeniz gerekir.
-   **Key:** `OPENAI_API_KEY`
    -   **Value:** Size ait olan OpenAI API anahtarını buraya girin.
-   **Key:** `CORS_ALLOWED_ORIGINS`
    -   **Value:** Frontend'inizin canlıya alındıktan sonra sahip olacağı URL'yi girin (örn: `https://sidrexgpt-frontend.onrender.com`). Bu, frontend'in backend'e istek atmasına izin verir.

Şimdi sayfanın en altındaki **Create Web Service** butonuna tıklayabilirsiniz.

---

## 4. Adım 3: Next.js Frontend'in Kurulumu

### 4.1: Statik Site Oluşturma

1.  Render Dashboard'una dönün. **New +** > **Static Site**'a tıklayın.
2.  Backend için bağladığınız aynı GitHub deposunu seçin.
3.  **Yapılandırma Ayarları:**
    -   **Name:** `sidrexgpt-frontend` (veya istediğiniz başka bir isim).
    -   **Branch:** `main`.
    -   **Root Directory:** `frontend`. Bu da çok önemlidir.
    -   **Build Command:** `pnpm install && pnpm build`. Projeniz `pnpm` kullandığı için bu komutları kullanıyoruz.
    -   **Publish Directory:** `.next`. Next.js, `build` komutundan sonra sitenin statik dosyalarını bu klasöre koyar. Render bu klasörü yayınlar.

### 4.2: Frontend Ortam Değişkeni

**Advanced** bölümünü açın ve **Add Environment Variable**'a tıklayın.

-   **Key:** `NEXT_PUBLIC_API_BASE_URL`
    -   **Value:** Backend servisinizin tam URL'si: `https://sidrexgpt-backend.onrender.com`.

**Create Static Site** butonuna tıklayın.

---

## 5. Adım 4: Canlıya Alma ve Sonrası Kontroller

### 5.1: Dağıtım Sürecini İzleme

-   **Backend:** Backend servisinizin yönetim panelinde, **Logs** sekmesine gidin. Burada build ve başlatma komutlarının çıktısını canlı olarak görebilirsiniz. `Deploy live` mesajını gördüğünüzde işlem başarılıdır.
-   **Frontend:** Frontend sitenizin yönetim panelinde, **Events** sekmesinden build sürecini takip edin.

### 5.2: Yönetici (Superuser) Hesabı Oluşturma

1.  Backend servisinizin panelinde **Shell** sekmesini açın.
2.  Açılan terminale şu komutu yazıp Enter'a basın: `python manage.py createsuperuser`
3.  Sizden istenen kullanıcı adı, e-posta ve şifre bilgilerini girerek yönetici hesabınızı oluşturun.

### 5.3: Fonksiyonel Testler

1.  **Siteyi Ziyaret Etme:** Frontend'inizin URL'sine (`https://sidrexgpt-frontend.onrender.com`) gidin.
2.  **Admin Paneli:** Sitenizin sonuna `/admin` ekleyerek (örn: `https://sidrexgpt-backend.onrender.com/admin`) Django admin paneline gidin ve az önce oluşturduğunuz bilgilerle giriş yapmayı deneyin.
3.  **Robotları Test Etme:** Sitedeki sohbet robotları ile konuşmayı deneyin.
4.  **Geliştirici Araçları:**
    -   Tarayıcınızda Geliştirici Araçları'nı (F12) açın.
    -   **Console** sekmesinde herhangi bir kırmızı hata olup olmadığını kontrol edin.
    -   **Network** sekmesinde, robotla konuştuğunuzda backend'inize giden istekleri (`sidrexgpt-backend.onrender.com`) ve bunların `200 OK` gibi başarılı durum kodları döndürdüğünü doğrulayın.

---

## 6. Ek Bilgiler ve Sorun Giderme

-   **Otomatik Dağıtım:** Artık `main` branch'inize her `git push` yaptığınızda, Render otomatik olarak hem backend'i hem de frontend'i yeniden dağıtacaktır.
-   **CORS Hataları:** Eğer frontend'de "CORS" ile ilgili bir hata alırsanız, backend'deki `CORS_ALLOWED_origins` ortam değişkenine frontend'inizin URL'sini doğru yazdığınızdan emin olun.
-   **Build Hataları:** Eğer build başarısız olursa, **Logs** sekmesindeki hata mesajlarını dikkatlice okuyun. Genellikle eksik bir paket veya yazım hatası gibi sorunları işaret ederler.
-   **502 Sunucu Hatası:** Eğer siteniz 502 hatası veriyorsa, backend servisinizin loglarını kontrol edin. Muhtemelen uygulama başlarken bir hata oluşmuştur.

Tebrikler! Projeniz artık Render.com üzerinde canlıda. 