#!/usr/bin/env bash
# Enhanced build script for Render.com deployment with database repair

set -o errexit  # Exit on error

echo " Starting enhanced build process..."

# Python sürümünü kontrol et
python --version

# Gerekli paketleri yükle
echo " Installing Python dependencies..."
pip install --upgrade pip
pip install -r requirements.txt

# Statik dosyaları topla
echo " Collecting static files..."
python manage.py collectstatic --no-input

# Veritabanı migrasyonlarını detaylı şekilde çalıştır
echo " Running database migrations..."

# Temel Django migrations
echo "  - Running core Django migrations..."
python manage.py migrate contenttypes --verbosity=2
python manage.py migrate auth --verbosity=2
python manage.py migrate sessions --verbosity=2

# Sites framework için özel kontrol
echo "  - Checking sites framework..."
python manage.py shell -c "
from django.db import connection
with connection.cursor() as cursor:
    try:
        cursor.execute('SELECT 1 FROM django_site LIMIT 1')
    except Exception as e:
        if 'relation \"django_site\" does not exist' in str(e):
            print('Sites table does not exist, forcing migration...')
            from django.core.management import call_command
            call_command('migrate', 'sites', '--fake-initial')
"

python manage.py migrate sites --verbosity=2
python manage.py migrate admin --verbosity=2

# Uygulama migrations
echo "  - Running application migrations..."
python manage.py migrate profiller --verbosity=2
python manage.py migrate robots --verbosity=2

# Tüm migrations'ları çalıştır (eksik olanlar için)
echo "  - Running remaining migrations..."
python manage.py migrate --verbosity=2

# Database repair ve debugging
echo " Database repair and debugging..."
python manage.py shell -c "
import sys
from django.db import connection
from django.contrib.sites.models import Site

# Database tabloları kontrol et
try:
    tables = connection.introspection.table_names()
    print(f' Database connected. Available tables: {len(tables)}')
    
    # Önemli tabloları kontrol et
    important_tables = ['django_site', 'robots_robot', 'robots_brand', 'auth_user']
    for table in important_tables:
        if table in tables:
            print(f' Table {table} exists')
        else:
            print(f' Table {table} missing')
            
except Exception as e:
    print(f' Database connection error: {e}')
    sys.exit(1)

# Sites framework kontrol et ve düzelt
try:
    if not Site.objects.filter(pk=1).exists():
        Site.objects.create(pk=1, domain='sidrexgpt-backend.onrender.com', name='SidrexGPT Backend')
        print(' Site object created')
    else:
        site = Site.objects.get(pk=1)
        site.domain = 'sidrexgpt-backend.onrender.com'
        site.name = 'SidrexGPT Backend'
        site.save()
        print(' Site object updated')
except Exception as e:
    print(f' Site setup error: {e}')

# Robot model kontrol et
try:
    from robots.models import Robot, Brand
    robot_count = Robot.objects.count()
    brand_count = Brand.objects.count()
    print(f' Robots: {robot_count}, Brands: {brand_count}')
except Exception as e:
    print(f' Robot models error: {e}')

print(' Database repair completed')
"

# Superuser oluştur (sadece yoksa)
echo " Setting up superuser..."
python manage.py shell -c "
from django.contrib.auth.models import User
import sys

try:
    if not User.objects.filter(is_superuser=True).exists():
        User.objects.create_superuser(
            username='admin',
            email='admin@sidrexgpt.com',
            password='SidrexAdmin2025!'
        )
        print(' Superuser created successfully!')
        print('  Username: admin')
        print('  Password: SidrexAdmin2025!')
    else:
        superuser_count = User.objects.filter(is_superuser=True).count()
        print(f' Superuser already exists. Total superusers: {superuser_count}')
except Exception as e:
    print(f' Superuser creation error: {e}')
"

# Final system check
echo " Running system checks..."
python manage.py check --verbosity=2

echo " Enhanced build completed successfully!" 
echo " Backend ready at: https://sidrexgpt-backend.onrender.com"
echo " Admin panel: https://sidrexgpt-backend.onrender.com/admin/"
echo " API root: https://sidrexgpt-backend.onrender.com/api/"
echo " Robots API: https://sidrexgpt-backend.onrender.com/api/robots/"
echo " Profiles API: https://sidrexgpt-backend.onrender.com/api/profile/profilleri/"
echo " Auth API: https://sidrexgpt-backend.onrender.com/api/rest-auth/"
