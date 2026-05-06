"""
Production settings for payme_backend project on Alwaysdata
"""

from .settings import *
import os

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = os.getenv('SECRET_KEY', SECRET_KEY)

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = os.getenv('DEBUG', 'False') == 'True'

# Allowed hosts
ALLOWED_HOSTS = os.getenv('ALLOWED_HOSTS', 'greenzone.alwaysdata.net,api.quyosh24.uz').split(',')

# Static files
STATIC_ROOT = os.getenv('STATIC_ROOT', '/home/greenzone/django-backend/static/')
STATIC_URL = '/static/'

# Payme Configuration - Environment variables
PAYME_ID = os.getenv('PAYME_ID', PAYME_ID)
PAYME_KEY = os.getenv('PAYME_KEY', PAYME_KEY)

# Security settings for production
SECURE_SSL_REDIRECT = True
SESSION_COOKIE_SECURE = True
CSRF_COOKIE_SECURE = True
SECURE_BROWSER_XSS_FILTER = True
SECURE_CONTENT_TYPE_NOSNIFF = True
X_FRAME_OPTIONS = 'DENY'

# CORS settings (agar kerak bo'lsa)
CORS_ALLOWED_ORIGINS = [
    'https://quyosh24.uz',
    'https://www.quyosh24.uz',
    'https://api.quyosh24.uz',
]
