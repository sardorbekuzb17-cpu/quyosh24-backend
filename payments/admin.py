from django.contrib import admin
from django.utils.html import format_html
from .models import PaymeTransaction
from .order_models import Order, OrderItem


@admin.register(PaymeTransaction)
class PaymeTransactionAdmin(admin.ModelAdmin):
    """Payme Tranzaksiyalar Admin"""
    
    list_display = [
        'transaction_id_short',
        'order_id',
        'amount_som',
        'state_badge',
        'create_time_formatted',
    ]
    
    list_filter = [
        'state',
        'created_at',
    ]
    
    search_fields = [
        'transaction_id',
        'order_id',
    ]
    
    readonly_fields = [
        'transaction_id',
        'order_id',
        'amount',
        'time',
        'create_time',
        'perform_time',
        'cancel_time',
        'state',
        'reason',
        'account',
        'created_at',
        'updated_at',
    ]
    
    def transaction_id_short(self, obj):
        """Qisqa tranzaksiya ID"""
        return f"{obj.transaction_id[:8]}...{obj.transaction_id[-8:]}"
    transaction_id_short.short_description = 'Tranzaksiya ID'
    
    def amount_som(self, obj):
        """Summa so'mda"""
        return f"{obj.amount / 100:,.0f} so'm"
    amount_som.short_description = 'Summa'
    
    def state_badge(self, obj):
        """Holat badge"""
        colors = {
            1: 'orange',
            2: 'green',
            -1: 'red',
            -2: 'darkred',
        }
        color = colors.get(obj.state, 'gray')
        return format_html(
            '<span style="background-color: {}; color: white; padding: 3px 10px; border-radius: 3px;">{}</span>',
            color,
            obj.get_state_display()
        )
    state_badge.short_description = 'Holat'
    
    def create_time_formatted(self, obj):
        """Yaratilgan vaqt"""
        return obj.created_at.strftime('%Y-%m-%d %H:%M:%S')
    create_time_formatted.short_description = 'Yaratilgan'


class OrderItemInline(admin.TabularInline):
    """Buyurtma mahsulotlari inline"""
    model = OrderItem
    extra = 1
    fields = ['product_name', 'product_type', 'quantity', 'price']
    readonly_fields = []


@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    """Buyurtmalar Admin"""
    
    list_display = [
        'customer_name',
        'address_short',
        'total_cost',
        'payment_method',
        'is_paid',
    ]
    
    list_filter = [
        'status',
        'payment_method',
        'delivery_region',
        'created_at',
    ]
    
    search_fields = [
        'order_id',
        'customer_name',
        'customer_phone',
        'customer_email',
    ]
    
    readonly_fields = [
        'order_id',
        'total_amount',
        'total_amount_tiyin',
        'created_at',
        'updated_at',
        'paid_at',
    ]
    
    fieldsets = (
        ('Mijoz Ma\'lumotlari', {
            'fields': ('customer_name', 'customer_phone', 'customer_email')
        }),
        ('Yetkazib Berish', {
            'fields': ('delivery_address', 'delivery_city', 'delivery_region')
        }),
        ('Buyurtma', {
            'fields': ('status', 'payment_method')
        }),
        ('Izohlar', {
            'fields': ('customer_notes', 'admin_notes'),
            'classes': ('collapse',)
        }),
    )
    
    inlines = [OrderItemInline]
    
    actions = ['mark_as_paid', 'mark_as_processing', 'mark_as_shipped']
    
    def address_short(self, obj):
        """Qisqa manzil"""
        if obj.delivery_address:
            address = obj.delivery_address[:50]
            if len(obj.delivery_address) > 50:
                address += '...'
            return address
        return '-'
    address_short.short_description = 'Manzil'
    
    def total_cost(self, obj):
        """Jami summa"""
        return f"{obj.total_amount:,.0f} so'm"
    total_cost.short_description = 'Jami Summa'
    
    def is_paid(self, obj):
        """To'langan yoki yo'q"""
        if obj.status == Order.STATUS_PAID or obj.paid_at:
            return format_html(
                '<span style="color: green; font-weight: bold;">✓ To\'langan</span>'
            )
        return format_html(
            '<span style="color: red;">✗ To\'lanmagan</span>'
        )
    is_paid.short_description = 'To\'lov Holati'
    
    def save_model(self, request, obj, form, change):
        """Buyurtmani saqlashda jami summani hisoblash"""
        if not change:  # Yangi buyurtma
            obj.order_id = self.generate_order_id()
        super().save_model(request, obj, form, change)
        
        # Jami summani hisoblash
        total = sum(item.total for item in obj.order_items.all())
        obj.total_amount = total
        obj.total_amount_tiyin = int(total * 100)
        obj.save()
    
    def generate_order_id(self):
        """Buyurtma ID generatsiya qilish"""
        from datetime import datetime
        import random
        import string
        
        now = datetime.now()
        date_str = now.strftime('%Y%m%d')
        time_str = now.strftime('%H%M%S')
        random_str = ''.join(random.choices(string.ascii_uppercase + string.digits, k=6))
        
        return f'QUYOSH24-{date_str}-{time_str}-{random_str}'
    
    # Actions
    def mark_as_paid(self, request, queryset):
        """To'langan deb belgilash"""
        updated = queryset.update(status=Order.STATUS_PAID)
        self.message_user(request, f'{updated} ta buyurtma to\'langan deb belgilandi.')
    mark_as_paid.short_description = "To'langan deb belgilash"
    
    def mark_as_processing(self, request, queryset):
        """Jarayonda deb belgilash"""
        updated = queryset.update(status=Order.STATUS_PROCESSING)
        self.message_user(request, f'{updated} ta buyurtma jarayonda deb belgilandi.')
    mark_as_processing.short_description = "Jarayonda deb belgilash"
    
    def mark_as_shipped(self, request, queryset):
        """Yuborilgan deb belgilash"""
        updated = queryset.update(status=Order.STATUS_SHIPPED)
        self.message_user(request, f'{updated} ta buyurtma yuborilgan deb belgilandi.')
    mark_as_shipped.short_description = "Yuborilgan deb belgilash"
