#!/usr/bin/env bash
# Build script for Render.com deployment

set -o errexit  # Exit on error

echo "🚀 Starting build process..."

# Python sürümünü kontrol et
python --version

# Gerekli paketleri yükle
echo "📦 Installing Python dependencies..."
pip install --upgrade pip
pip install -r requirements.txt

# Statik dosyaları topla
echo "📂 Collecting static files..."
python manage.py collectstatic --no-input

# Veritabanı migrasyonlarını detaylı şekilde çalıştır
echo "🔄 Running database migrations..."

# Temel Django migrations
echo "  - Running core Django migrations..."
python manage.py migrate contenttypes
python manage.py migrate auth
python manage.py migrate sessions
python manage.py migrate sites
python manage.py migrate admin

# Uygulama migrations
echo "  - Running application migrations..."
python manage.py migrate profiller
python manage.py migrate robots

# Tüm migrations'ları çalıştır (eksik olanlar için)
echo "  - Running remaining migrations..."
python manage.py migrate

# Sites framework'ü düzelt
echo "🌐 Setting up sites framework..."
python manage.py shell -c "
from django.contrib.sites.models import Site
try:
    site = Site.objects.get(pk=1)
    site.domain = 'sidrexgpt-backend.onrender.com'
    site.name = 'SidrexGPT Backend'
    site.save()
    print('Site updated successfully!')
except Site.DoesNotExist:
    site = Site.objects.create(pk=1, domain='sidrexgpt-backend.onrender.com', name='SidrexGPT Backend')
    print('Site created successfully!')
except Exception as e:
    print(f'Site setup error: {e}')
"

# Superuser oluştur (sadece yoksa)
echo "👤 Setting up superuser..."
python manage.py shell -c "
from django.contrib.auth.models import User
if not User.objects.filter(is_superuser=True).exists():
    try:
        User.objects.create_superuser(
            username='admin',
            email='admin@sidrexgpt.com',
            password='SidrexAdmin2025!'
        )
        print('Superuser created successfully!')
        print('Username: admin')
        print('Password: SidrexAdmin2025!')
    except Exception as e:
        print(f'Superuser creation error: {e}')
else:
    print('Superuser already exists.')
"

echo "✅ Build completed successfully!" 
echo "🎉 Backend ready at: https://sidrexgpt-backend.onrender.com"
echo "🔐 Admin panel: https://sidrexgpt-backend.onrender.com/admin/"
echo "📡 API root: https://sidrexgpt-backend.onrender.com/api/" 