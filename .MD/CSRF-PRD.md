# 🔐 CSRF Token Sorunları ve Çözümleri - Production Readiness Document (PRD)

## ✅ UYGULANAN ÇÖZÜMLER (2025-01-27)

### 🚀 Production Hazırlık Tamamlandı

Bu dokümandaki tüm kritik CSRF güvenlik önlemleri projeye uygulanmıştır:

**✅ Backend Güncellemeleri:**
- Environment-based CSRF configuration eklendi
- Production/Development ortam ayrımı yapıldı
- Gelişmiş CSRF view implementasyonu
- Enhanced CORS headers ve trusted origins

**✅ Frontend Güncellemeleri:**
- Proactive CSRF token management sistemi
- Auto-retry mechanism CSRF hatalarında
- Improved error handling ve user experience

**✅ Production Deployment İçin Kritik Environment Variables:**

**Render.com Backend Environment Variables:**
```bash
# Güvenlik
SECRET_KEY=[güçlü-rastgele-anahtar]
DEBUG=false
FORCE_HTTPS=true
CROSS_DOMAIN=true

# CSRF & Cookie Ayarları
CSRF_COOKIE_DOMAIN=.yourdomain.com
SESSION_COOKIE_DOMAIN=.yourdomain.com
ADDITIONAL_TRUSTED_ORIGINS=https://yourdomain.com,https://www.yourdomain.com,https://frontend-app.onrender.com

# Diğer ayarlar...
ALLOWED_HOSTS=backend-app.onrender.com,yourdomain.com
FRONTEND_URL=https://frontend-app.onrender.com
```

**Render.com Frontend Environment Variables:**
```bash
NEXT_PUBLIC_API_BASE_URL=https://backend-app.onrender.com/api
NEXT_PUBLIC_API_URL=https://backend-app.onrender.com
```

### 🔍 Production'a Alım Öncesi Kontrol Listesi

- [ ] Backend'te `DEBUG=false` ayarlandı
- [ ] `FORCE_HTTPS=true` ve `CROSS_DOMAIN=true` ayarlandı  
- [ ] CSRF_COOKIE_DOMAIN ve SESSION_COOKIE_DOMAIN değerleri gerçek domain'iniz
- [ ] ADDITIONAL_TRUSTED_ORIGINS tüm gerekli domain'leri içeriyor
- [ ] Frontend'te API URL'leri production backend'i gösteriyor
- [ ] SSL sertifikaları aktif
- [ ] Test senaryoları staging'de çalıştırıldı

---

## 📋 İçerik

1. [Mevcut Durum Analizi](#mevcut-durum-analizi)
2. [Kritik Sorunlar](#kritik-sorunlar)
3. [Çözüm Adımları](#çözüm-adımları)
4. [Test Senaryoları](#test-senaryoları)
5. [Deployment Checklist](#deployment-checklist)
6. [Acil Durum Çözümleri](#acil-durum-çözümleri)

---

## 🔍 Mevcut Durum Analizi

### Django Backend CSRF Konfigürasyonu
```python
# ✅ Doğru Konfigürasyonlar:
- CSRF middleware aktif
- CSRF_COOKIE_HTTPONLY = False (JS erişimi için)
- CSRF_USE_SESSIONS = False
- ensure_csrf_cookie endpoint mevcut

# ⚠️ Risk Alanları:
- SameSite=None production'da HTTPS gerektiriyor
- Cookie domain'i tanımlanmamış
- Trusted origins environment'a bağlı değil
```

### Frontend CSRF Implementasyonu
```typescript
// ✅ Doğru Implementasyonlar:
- CSRF token cookie'den okunuyor
- X-CSRFToken header'ı gönderiliyor
- withCredentials: true aktif

// ⚠️ Risk Alanları:
- Token alınamadığında warning verip devam ediyor
- Proactive CSRF token alma yok
```

---

## 🚨 Kritik Sorunlar

### 1. **Production SameSite=None + HTTP Sorunu**
**Risk Seviyesi:** 🔴 YÜKSEK
**Açıklama:** Production'da `SameSite=None` ayarı HTTPS gerektiriyor. HTTP'te cookie reddedilir.

### 2. **Domain Mismatch Sorunu**
**Risk Seviyesi:** 🔴 YÜKSEK
**Açıklama:** Frontend ve Backend farklı domain/subdomain'lerdeyse CSRF başarısız olur.

### 3. **Cookie Domain Tanımlanmamış**
**Risk Seviyesi:** 🟡 ORTA
**Açıklama:** Subdomain'ler arası cookie paylaşımı olmaz.

### 4. **Environment-Specific Configuration Eksik**
**Risk Seviyesi:** 🟡 ORTA
**Açıklama:** Farklı ortamlar için ayrı CSRF ayarları yok.

---

## ✅ Çözüm Adımları

### GÖREV 1: Backend Settings.py Güncellemesi

#### 1.1 CSRF Cookie Domain Ayarları
```python
# AI-powered-chatbox/backend/core/settings.py dosyasında güncelleyin:

# CSRF Cookie Domain Ayarları (settings.py'nin sonuna ekleyin)
# ==============================================================================
# ENHANCED CSRF CONFIGURATION FOR PRODUCTION
# ==============================================================================

# Domain ayarları - Environment'tan al
CSRF_COOKIE_DOMAIN = config('CSRF_COOKIE_DOMAIN', default=None)
SESSION_COOKIE_DOMAIN = config('SESSION_COOKIE_DOMAIN', default=None)

# HTTPS kontrolü
FORCE_HTTPS = config('FORCE_HTTPS', default=not DEBUG, cast=bool)
CSRF_COOKIE_SECURE = FORCE_HTTPS
SESSION_COOKIE_SECURE = FORCE_HTTPS

# SameSite ayarları - Environment'a göre
CROSS_DOMAIN = config('CROSS_DOMAIN', default=False, cast=bool)

if DEBUG:
    # Development: Esnek ayarlar
    CSRF_COOKIE_SAMESITE = 'Lax'
    SESSION_COOKIE_SAMESITE = 'Lax'
    CSRF_COOKIE_SECURE = False
    SESSION_COOKIE_SECURE = False
elif CROSS_DOMAIN:
    # Production + Cross Domain: Strict güvenlik
    CSRF_COOKIE_SAMESITE = 'None'
    SESSION_COOKIE_SAMESITE = 'None'
    # None kullanıyorsak HTTPS zorunlu
    CSRF_COOKIE_SECURE = True
    SESSION_COOKIE_SECURE = True
else:
    # Production + Same Domain: Maximum güvenlik
    CSRF_COOKIE_SAMESITE = 'Strict'
    SESSION_COOKIE_SAMESITE = 'Strict'

# Trusted Origins - Environment'tan ekle
ADDITIONAL_TRUSTED_ORIGINS = config('ADDITIONAL_TRUSTED_ORIGINS', default='', cast=lambda v: [x.strip() for x in v.split(',') if x.strip()])
CSRF_TRUSTED_ORIGINS = CORS_ALLOWED_ORIGINS + ADDITIONAL_TRUSTED_ORIGINS

# Debug bilgisi
if DEBUG:
    print(f"🔐 CSRF Configuration:")
    print(f"   - CSRF_COOKIE_SECURE: {CSRF_COOKIE_SECURE}")
    print(f"   - CSRF_COOKIE_SAMESITE: {CSRF_COOKIE_SAMESITE}")
    print(f"   - CSRF_COOKIE_DOMAIN: {CSRF_COOKIE_DOMAIN}")
    print(f"   - CSRF_TRUSTED_ORIGINS: {CSRF_TRUSTED_ORIGINS}")
```

#### 1.2 CORS Header'larını Güncelle
```python
# Mevcut CORS_ALLOW_HEADERS'ı bulun ve güncelleyin:
CORS_ALLOW_HEADERS = [
    'accept',
    'accept-encoding',
    'authorization',
    'content-type',
    'dnt',
    'origin',
    'user-agent',
    'x-csrftoken',
    'x-requested-with',
    'cache-control',  # Yeni eklenen
    'pragma',         # Yeni eklenen
]

# CORS_EXPOSE_HEADERS'ı güncelle
CORS_EXPOSE_HEADERS = [
    'content-type', 
    'x-csrftoken',
    'set-cookie',     # Yeni eklenen
]
```

### GÖREV 2: Environment Variables Yapılandırması

#### 2.1 .env Dosyası Güncellemesi
```bash
# AI-powered-chatbox/backend/.env dosyasına ekleyin:

# CSRF Configuration
CSRF_COOKIE_DOMAIN=
SESSION_COOKIE_DOMAIN=
FORCE_HTTPS=false
CROSS_DOMAIN=true
ADDITIONAL_TRUSTED_ORIGINS=

# Production'da bu değerleri güncelleyin:
# CSRF_COOKIE_DOMAIN=.yourdomain.com
# SESSION_COOKIE_DOMAIN=.yourdomain.com
# FORCE_HTTPS=true
# CROSS_DOMAIN=true
# ADDITIONAL_TRUSTED_ORIGINS=https://yourdomain.com,https://www.yourdomain.com
```

#### 2.2 Production Environment Variables
```bash
# Render.com veya hosting platformunuzda ayarlayın:
CSRF_COOKIE_DOMAIN=.sidrexgpt.com
SESSION_COOKIE_DOMAIN=.sidrexgpt.com
FORCE_HTTPS=true
CROSS_DOMAIN=true
ADDITIONAL_TRUSTED_ORIGINS=https://sidrexgpt.com,https://www.sidrexgpt.com,https://sidrexgpt-frontend.onrender.com
```

### GÖREV 3: Frontend API Client Güncellemesi

#### 3.1 CSRF Token Management Sistemi
```typescript
// AI-powered-chatbox/frontend/lib/api.ts dosyasını güncelleyin:

// CSRF token yönetimi için yeni fonksiyonlar ekleyin:

// CSRF token varlığını kontrol et
function hasValidCSRFToken(): boolean {
  const token = getCookie('csrftoken');
  return token !== null && token.length > 0;
}

// CSRF token alma - zorunlu
export const ensureCSRFToken = async (): Promise<void> => {
  if (hasValidCSRFToken()) {
    console.log('✅ CSRF token mevcut');
    return;
  }

  try {
    console.log('🔄 CSRF token alınıyor...');
    await apiClient.get('/csrf/');
    
    // Token alındı mı kontrol et
    if (!hasValidCSRFToken()) {
      throw new Error('CSRF token alınamadı');
    }
    
    console.log('✅ CSRF token başarıyla alındı');
  } catch (error) {
    console.error('❌ CSRF token alınırken hata:', error);
    throw new Error('CSRF token alınamadı. Lütfen sayfayı yenileyin.');
  }
};

// Auto-retry with CSRF token
async function apiCallWithCSRF<T>(apiCall: () => Promise<T>, retryOnce = true): Promise<T> {
  try {
    return await apiCall();
  } catch (error: any) {
    // CSRF hatası ve retry hakkımız varsa
    if (retryOnce && error.response?.status === 403 && 
        error.response?.data?.detail?.includes('CSRF')) {
      
      console.log('🔄 CSRF hatası tespit edildi, token yenileniyor...');
      await ensureCSRFToken();
      return await apiCall(); // Tekrar dene
    }
    throw error;
  }
}
```

#### 3.2 Request Interceptor Güncellemesi
```typescript
// Mevcut request interceptor'ı güncelleyin:
apiClient.interceptors.request.use(
  async (config) => {
    // CSRF token kontrolü ve ekleme
    if (typeof window !== 'undefined' && config.method && 
        !['GET', 'HEAD', 'OPTIONS'].includes(config.method.toUpperCase())) {
      
      const csrfToken = getCookie('csrftoken');
      if (csrfToken && config.headers) {
        config.headers['X-CSRFToken'] = csrfToken;
      } else {
        // Token yoksa hata fırlat
        console.error('❌ CSRF token bulunamadı');
        throw new Error('CSRF token bulunamadı. Sayfayı yenileyin.');
      }
    }

    // Content-Type ayarları
    if (config.headers && !config.headers['Content-Type']) {
      if (config.data instanceof FormData) {
        delete config.headers['Content-Type'];
      } else {
        config.headers['Content-Type'] = 'application/json';
      }
    }

    // Header'lar
    if (config.headers) {
      config.headers['Accept'] = 'application/json';
      config.headers['X-Requested-With'] = 'XMLHttpRequest';
    }
    
    config.withCredentials = true;
    return config;
  },
  (error) => Promise.reject(error)
);
```

#### 3.3 Güvenli API Çağrıları
```typescript
// API fonksiyonlarını güvenli hale getirin:
export const api = {
  auth: {
    getCSRFToken: () => ensureCSRFToken(),
    
    login: async (credentials: { username: string; password: string }) => {
      return apiCallWithCSRF(async () => {
        const formData = new FormData();
        formData.append('username', credentials.username);
        formData.append('password', credentials.password);
        return await apiClient.post('/rest-auth/login/', formData, {
          headers: { 'Content-Type': 'multipart/form-data' }
        });
      });
    },
    
    logout: () => apiCallWithCSRF(() => apiClient.post('/rest-auth/logout/')),
  },

  // Diğer API çağrılarını da aynı şekilde sarın...
};
```

### GÖREV 4: Authentication Context Güncellemesi

#### 4.1 Login Flow'u Güncelle
```typescript
// AI-powered-chatbox/frontend/contexts/AuthContext.tsx'yi güncelleyin:

const login = async (username: string, password: string) => {
  try {
    // Önce CSRF token al
    await api.auth.getCSRFToken();
    
    // Sonra login yap
    const response = await api.auth.login({ username, password });
    
    if (response.data.key) {
      localStorage.setItem('authToken', response.data.key);
      setIsAuthenticated(true);
      setUser(response.data.user);
      router.push('/');
    }
  } catch (error: any) {
    if (error.message.includes('CSRF')) {
      setError('Güvenlik token hatası. Lütfen sayfayı yenileyin.');
    } else {
      setError('Giriş başarısız. Kullanıcı adı veya şifre hatalı.');
    }
    throw error;
  }
};
```

### GÖREV 5: Error Handling ve User Experience

#### 5.1 CSRF Error Component
```typescript
// AI-powered-chatbox/frontend/components/CSRFErrorHandler.tsx oluşturun:

import React from 'react';
import { Alert, AlertDescription } from '@/components/ui/alert';
import { Button } from '@/components/ui/button';

interface CSRFErrorHandlerProps {
  error: Error | null;
  onRetry?: () => void;
}

export const CSRFErrorHandler: React.FC<CSRFErrorHandlerProps> = ({ error, onRetry }) => {
  if (!error || !error.message.includes('CSRF')) return null;

  return (
    <Alert variant="destructive" className="mb-4">
      <AlertDescription>
        Güvenlik token hatası oluştu. Bu durum genellikle uzun süre aktif olmadığında ortaya çıkar.
        <div className="mt-2 space-x-2">
          {onRetry && (
            <Button variant="outline" size="sm" onClick={onRetry}>
              Tekrar Dene
            </Button>
          )}
          <Button variant="outline" size="sm" onClick={() => window.location.reload()}>
            Sayfayı Yenile
          </Button>
        </div>
      </AlertDescription>
    </Alert>
  );
};
```

### GÖREV 6: Backend CSRF View Geliştirmesi

#### 6.1 Gelişmiş CSRF Endpoint
```python
# AI-powered-chatbox/backend/core/views.py'yi güncelleyin:

from django.http import JsonResponse
from django.views.decorators.csrf import ensure_csrf_cookie
from django.views.decorators.http import require_http_methods
from django.views.decorators.cache import never_cache
import logging

logger = logging.getLogger(__name__)

@never_cache
@ensure_csrf_cookie
@require_http_methods(["GET"])
def get_csrf_token(request):
    """
    CSRF token'ı client'a gönderir ve cookie'yi set eder.
    Cache'lenmez ve sadece GET metoduna izin verir.
    """
    try:
        # CSRF token'ı response'a ekle
        response = JsonResponse({
            'detail': 'CSRF cookie set successfully',
            'csrf_token': request.META.get('CSRF_COOKIE'),
            'secure': request.is_secure(),
            'domain': request.get_host()
        })
        
        # Debug bilgisi
        logger.info(f"CSRF token requested from {request.get_host()}")
        
        return response
    except Exception as e:
        logger.error(f"CSRF token error: {e}")
        return JsonResponse({
            'error': 'CSRF token could not be set'
        }, status=500)
```

---

## 🧪 Test Senaryoları

### TEST 1: Local Development Test
```bash
# Terminal 1: Backend
cd AI-powered-chatbox/backend
python manage.py runserver

# Terminal 2: Frontend  
cd AI-powered-chatbox/frontend
npm run dev

# Test adımları:
1. http://localhost:3000 açın
2. Browser DevTools > Network açın
3. Login deneyin
4. CSRF token gönderildiğini kontrol edin
```

### TEST 2: CSRF Token Alma Testi
```javascript
// Browser Console'da çalıştırın:
fetch('http://localhost:8000/api/csrf/', {
  method: 'GET',
  credentials: 'include'
})
.then(response => response.json())
.then(data => console.log('CSRF Response:', data));

// Cookie'yi kontrol edin:
console.log('CSRF Cookie:', document.cookie);
```

### TEST 3: Cross-Domain Test
```bash
# Production benzeri test için:
# Backend: https://backend-domain.com
# Frontend: https://frontend-domain.com
# Bu senaryoyu staging ortamında test edin
```

### TEST 4: HTTPS Test
```bash
# ngrok veya benzer tool ile HTTPS test:
ngrok http 3000  # Frontend için
ngrok http 8000  # Backend için
```

---

## 📋 Deployment Checklist

### Pre-Deployment Kontrolü

#### ✅ Backend Kontrolleri
- [ ] `CSRF_COOKIE_SECURE = True` (HTTPS için)
- [ ] `CSRF_COOKIE_SAMESITE` doğru ayarlanmış
- [ ] `CSRF_TRUSTED_ORIGINS` production domain'lerini içeriyor
- [ ] `CORS_ALLOWED_ORIGINS` güncel
- [ ] Environment variables ayarlanmış

#### ✅ Frontend Kontrolleri  
- [ ] CSRF token alım mekanizması aktif
- [ ] Error handling implementasyonu mevcut
- [ ] withCredentials: true ayarlanmış
- [ ] API base URL production'a uygun

#### ✅ Infrastructure Kontrolleri
- [ ] SSL sertifikaları geçerli
- [ ] Domain/subdomain yapılandırması doğru
- [ ] Load balancer CSRF cookie'lerini koruyor
- [ ] CDN CSRF header'larını geçiriyor

### Post-Deployment Kontrolü

#### ✅ Functional Tests
- [ ] Login/logout çalışıyor
- [ ] API çağrıları başarılı
- [ ] File upload çalışıyor
- [ ] Chat fonksiyonu aktif

#### ✅ Security Tests
- [ ] CSRF protection aktif
- [ ] Cookie secure flags ayarlanmış
- [ ] Cross-domain istekler kontrol altında
- [ ] XSS protection aktif

---

## 🚨 Acil Durum Çözümleri

### Acil Çözüm 1: CSRF Bypass (Sadece Geçici)
```python
# SADECE ACİL DURUMLARDA - GÜVENLİK RİSKİ!
# settings.py'de:

if os.getenv('EMERGENCY_CSRF_DISABLE'):
    MIDDLEWARE = [m for m in MIDDLEWARE if 'CsrfViewMiddleware' not in m]
    print("⚠️ WARNING: CSRF protection disabled for emergency!")
```

### Acil Çözüm 2: Flexible Cookie Settings
```python
# Geçici olarak daha esnek ayarlar:
if os.getenv('EMERGENCY_FLEXIBLE_COOKIES'):
    CSRF_COOKIE_SECURE = False
    SESSION_COOKIE_SECURE = False
    CSRF_COOKIE_SAMESITE = 'Lax'
    SESSION_COOKIE_SAMESITE = 'Lax'
    print("⚠️ WARNING: Cookie security relaxed for emergency!")
```

### Acil Çözüm 3: API Token Fallback
```python
# CSRF yerine API token kullanımı:
REST_FRAMEWORK['DEFAULT_AUTHENTICATION_CLASSES'] = [
    'knox.auth.TokenAuthentication',  # CSRF gerektirmez
    'rest_framework.authentication.SessionAuthentication',
]
```

---

## 📞 Troubleshooting

### Sık Görülen Hatalar

#### 1. "CSRF token missing or incorrect"
**Çözüm:**
- Frontend'te CSRF token alma fonksiyonunu çağırın
- Cookie domain ayarlarını kontrol edin
- Browser cache'ini temizleyin

#### 2. "Forbidden (CSRF cookie not set)"
**Çözüm:**
- `/api/csrf/` endpoint'ini çağırın
- `withCredentials: true` ayarlanmış mı kontrol edin
- SameSite ayarlarını gözden geçirin

#### 3. "CSRF verification failed"
**Çözüm:**
- CSRF_TRUSTED_ORIGINS listesini kontrol edin
- Origin header'ının doğru gönderildiğini kontrol edin
- Proxy/load balancer ayarlarını kontrol edin

---

## 📈 Monitoring ve Alerting

### Log Monitoring
```python
# settings.py'de CSRF logları:
LOGGING['loggers']['django.security'] = {
    'handlers': ['console'],
    'level': 'WARNING',
    'propagate': True,
}
```

### Metrics
- CSRF token başarısızlık oranı
- 403 error sayısı
- Cross-domain request başarı oranı

---

## 📝 Notlar

- **Bu doküman üretim ortamına alım öncesi mutlaka uygulanmalıdır**
- **Güvenlik ayarları hiçbir zaman production'da gevşetilmemelidir**
- **Test senaryoları staging ortamında çalıştırılmalıdır**
- **Emergency çözümler sadece kritik durumlarda kullanılmalıdır**

---

**Son Güncelleme:** 2025-01-27
**Versiyon:** 1.0
**Yazan:** AI Assistant
**Review:** Production'a alım öncesi teknik ekip tarafından gözden geçirilmelidir 