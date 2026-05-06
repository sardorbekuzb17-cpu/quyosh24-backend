# Django Backend - Alwaysdata Deployment Guide

## 📋 Tayyorgarlik

### 1. Fayllarni Zip qilish

Local kompyuterda:

```bash
cd C:\Jaha\solar_panel_app
tar -czf payme_backend.tar.gz payme_backend/
```

Yoki Windows PowerShell:

```powershell
Compress-Archive -Path payme_backend -DestinationPath payme_backend.zip
```

### 2. FTP/SFTP orqali yuklash

**FileZilla yoki WinSCP:**

- **Host:** `ssh-greenzone.alwaysdata.net`
- **Port:** `22` (SFTP)
- **Username:** `greenzone`
- **Password:** Sizning parolingiz

**Yuklash manzili:** `/home/greenzone/django-backend/`

## 🚀 Serverda Deploy Qilish

### 1. SSH orqali ulanish

```bash
ssh greenzone@ssh-greenzone.alwaysdata.net
```

### 2. Fayllarni ochish

```bash
cd ~/django-backend
unzip payme_backend.zip
# yoki
tar -xzf payme_backend.tar.gz

cd payme_backend
```

### 3. Deploy skriptini ishga tushirish

```bash
chmod +x deploy.sh
./deploy.sh
```

### 4. Superuser yaratish

```bash
source venv/bin/activate
python manage.py createsuperuser
```

**Ma'lumotlar:**
- Username: `admin`
- Email: `admin@quyosh24.uz`
- Password: `admin123` (yoki xavfsizroq parol)

## 🌐 Alwaysdata Admin Panel Sozlamalari

### 1. Admin panelga kirish

URL: https://admin.alwaysdata.com
Login: `greenzone`

### 2. Site qo'shish

**Web → Sites → Add a site**

**Sozlamalar:**

- **Name:** `django-backend`
- **Type:** **Reverse proxy**
- **Addresses:**
  - Domain: `greenzone.alwaysdata.net`
  - Path: `/api/payme-custom`
- **Remote URL:** `http://localhost:8081/api/payme-custom/`
- **Force HTTPS:** ✅ Yoqing

**Save** bosing.

### 3. Custom Domain (Agar kerak bo'lsa)

**Domains → Add a domain:**

- Domain: `api.quyosh24.uz`

**DNS sozlamalari (Cloudflare/domen providerda):**

```
Type: CNAME
Name: api
Value: greenzone.alwaysdata.net
TTL: Auto
```

## 🧪 Test Qilish

### 1. Browser da test

```
https://greenzone.alwaysdata.net/api/payme-custom/
```

Javob:

```json
{
  "status": "ok",
  "message": "Payme Custom API is running"
}
```

### 2. Admin panel

```
https://greenzone.alwaysdata.net/admin/
```

Login: `admin` / `admin123`

### 3. Payme Sandbox Test

1. https://test.paycom.uz ga kiring
2. Merchant ID: `69d6d6113663bd982443630d`
3. Secret Key: `4EkYNKATgBk2tyBENNfCaAn&QPVRSGjP2FAj`
4. Webhook URL: `https://greenzone.alwaysdata.net/api/payme-custom/`
5. Testlarni boshlang

## 🔧 Foydali Buyruqlar

### PM2 boshqaruvi

```bash
# Status
pm2 status

# Loglar
pm2 logs django-backend

# Qayta ishga tushirish
pm2 restart django-backend

# To'xtatish
pm2 stop django-backend

# O'chirish
pm2 delete django-backend
```

### Django buyruqlari

```bash
# Virtual environment aktivlashtirish
source ~/django-backend/payme_backend/venv/bin/activate

# Migratsiya
python manage.py migrate

# Static files
python manage.py collectstatic --noinput

# Superuser yaratish
python manage.py createsuperuser

# Shell
python manage.py shell
```

### Fayllarni yangilash

Local kompyuterdan:

```bash
# Faylni yuklash
scp -r payme_backend greenzone@ssh-greenzone.alwaysdata.net:~/django-backend/

# Serverda qayta ishga tushirish
ssh greenzone@ssh-greenzone.alwaysdata.net "pm2 restart django-backend"
```

## 📊 Database Boshqaruvi

### SQLite (default)

```bash
cd ~/django-backend/payme_backend
sqlite3 db.sqlite3

# SQL buyruqlar
.tables
SELECT * FROM orders;
.quit
```

### PostgreSQL ga o'tish (optional)

1. Alwaysdata admin panelda PostgreSQL database yarating
2. `.env` faylini yangilang:

```env
DATABASE_URL=postgresql://user:password@postgresql-greenzone.alwaysdata.net/dbname
```

3. `settings.py` da:

```python
import dj_database_url
DATABASES = {
    'default': dj_database_url.config(default=os.getenv('DATABASE_URL'))
}
```

4. `requirements.txt` ga qo'shing:

```
dj-database-url==2.1.0
```

## 🔐 Xavfsizlik

### Production uchun:

1. **SECRET_KEY ni o'zgartiring:**

```bash
python -c "from django.core.management.utils import get_random_secret_key; print(get_random_secret_key())"
```

2. **DEBUG = False** qiling

3. **ALLOWED_HOSTS** ni to'g'ri sozlang:

```python
ALLOWED_HOSTS = ['greenzone.alwaysdata.net', 'api.quyosh24.uz']
```

4. **Payme Production credentials** ga o'ting

## 📝 Environment Variables

`.env` fayli:

```env
SECRET_KEY=your-new-secret-key-here
DEBUG=False
ALLOWED_HOSTS=greenzone.alwaysdata.net,api.quyosh24.uz

# Payme Production
PAYME_ID=your_production_merchant_id
PAYME_KEY=your_production_secret_key
```

## ⚠️ Muammolarni Hal Qilish

### API ishlamayapti

```bash
# Loglarni tekshiring
pm2 logs django-backend

# Port band emasligini tekshiring
netstat -tulpn | grep 8081

# Gunicorn qayta ishga tushiring
pm2 restart django-backend
```

### Database xatolari

```bash
# Migratsiyalarni qayta ishga tushiring
source venv/bin/activate
python manage.py migrate --run-syncdb
```

### Static files ko'rinmayapti

```bash
python manage.py collectstatic --noinput --clear
```

## ✅ Deployment Checklist

- [ ] Fayllar serverga yuklandi
- [ ] Virtual environment yaratildi
- [ ] Dependencies o'rnatildi
- [ ] Database migratsiya bajarildi
- [ ] Superuser yaratildi
- [ ] Static files yig'ildi
- [ ] Gunicorn PM2 bilan ishga tushdi
- [ ] Alwaysdata admin panelda site sozlandi
- [ ] HTTPS yoqildi
- [ ] Admin panel ochiladi
- [ ] Payme sandbox testlari o'tdi
- [ ] Production credentials sozlandi

## 🎉 Tayyor!

Django backend muvaffaqiyatli deploy qilindi!

**Webhook URL:** `https://greenzone.alwaysdata.net/api/payme-custom/`

**Admin Panel:** `https://greenzone.alwaysdata.net/admin/`
