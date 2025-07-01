#!/usr/bin/env bash
# Build script for Render.com deployment

set -o errexit  # Exit on error

echo "Starting build process..."

# Install dependencies
echo "Installing Python dependencies..."
pip install -r requirements.txt

echo "Collecting static files..."
python manage.py collectstatic --no-input

echo "Running database migrations..."
python manage.py migrate

echo "Build completed successfully!" 