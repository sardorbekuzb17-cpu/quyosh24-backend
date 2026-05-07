from django.contrib import admin
from .models import PaymeTransaction
from .order_models import Order, OrderItem


# Admin paneldan Groups va Users ni yashirish
from django.contrib.auth.models import Group, User
admin.site.unregister(Group)


@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    """Buyurtmalar admin paneli - juda sodda"""
    
    list_display = ('id', 'order_id', 'customer_name', 'total_amount', 'is_paid', 'created_at')
    list_filter = ('is_paid', 'created_at')
    search_fields = ('order_id', 'customer_name')
    readonly_fields = ('order_id', 'created_at')
    
    fields = (
        'order_id',
        'customer_name',
        'delivery_address',
        'total_amount',
        'payment_method',
        'is_paid',
    )
    
    def has_add_permission(self, request):
        """Yangi buyurtma qo'shish imkoniyati"""
        return True
    
    def has_delete_permission(self, request, obj=None):
        """O'chirish imkoniyati"""
        return True


@admin.register(PaymeTransaction)
class PaymeTransactionAdmin(admin.ModelAdmin):
    """Payme tranzaksiyalari admin paneli"""
    
    list_display = ('transaction_id', 'order_id', 'amount_sum', 'state', 'created_at')
    list_filter = ('state', 'created_at')
    search_fields = ('transaction_id', 'order_id')
    readonly_fields = ('transaction_id', 'order_id', 'amount', 'state', 'time', 'create_time', 
                      'perform_time', 'cancel_time', 'reason', 'account', 'created_at', 'updated_at')
    
    fieldsets = (
        ('Asosiy Ma\'lumotlar', {
            'fields': ('transaction_id', 'order_id', 'amount', 'state')
        }),
        ('Vaqt Ma\'lumotlari', {
            'fields': ('time', 'create_time', 'perform_time', 'cancel_time')
        }),
        ('Qo\'shimcha', {
            'fields': ('reason', 'account', 'created_at', 'updated_at')
        }),
    )
    
    def amount_sum(self, obj):
        """Summani so'm formatda ko'rsatish"""
        return f"{obj.amount / 100:,.0f} so'm"
    amount_sum.short_description = 'Summa'
    
    def has_add_permission(self, request):
        """Qo'lda tranzaksiya qo'shishni taqiqlash"""
        return False
    
    def has_delete_permission(self, request, obj=None):
        """O'chirishni taqiqlash"""
        return False


# Admin panel sarlavhalarini o'zgartirish
admin.site.site_header = 'Quyosh24 Admin Panel'
admin.site.site_title = 'Quyosh24'
admin.site.index_title = 'Boshqaruv Paneli'
