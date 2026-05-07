#!/usr/bin/env python
"""
Superuser yaratish scripti
"""
import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'payme_backend.settings')
django.setup()

from django.contrib.auth import get_user_model

User = get_user_model()

username = 'admin'
email = 'admin@quyosh24.uz'
password = 'admin123'

if not User.objects.filter(username=username).exists():
    User.objects.create_superuser(username=username, email=email, password=password)
    print(f'Superuser "{username}" yaratildi!')
else:
    print(f'Superuser "{username}" allaqachon mavjud.')
