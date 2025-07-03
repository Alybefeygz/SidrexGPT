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

# Veritabanı migrasyonlarını çalıştır
echo "🔄 Running database migrations..."
python manage.py migrate

echo "✅ Build completed successfully!" 