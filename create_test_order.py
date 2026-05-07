#!/usr/bin/env python
"""Test buyurtma yaratish scripti"""

import os
import django

# Django sozlamalarini yuklash
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'payme_backend.settings')
django.setup()

from payments.order_models import Order, OrderItem
from django.utils import timezone

# Buyurtma yaratish
order = Order.objects.create(
    order_id='QUYOSH24-TEST-001',
    customer_name='Test Mijoz',
    delivery_address='Toshkent, Chilonzor tumani, Test ko\'cha 123',
    total_amount=1500000,  # 1,500,000 so'm
    payment_method='payme',
    is_paid=False
)

# Mahsulotlar qo'shish
OrderItem.objects.create(
    order=order,
    product_id='PANEL-550W',
    product_name='Quyosh paneli 550W Longi',
    quantity=2,
    price=500000,
    total=1000000
)

OrderItem.objects.create(
    order=order,
    product_id='INV-5KW',
    product_name='Inverter 5kW Growatt',
    quantity=1,
    price=500000,
    total=500000
)

print("✅ Test buyurtma yaratildi!")
print(f"Order ID: {order.order_id}")
print(f"Mijoz: {order.customer_name}")
print(f"Jami summa: {order.total_amount:,} so'm")
print(f"\nAdmin panelda ko'ring: http://127.0.0.1:8000/admin/payments/order/")
