from django.db import models
from django.utils import timezone


class Order(models.Model):
    """Buyurtmalar modeli"""
    
    # Buyurtma holatlari
    STATUS_PENDING = 'pending'  # Kutilmoqda
    STATUS_PAID = 'paid'  # To'langan
    STATUS_PROCESSING = 'processing'  # Jarayonda
    STATUS_SHIPPED = 'shipped'  # Yuborilgan
    STATUS_DELIVERED = 'delivered'  # Yetkazilgan
    STATUS_CANCELLED = 'cancelled'  # Bekor qilingan
    
    STATUS_CHOICES = [
        (STATUS_PENDING, 'Kutilmoqda'),
        (STATUS_PAID, 'To\'langan'),
        (STATUS_PROCESSING, 'Jarayonda'),
        (STATUS_SHIPPED, 'Yuborilgan'),
        (STATUS_DELIVERED, 'Yetkazilgan'),
        (STATUS_CANCELLED, 'Bekor qilingan'),
    ]
    
    # Asosiy maydonlar
    order_id = models.CharField(max_length=255, unique=True, db_index=True, verbose_name='Buyurtma ID')
    customer_name = models.CharField(max_length=255, verbose_name='Mijoz ismi')
    customer_phone = models.CharField(max_length=20, verbose_name='Telefon raqam')
    customer_email = models.EmailField(blank=True, null=True, verbose_name='Email')
    
    # Buyurtma ma'lumotlari
    items = models.JSONField(default=list, verbose_name='Mahsulotlar')
    total_amount = models.DecimalField(max_digits=12, decimal_places=2, default=0, verbose_name='Jami summa (so\'m)')
    total_amount_tiyin = models.BigIntegerField(default=0, verbose_name='Jami summa (tiyin)')
    
    # Holat
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default=STATUS_PENDING, verbose_name='Holat')
    is_paid = models.BooleanField(default=False, verbose_name='To\'langan')
    payment_method = models.CharField(max_length=50, blank=True, null=True, verbose_name='To\'lov usuli')
    
    # Manzil
    delivery_address = models.CharField(max_length=255, blank=True, null=True, verbose_name='Yetkazib berish manzili')
    delivery_city = models.CharField(max_length=100, blank=True, null=True, verbose_name='Shahar')
    delivery_region = models.CharField(max_length=100, blank=True, null=True, verbose_name='Viloyat')
    
    # Izohlar
    customer_notes = models.TextField(blank=True, null=True, verbose_name='Mijoz izohi')
    admin_notes = models.TextField(blank=True, null=True, verbose_name='Admin izohi')
    
    # Vaqt maydonlari
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='Yaratilgan')
    updated_at = models.DateTimeField(auto_now=True, verbose_name='Yangilangan')
    paid_at = models.DateTimeField(blank=True, null=True, verbose_name='To\'langan vaqt')
    
    class Meta:
        db_table = 'orders'
        verbose_name = 'Buyurtma'
        verbose_name_plural = 'Buyurtmalar'
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['order_id']),
            models.Index(fields=['customer_phone']),
            models.Index(fields=['status']),
            models.Index(fields=['created_at']),
        ]
    
    def __str__(self):
        return f"Order {self.order_id} - {self.customer_name}"
    
    def mark_as_paid(self):
        """Buyurtmani to'langan deb belgilash"""
        self.status = self.STATUS_PAID
        self.paid_at = timezone.now()
        self.save()
    
    # Payme-pkg uchun kerakli metodlar
    def check_order_amount(self, amount):
        """
        Payme-pkg uchun summa validatsiyasi
        amount - tiyin formatda
        """
        if amount != self.total_amount_tiyin:
            from payme.errors import PerformTransactionDoesNotExist
            raise PerformTransactionDoesNotExist()
        return True
    
    def to_dict(self):
        """Dict formatda qaytarish"""
        return {
            'order_id': self.order_id,
            'customer_name': self.customer_name,
            'customer_phone': self.customer_phone,
            'items': self.items,
            'total_amount': float(self.total_amount),
            'status': self.status,
            'payment_method': self.payment_method,
            'created_at': self.created_at.isoformat(),
            'paid_at': self.paid_at.isoformat() if self.paid_at else None,
        }


class OrderItem(models.Model):
    """Buyurtma mahsulotlari"""
    
    order = models.ForeignKey(Order, on_delete=models.CASCADE, related_name='order_items', verbose_name='Buyurtma')
    product_id = models.CharField(max_length=255, blank=True, verbose_name='Mahsulot ID')
    product_name = models.CharField(max_length=255, verbose_name='Mahsulot nomi')
    product_type = models.CharField(max_length=50, verbose_name='Mahsulot turi')  # panel, inverter, modul
    quantity = models.IntegerField(default=1, verbose_name='Miqdor')
    price = models.DecimalField(max_digits=12, decimal_places=2, verbose_name='Narx')
    total = models.DecimalField(max_digits=12, decimal_places=2, verbose_name='Jami', editable=False)
    
    class Meta:
        db_table = 'order_items'
        verbose_name = 'Buyurtma Mahsuloti'
        verbose_name_plural = 'Buyurtma Mahsulotlari'
    
    def __str__(self):
        return f"{self.product_name} x {self.quantity}"
    
    def save(self, *args, **kwargs):
        """Saqlashda jami summani hisoblash"""
        self.total = self.price * self.quantity
        super().save(*args, **kwargs)
