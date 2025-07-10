#!/usr/bin/env bash
# Simplified build script for Render.com with existing Supabase database

echo "🚀 Starting build process for Supabase-connected Django app..."

# Python sürümünü kontrol et
echo "🐍 Python version:"
python --version

# Gerekli paketleri yükle
echo "📦 Installing Python dependencies..."
pip install --upgrade pip
pip install -r requirements.txt

# Statik dosyaları topla
echo "📁 Collecting static files..."
python manage.py collectstatic --no-input

# Supabase bağlantısını test et
echo "🗄️ Testing Supabase database connection..."
python manage.py shell -c "
from django.db import connection
from django.contrib.sites.models import Site
from django.contrib.auth.models import User

try:
    # Bağlantı testi
    with connection.cursor() as cursor:
        cursor.execute('SELECT version();')
        version = cursor.fetchone()
        print(f'✅ PostgreSQL connected: {version[0][:50]}...')
    
    # Site konfigürasyonu
    site, created = Site.objects.get_or_create(
        pk=1,
        defaults={
            'domain': 'sidrexgpt-backend.onrender.com',
            'name': 'SidrexGPT Backend'
        }
    )
    if not created:
        site.domain = 'sidrexgpt-backend.onrender.com'
        site.name = 'SidrexGPT Backend'
        site.save()
    print(f'✅ Site configured: {site.domain}')
    
    # Superuser kontrolü
    if not User.objects.filter(is_superuser=True).exists():
        User.objects.create_superuser(
            username='admin',
            email='admin@sidrexgpt.com',
            password='SidrexAdmin2025!'
        )
        print('✅ Superuser created: admin/SidrexAdmin2025!')
    else:
        print('✅ Superuser already exists')
    
    # Mevcut veri kontrolü
    from robots.models import Robot, Brand
    robot_count = Robot.objects.count()
    brand_count = Brand.objects.count()
    print(f'📊 Current data: {robot_count} robots, {brand_count} brands')
    
except Exception as e:
    print(f'❌ Database error: {e}')
    exit(1)

print('✅ Supabase database ready - skipping migrations')
"

# System check
echo "🔍 Running Django system checks..."
python manage.py check --verbosity=1

echo "🎉 Build completed successfully!" 
echo "🌐 Backend will be ready at: https://sidrexgpt-backend.onrender.com"
echo "🔐 Admin panel: https://sidrexgpt-backend.onrender.com/admin/"
echo "📡 API endpoints: https://sidrexgpt-backend.onrender.com/api/"
echo "🤖 Note: Using existing Supabase database - no migrations applied"
