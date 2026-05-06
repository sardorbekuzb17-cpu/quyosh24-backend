#!/usr/bin/env python
"""Admin parolini o'rnatish"""
import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'payme_backend.settings')
django.setup()

from django.contrib.auth import get_user_model

User = get_user_model()
admin = User.objects.get(username='admin')
admin.set_password('admin123')  # Parolni o'zgartiring!
admin.save()

print("✅ Admin paroli o'rnatildi: admin123")
print("⚠️  Production'da parolni o'zgartiring!")
