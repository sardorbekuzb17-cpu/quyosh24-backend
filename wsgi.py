"""
WSGI config for ahost.uz hosting
"""
import os
import sys

# Django loyihasi yo'lini qo'shish
path = '/home/username/payme_backend'  # Bu yo'lni o'zgartiring
if path not in sys.path:
    sys.path.append(path)

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'payme_backend.settings')

from django.core.wsgi import get_wsgi_application
application = get_wsgi_application()
