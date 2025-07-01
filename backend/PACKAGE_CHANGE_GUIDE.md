# Sidrex Brand Package Change Guide

Bu doküman, Sidrex markası için paket türü değiştirme işlemlerini açıklar.

## ⚠️ Önemli Uyarı - Hata Çözümü

Eğer `UNIQUE constraint failed: robots_brand.name` hatası alıyorsanız, bu normali çünkü:

1. **API sadece mevcut Sidrex markasını düzenler** - Yeni marka oluşturmayı engeller
2. **POST /api/brands/** endpoint'i ile yeni marka oluşturmaya çalışmayın
3. **Sadece mevcut Sidrex markasının paket türünü değiştirin**

## Kurulum ve Kontrol

Sidrex markasının var olduğundan emin olmak için:

```bash
# Virtual environment'ı aktive edin
source venv/bin/activate  # Linux/Mac
# veya
venv\Scripts\activate  # Windows

# Sidrex markasını oluşturun veya kontrol edin
python manage.py setup_sidrex_brand
```

## Genel Bakış

Sidrex markası için şu paket türleri kullanılabilir:
- `normal`: Normal Paket (500 istek limiti)
- `pro`: Pro Paket (1000 istek limiti) 
- `premium`: Premium Paket (5000 istek limiti)

## API Endpoint

Base URL: `http://127.0.0.1:8000/api/brands/`

### ✅ Doğru Kullanım - Mevcut Durumu Görüntüleme

**GET** `/api/brands/`

Sidrex markasının mevcut durumunu görüntüler.

```bash
curl -X GET http://127.0.0.1:8000/api/brands/
```

Response örneği:
```json
[
  {
    "id": 4,
    "name": "Sidrex",
    "total_api_requests": 0,
    "request_limit": 500,
    "paket_turu": "normal",
    "paket_turu_display": "Normal Paket",
    "paket_baslangic_tarihi": "2024-01-01T00:00:00Z",
    "paket_bitis_tarihi": "2024-01-31T00:00:00Z",
    "remaining_requests": 500,
    "remaining_days": 15,
    "package_status": "✅ Aktif",
    "is_package_expired": false,
    "created_at": "2024-01-01T00:00:00Z",
    "updated_at": "2024-01-01T00:00:00Z"
  }
]
```

### ❌ Yanlış Kullanım - Yeni Marka Oluşturma

**Bu işlem ENGELLENDİ:**

```bash
# BU ÇALIŞMAZ ve hata verir!
curl -X POST http://127.0.0.1:8000/api/brands/ \
  -H "Content-Type: application/json" \
  -d '{"name": "Sidrex", "paket_turu": "pro"}'
```

**Hata mesajı:**
```json
{
  "error": "Yeni marka oluşturulamaz. Sadece mevcut Sidrex markası düzenlenebilir.",
  "detail": "Bu endpoint sadece mevcut Sidrex markasının paket türünü değiştirmek için kullanılabilir.",
  "available_actions": [
    "GET /api/brands/ - Mevcut durumu görüntüle",
    "PATCH /api/brands/{id}/ - Paket türünü değiştir",
    "POST /api/brands/{id}/change_package/ - Özel paket değiştirme action"
  ]
}
```

## ✅ Paket Türü Değiştirme Yöntemleri

### Yöntem 1: Özel Action ile (Önerilen)

**POST** `/api/brands/{id}/change_package/`

```bash
curl -X POST http://127.0.0.1:8000/api/brands/4/change_package/ \
  -H "Content-Type: application/json" \
  -d '{"paket_turu": "pro"}'
```

**Avantajları:**
- Paket değişikliği sırasında otomatik işlemler gerçekleşir
- API istek sayacı sıfırlanır
- Yeni paket süresi başlatılır
- Detaylı response döner

Response örneği:
```json
{
  "message": "Paket türü normal dan pro e değiştirildi",
  "brand_id": 4,
  "old_package": "normal",
  "new_package": "pro",
  "new_limit": 1000,
  "reset_requests": true,
  "new_end_date": "2024-02-01T00:00:00Z",
  "remaining_requests": 1000,
  "remaining_days": 30,
  "package_status": "✅ Aktif"
}
```

### Yöntem 2: PATCH ile

**PATCH** `/api/brands/{id}/`

```bash
curl -X PATCH http://127.0.0.1:8000/api/brands/4/ \
  -H "Content-Type: application/json" \
  -d '{"paket_turu": "premium"}'
```

### Yöntem 3: PUT ile

**PUT** `/api/brands/{id}/`

```bash
curl -X PUT http://127.0.0.1:8000/api/brands/4/ \
  -H "Content-Type: application/json" \
  -d '{
    "paket_turu": "premium"
  }'
```

## JavaScript/Frontend Örneği

```javascript
// ✅ Doğru: Mevcut durumu kontrol et
async function getCurrentPackage() {
  const response = await fetch('http://127.0.0.1:8000/api/brands/');
  const brands = await response.json();
  return brands[0]; // Sidrex brand
}

// ✅ Doğru: Paket türünü değiştir (Önerilen yöntem)
async function changePackage(brandId, newPackageType) {
  const response = await fetch(`http://127.0.0.1:8000/api/brands/${brandId}/change_package/`, {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
    },
    body: JSON.stringify({
      paket_turu: newPackageType
    })
  });
  
  if (response.ok) {
    const result = await response.json();
    console.log('Paket değiştirildi:', result);
    return result;
  } else {
    const error = await response.json();
    console.error('Hata:', error);
    throw new Error(error.error);
  }
}

// ❌ Yanlış: Yeni marka oluşturmaya çalışma
// Bu kod hata verecek!
async function createNewBrand() {
  try {
    const response = await fetch('http://127.0.0.1:8000/api/brands/', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ name: 'Sidrex', paket_turu: 'pro' })
    });
    // Bu hata verecek!
  } catch (error) {
    console.error('Bu işlem engellendi:', error);
  }
}

// ✅ Kullanım örneği
(async () => {
  try {
    const currentBrand = await getCurrentPackage();
    console.log('Mevcut paket:', currentBrand.paket_turu);
    
    // Pro pakete geç
    const result = await changePackage(currentBrand.id, 'pro');
    console.log('Yeni paket:', result.new_package);
  } catch (error) {
    console.error('İşlem başarısız:', error);
  }
})();
```

## Python Model Kullanımı

```python
from robots.models import Brand

# Sidrex markasını al
brand = Brand.get_or_create_sidrex()

# Mevcut durumu kontrol et
print(f"Mevcut paket: {brand.paket_turu}")
print(f"Limit: {brand.request_limit}")
print(f"Kalan istek: {brand.remaining_requests()}")

# Paket türünü değiştir
result = brand.change_package_type('premium')
print(f"Değişiklik sonucu: {result}")

# Yeni durumu kontrol et
brand.refresh_from_db()
print(f"Yeni paket: {brand.paket_turu}")
print(f"Yeni limit: {brand.request_limit}")
```

## Otomatik İşlemler

Paket türü değiştirildiğinde aşağıdaki işlemler otomatik olarak gerçekleşir:

1. **Request Limit Güncelleme**: Yeni paket türüne göre istek limiti ayarlanır
2. **Tarih Sıfırlama**: Paket başlangıç tarihi bugüne, bitiş tarihi 30 gün sonraya ayarlanır  
3. **Sayaç Sıfırlama**: Toplam API istek sayısı 0'a sıfırlanır
4. **Limit Kontrolü**: Yeni limit değerleri hesaplanır

## Error Handling

### Geçersiz Paket Türü

```json
{
  "error": "Geçersiz paket türü: invalid_package",
  "valid_choices": ["normal", "pro", "premium"]
}
```

### Eksik Parametre

```json
{
  "error": "paket_turu alanı gereklidir"
}
```

### Yeni Marka Oluşturma Engeli

```json
{
  "error": "Yeni marka oluşturulamaz. Sadece mevcut Sidrex markası düzenlenebilir.",
  "detail": "Bu endpoint sadece mevcut Sidrex markasının paket türünü değiştirmek için kullanılabilir.",
  "available_actions": [
    "GET /api/brands/ - Mevcut durumu görüntüle",
    "PATCH /api/brands/{id}/ - Paket türünü değiştir",
    "POST /api/brands/{id}/change_package/ - Özel paket değiştirme action"
  ]
}
```

## İzinler

- Bu işlemler sadece **admin kullanıcılar** tarafından gerçekleştirilebilir
- `IsAdminUser` permission class kullanılmaktadır

## Notlar

- **Yeni marka oluşturma engellendi** - Sadece mevcut Sidrex markası düzenlenebilir
- Paket değişikliği sırasında mevcut API istek sayısı sıfırlanır
- Paket süresi her değişiklikte yenilenir (30 gün)
- ViewSet sadece Sidrex markasını döndürecek şekilde filtrelenmiştir

## Sorun Giderme

**Eğer hala `UNIQUE constraint failed` hatası alıyorsanız:**

1. Virtual environment'ı aktive edin
2. `python manage.py setup_sidrex_brand` komutunu çalıştırın
3. Django sunucusunu yeniden başlatın
4. POST yerine PATCH veya custom action kullanın 