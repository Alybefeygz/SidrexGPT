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
    print(f"Username: {admin_user.username}")
    print(f"is_staff: {admin_user.is_staff}")
    print(f"is_superuser: {admin_user.is_superuser}")
    print(f"is_active: {admin_user.is_active}")
    
    # Admin kullanıcısının is_staff'ını True yap eğer False ise
    if not admin_user.is_staff:
        admin_user.is_staff = True
        admin_user.save()
        print("is_staff set to True")
    
except User.DoesNotExist:
    print("Admin user not found")
    
# Ayrıca API'den dönen kullanıcı verisini test edelim
print("\n--- API Test ---")
from rest_framework.authtoken.models import Token

try:
    token = Token.objects.get(user__username='admin')
    print(f"Admin token: {token.key}")
except Token.DoesNotExist:
    print("Admin token not found, creating one...")
    token = Token.objects.create(user=admin_user)
    print(f"Created admin token: {token.key}")

def check_admin(username, email, password):
    """
    Belirtilen kullanıcı adıyla bir süper kullanıcı olup olmadığını kontrol eder,
    yoksa oluşturur.
    """
    if User.objects.filter(username=username).exists():
        print(f"'{username}' adlı süper kullanıcı zaten mevcut. Şifre güncelleniyor...")
        user = User.objects.get(username=username)
        user.set_password(password)
        user.save()
        print(f"'{username}' kullanıcısının şifresi başarıyla güncellendi.")
    else:
        print(f"'{username}' adlı süper kullanıcı bulunamadı. Yeni bir tane oluşturuluyor...")
        User.objects.create_superuser(username=username, email=email, password=password) 