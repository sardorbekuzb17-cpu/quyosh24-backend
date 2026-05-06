from django.db import models
from django.utils import timezone


class PaymeTransaction(models.Model):
    """Payme tranzaksiyalari modeli"""
    
    # Tranzaksiya holatlari
    STATE_CREATED = 1  # Yaratilgan
    STATE_COMPLETED = 2  # Bajarilgan
    STATE_CANCELLED = -1  # Bekor qilingan (yaratilgan holatda)
    STATE_CANCELLED_AFTER_COMPLETE = -2  # Bekor qilingan (bajarilgan holatda)
    
    STATE_CHOICES = [
        (STATE_CREATED, 'Yaratilgan'),
        (STATE_COMPLETED, 'Bajarilgan'),
        (STATE_CANCELLED, 'Bekor qilingan'),
        (STATE_CANCELLED_AFTER_COMPLETE, 'Bekor qilingan (bajarilgandan keyin)'),
    ]
    
    # Asosiy maydonlar
    transaction_id = models.CharField(max_length=255, unique=True, db_index=True, verbose_name='Tranzaksiya ID')
    order_id = models.CharField(max_length=255, db_index=True, verbose_name='Buyurtma ID')
    amount = models.BigIntegerField(verbose_name='Summa (tiyin)')
    state = models.IntegerField(choices=STATE_CHOICES, default=STATE_CREATED, verbose_name='Holat')
    
    # Vaqt maydonlari
    time = models.BigIntegerField(verbose_name='Payme vaqti (milliseconds)')
    create_time = models.BigIntegerField(verbose_name='Yaratilgan vaqt (milliseconds)')
    perform_time = models.BigIntegerField(default=0, verbose_name='Bajarilgan vaqt (milliseconds)')
    cancel_time = models.BigIntegerField(default=0, verbose_name='Bekor qilingan vaqt (milliseconds)')
    
    # Qo'shimcha maydonlar
    reason = models.IntegerField(null=True, blank=True, verbose_name='Bekor qilish sababi')
    account = models.JSONField(default=dict, verbose_name='Account ma\'lumotlari')
    
    # Django maydonlari
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='Yaratilgan')
    updated_at = models.DateTimeField(auto_now=True, verbose_name='Yangilangan')
    
    class Meta:
        db_table = 'custom_payme_transactions'  # payme-pkg bilan konflikt bo'lmasligi uchun
        verbose_name = 'Payme Tranzaksiya (Custom)'
        verbose_name_plural = 'Payme Tranzaksiyalar (Custom)'
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['transaction_id']),
            models.Index(fields=['order_id']),
            models.Index(fields=['state']),
            models.Index(fields=['create_time']),
        ]
    
    def __str__(self):
        return f"Transaction {self.transaction_id} - {self.get_state_display()}"
    
    def to_payme_dict(self):
        """Payme API uchun dict qaytarish"""
        return {
            'create_time': self.create_time,
            'perform_time': self.perform_time,
            'cancel_time': self.cancel_time,
            'transaction': self.transaction_id,
            'state': self.state,
            'reason': self.reason,
        }
