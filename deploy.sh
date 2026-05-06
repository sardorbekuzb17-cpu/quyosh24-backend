#!/bin/bash
# Django Backend Deployment Script for Alwaysdata

echo "🚀 Django Backend Deployment Starting..."

# 1. Virtual environment yaratish
echo "📦 Creating virtual environment..."
python3 -m venv venv
source venv/bin/activate

# 2. Dependencies o'rnatish
echo "📥 Installing dependencies..."
pip install --upgrade pip
pip install -r requirements.txt

# 3. Environment variables
echo "🔧 Setting up environment..."
cp .env.production .env

# 4. Database migratsiya
echo "🗄️ Running migrations..."
python manage.py migrate

# 5. Static files yig'ish
echo "📁 Collecting static files..."
python manage.py collectstatic --noinput

# 6. Superuser yaratish (agar kerak bo'lsa)
echo "👤 Create superuser (optional)..."
echo "Run: python manage.py createsuperuser"

# 7. Gunicorn bilan ishga tushirish
echo "🌐 Starting Gunicorn with PM2..."
pm2 start "venv/bin/gunicorn payme_backend.wsgi:application --bind 0.0.0.0:8081 --workers 2" --name django-backend

# 8. PM2 ni saqlash
pm2 save

echo "✅ Deployment completed!"
echo ""
echo "📝 Next steps:"
echo "1. Go to https://admin.alwaysdata.com"
echo "2. Add a Reverse Proxy site pointing to http://localhost:8081"
echo "3. Test the API: https://greenzone.alwaysdata.net/api/payme-custom/"
echo ""
echo "🔗 Webhook URL: https://greenzone.alwaysdata.net/api/payme-custom/"
