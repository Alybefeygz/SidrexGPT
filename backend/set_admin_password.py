#!/usr/bin/env python
import os
import sys
import django

# Django'yu setup et
sys.path.append(os.path.dirname(os.path.abspath(__file__)))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'core.settings')
django.setup()

from django.contrib.auth.models import User

try:
    admin_user = User.objects.get(username='admin')
    admin_user.set_password('admin123')  # Şifre: admin123
    admin_user.save()
    print("Admin password set to: admin123")
    print(f"Username: {admin_user.username}")
    print(f"is_staff: {admin_user.is_staff}")
    print(f"is_superuser: {admin_user.is_superuser}")
except User.DoesNotExist:
    print("Admin user not found") 