# 🔄 Google Drive JSON'dan Environment Variables'a Geçiş Rehberi

## 📋 Genel Bakış

Bu rehber, Google Drive Service Account authentication'ı JSON dosyasından environment variables'a geçirme sürecini anlatır.

## ✅ Uygulanan Değişiklikler

### 1. Backend Settings.py Güncellemesi

Google Service Account bilgileri artık environment variables'tan okunuyor:

```python
# Google Service Account Bilgileri - Environment Variables'tan al
GOOGLE_SERVICE_ACCOUNT_INFO = {
    'type': config('GOOGLE_SERVICE_ACCOUNT_TYPE', default='service_account'),
    'project_id': config('GOOGLE_PROJECT_ID', default=''),
    'private_key_id': config('GOOGLE_PRIVATE_KEY_ID', default=''),
    'private_key': config('GOOGLE_PRIVATE_KEY', default='').replace('\\n', '\n'),
    'client_email': config('GOOGLE_CLIENT_EMAIL', default=''),
    'client_id': config('GOOGLE_CLIENT_ID', default=''),
    'auth_uri': config('GOOGLE_AUTH_URI', default='https://accounts.google.com/o/oauth2/auth'),
    'token_uri': config('GOOGLE_TOKEN_URI', default='https://oauth2.googleapis.com/token'),
    'auth_provider_x509_cert_url': config('GOOGLE_AUTH_PROVIDER_X509_CERT_URL', default='https://www.googleapis.com/oauth2/v1/certs'),
    'client_x509_cert_url': config('GOOGLE_CLIENT_X509_CERT_URL', default=''),
    'universe_domain': config('GOOGLE_UNIVERSE_DOMAIN', default='googleapis.com')
}
```

### 2. Environment Variables Template

`env.example` dosyasına şu değişkenler eklendi:

```bash
# Google Drive Klasör ID'si
GOOGLE_DRIVE_FOLDER_ID=1HdOnnvWo6eccfsGJtwhYuN_jGbcWgHe4

# Google Service Account Bilgileri
GOOGLE_SERVICE_ACCOUNT_TYPE=service_account
GOOGLE_PROJECT_ID=sidrexgpts
GOOGLE_PRIVATE_KEY_ID=4f64e5e46ab0fdc3f057b990b53849396864fb17
GOOGLE_PRIVATE_KEY="-----BEGIN PRIVATE KEY-----\n...\n-----END PRIVATE KEY-----\n"
GOOGLE_CLIENT_EMAIL=sidrexgpt-s@sidrexgpts.iam.gserviceaccount.com
GOOGLE_CLIENT_ID=105524261671549265478
GOOGLE_AUTH_URI=https://accounts.google.com/o/oauth2/auth
GOOGLE_TOKEN_URI=https://oauth2.googleapis.com/token
GOOGLE_AUTH_PROVIDER_X509_CERT_URL=https://www.googleapis.com/oauth2/v1/certs
GOOGLE_CLIENT_X509_CERT_URL=https://www.googleapis.com/robot/v1/metadata/x509/sidrexgpt-s%40sidrexgpts.iam.gserviceaccount.com
GOOGLE_UNIVERSE_DOMAIN=googleapis.com
```

### 3. Code Changes

Aşağıdaki dosyalar güncellendi:
- `robots/services.py` - 3 function güncellendi
- `robots/utils.py` - authentication method güncellendi  
- `tests/management_commands/test_pdf_upload.py` - test dosyası güncellendi

## 🚀 Production Deployment

### Render.com Environment Variables

Render.com dashboard'unda şu environment variables'ları ayarlayın:

```bash
# Google Drive Configuration
GOOGLE_DRIVE_FOLDER_ID=1HdOnnvWo6eccfsGJtwhYuN_jGbcWgHe4
GOOGLE_SERVICE_ACCOUNT_TYPE=service_account
GOOGLE_PROJECT_ID=sidrexgpts
GOOGLE_PRIVATE_KEY_ID=4f64e5e46ab0fdc3f057b990b53849396864fb17
GOOGLE_CLIENT_EMAIL=sidrexgpt-s@sidrexgpts.iam.gserviceaccount.com
GOOGLE_CLIENT_ID=105524261671549265478
GOOGLE_AUTH_URI=https://accounts.google.com/o/oauth2/auth
GOOGLE_TOKEN_URI=https://oauth2.googleapis.com/token
GOOGLE_AUTH_PROVIDER_X509_CERT_URL=https://www.googleapis.com/oauth2/v1/certs
GOOGLE_CLIENT_X509_CERT_URL=https://www.googleapis.com/robot/v1/metadata/x509/sidrexgpt-s%40sidrexgpts.iam.gserviceaccount.com
GOOGLE_UNIVERSE_DOMAIN=googleapis.com
```

**ÖNEMLİ:** `GOOGLE_PRIVATE_KEY` için:
```bash
GOOGLE_PRIVATE_KEY="-----BEGIN PRIVATE KEY-----\nMIIEvgIBADANBgkqhkiG9w0BAQEFAASCBKgwggSkAgEAAoIBAQCuUvy7mIzYSt3s\nfgNTjS/s9WCOLmRK3pFy96HLG8LRtZSdJVc4nAfVgW2Uj7Rwkg9rJmtWMfw3DxZS\nZXeh9wZJ4NWVGM1rhAdh9iGV0EjAQlAGIyZHwUJ4BnSDWAvdeZoQx53YvpCjcWj0\n5ajV61RkVjVaE60DN74huELezTEbPSSgBXA+scsvaYtvgIqkaMgXAZN3UNw7jF4O\nMiVZ8wdP0ZwbRMMkHEnpbLnzB3//RwEl8Se5Vw3tC2p503wiWB8UqYVIZX4BT0d1\n/iRdUEeB14wrGLgwKCTUfMfjkaRq2XNKqNhTPkHU7qrLOSSNRJUt5V9mKDVa+pj\n1CgSrHIRAgMBAAECggEAMwaJgaO6fkkTwnh0Is2t3I9KbvO3WY7iRiOj0R7UHKwo\nzwKyEBjj1iPnXlfd+iFWsAdz3awN5lPdNcsLhHYY+iD8g4LaBgGEY7E2zXJFCTmf\n0NwTBWfVO+qvyg5IktBYP1cepeXJ0n2MujpK/CrA7gmp3i7qMonrdlVIBY1MNWtp\ngE3VGBHigANoiwM7Sniz4VTykOFU77adbYnT39ljTD3ghl3/bhXIDXmZGaI1JkdZ\n2o1YBEwnDkBaI0AQQR/X5KuvNc3URPJvoBHrmBBGD1pnJHLAlxWU4zpcIHg2HgyD\n/FuDie2jo3LnwdDmJPzMiDfqI8EPtQqRV1z17VnrnQKBgQDa6+g2kOXZQT1KLzV7\nAQcR32yZ2zlcOOTq+4et10EIbnaWlWQgF6otzrMyKUeSWX5fvG0gUKi0ovh3gYVu\n5Q2no0GmXIJ8/hc71i9nTqaO2u10fhy0NEtrRWJMbOJbFjk++UKXETyUxizML6+j\nKaC1iB1nSEseALByO0Lkes9/XwKBgQDL2WjOknB7riu2sjlIAxfa453Wa75iMlsL\n8IaMriTDDxZIqL3LoU7dCCO8nlIMGEBxBiG7/KZZry9NZugkNDOXvqcx8syLB/Xb\n8nqzbL1YkwhRPpfjmkr1NdFyRGH62jOMkqfEEc547MpGAOsuFhShDzcdW5LwkRht\nM/k4CDs0jwKBgQDZD5bKo5iCdOEkMPLB5x7vZav0URzqh67SHltEzmy4w23pmG4S\nM+SUTqH2Vl+UiA95NQauR8s+b2gUdeOrNIj5cjGhlY/8BqNavN97esxCUGeoXXJw\nanls/vqb9EnrLnnMKrEPwBNlH6lDOvTWvmuOEku1IET6loxcds24ZNxf2QKBgQCA\n7lqOxSpl36yAWktGk8ZDyNFs7Cq3Wxgg/hlr4z0XLnSusiORJs6FmH9Z7l0Aj1o6\n4mD10H+6m8X0U9EiDO5Q3OJNAj+C9B755WzcDTvZSO3qzQcuisk8PLTjbAL4sYgH\nMj7wET8hVss86ZnWRVr433HBnMjcZTko4MWRPguMWwKBgH4Ju+gXgH6ZU1u8JrfK\nCsrl0IzkUZod3trPUDqGrNSynglZaxRRJShPSRklhxTtVlQ8XbZtwe37GB6UTsZf\nx/S6Yk34DJtU7jpF8JjAr7OYv3B3/W1T3QuJN36ULGnR6qODk+CpaNCvipaj9tT8\njBMYjUiXoIMdfXacHAywHuZa\n-----END PRIVATE KEY-----\n"
```

### Local Development

Local development için `.env` dosyasını oluşturun ve yukarıdaki değerleri ekleyin.

## 🔧 Backward Compatibility

Sistem backward compatible'dır:
- Environment variables mevcutsa: Öncelikle bunları kullanır
- Environment variables yoksa: JSON dosyasından okur (fallback)

## ✅ Avantajlar

1. **Güvenlik**: JSON dosyasını repository'ye commit etme riski yok
2. **Deployment**: Environment variables hosting platformlarında kolay yönetim
3. **Esneklik**: Farklı ortamlar için farklı credentials kolay ayarlama
4. **Security Best Practices**: Sensitive data environment'ta saklanıyor

## 🚨 Önemli Notlar

1. `GOOGLE_PRIVATE_KEY` değerinde `\n` karakterleri korunmalıdır
2. Private key tırnak içinde olmalıdır
3. Production'da JSON dosyasını silmenizi öneririz
4. Environment variables ayarladıktan sonra test edin

## 🧪 Test Etme

```bash
# Test management command'ı
python manage.py test_pdf_upload 1

# Backend'te test
python tests/integration/test_chat_api.py
```

---

**Son Güncelleme:** 2025-01-27  
**Durum:** ✅ Production Ready  
**Backward Compatibility:** ✅ Destekleniyor 