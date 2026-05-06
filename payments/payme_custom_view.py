"""
Custom Payme Webhook View
To'liq nazorat uchun payme-pkg dan mustaqil
"""
import json
import base64
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_http_methods
from django.utils import timezone
from django.conf import settings
from .models import PaymeTransaction
from .order_models import Order


# Payme xato kodlari
class PaymeErrors:
    INVALID_AMOUNT = {
        'code': -31001,
        'message': {
            'uz': "Noto'g'ri summa",
            'ru': "Неверная сумма",
            'en': "Invalid amount"
        }
    }
    
    ORDER_NOT_FOUND = {
        'code': -31050,
        'message': {
            'uz': "Buyurtma topilmadi",
            'ru': "Заказ не найден",
            'en': "Order not found"
        }
    }
    
    INVALID_ACCOUNT = {
        'code': -31053,
        'message': {
            'uz': "Noto'g'ri hisob",
            'ru': "Неверный счет",
            'en': "Invalid account"
        }
    }
    
    TRANSACTION_NOT_FOUND = {
        'code': -31003,
        'message': {
            'uz': "Tranzaksiya topilmadi",
            'ru': "Транзакция не найдена",
            'en': "Transaction not found"
        }
    }
    
    CANT_PERFORM = {
        'code': -31008,
        'message': {
            'uz': "Amalga oshirib bo'lmaydi",
            'ru': "Невозможно выполнить",
            'en': "Cannot perform transaction"
        }
    }
    
    AUTH_ERROR = {
        'code': -32504,
        'message': {
            'uz': 'Avtorizatsiya xatosi',
            'ru': 'Ошибка авторизации',
            'en': 'Authorization error'
        }
    }


def check_auth(request):
    """Authorization tekshirish"""
    auth = request.META.get('HTTP_AUTHORIZATION', '')
    if not auth or not auth.startswith('Basic '):
        return False
    
    try:
        credentials = base64.b64decode(auth.split(' ')[1]).decode('utf-8')
        username, password = credentials.split(':')
        return username == 'Paycom' and password == settings.PAYME_KEY
    except:
        return False


@csrf_exempt
@require_http_methods(["POST"])
def payme_custom_webhook(request):
    """Custom Payme Webhook - to'liq nazorat"""
    
    # Log qilish
    print("\n" + "="*80)
    print("🔔 PAYME SO'ROV KELDI!")
    print("="*80)
    
    # Authorization tekshirish
    if not check_auth(request):
        print("❌ Authorization xatosi!")
        print("="*80 + "\n")
        return JsonResponse({
            'jsonrpc': '2.0',
            'id': None,
            'error': PaymeErrors.AUTH_ERROR
        })
    
    try:
        data = json.loads(request.body)
        method = data.get('method')
        params = data.get('params', {})
        request_id = data.get('id')
        
        print(f"📥 Method: {method}")
        print(f"📥 Params: {json.dumps(params, indent=2, ensure_ascii=False)}")
        print("="*80 + "\n")
        
        # Metodlarni chaqirish
        if method == 'CheckPerformTransaction':
            result = check_perform_transaction(params)
        elif method == 'CreateTransaction':
            result = create_transaction(params)
        elif method == 'PerformTransaction':
            result = perform_transaction(params)
        elif method == 'CancelTransaction':
            result = cancel_transaction(params)
        elif method == 'CheckTransaction':
            result = check_transaction(params)
        elif method == 'GetStatement':
            result = get_statement(params)
        else:
            result = {
                'error': {
                    'code': -32601,
                    'message': {
                        'uz': "Usul topilmadi",
                        'ru': "Метод не найден",
                        'en': "Method not found"
                    }
                }
            }
        
        # Javobni log qilish
        print("\n" + "="*80)
        print("📤 JAVOB YUBORILDI!")
        print("="*80)
        print(f"📤 Response: {json.dumps(result, indent=2, ensure_ascii=False)}")
        print("="*80 + "\n")
        
        return JsonResponse({
            'jsonrpc': '2.0',
            'id': request_id,
            **result
        })
    
    except Exception as e:
        print(f"❌ Xato: {e}")
        print("="*80 + "\n")
        return JsonResponse({
            'jsonrpc': '2.0',
            'id': None,
            'error': {
                'code': -32400,
                'message': {
                    'uz': "Tizim xatosi",
                    'ru': "Системная ошибка",
                    'en': "System error"
                },
                'data': str(e)
            }
        })


def check_perform_transaction(params):
    """To'lov imkoniyatini tekshirish"""
    amount = params.get('amount')
    account = params.get('account', {})
    
    print(f"🔍 CheckPerformTransaction: amount={amount}, account={account}")
    
    # Account ID ni olish
    account_id = account.get('id')
    if not account_id:
        print("❌ Account ID topilmadi!")
        return {'error': PaymeErrors.INVALID_ACCOUNT}
    
    # Buyurtmani topish
    try:
        order = Order.objects.get(id=account_id)
        print(f"✅ Buyurtma topildi: {order.order_id}, Summa: {order.total_amount_tiyin}")
    except Order.DoesNotExist:
        print(f"❌ Buyurtma topilmadi: id={account_id}")
        return {'error': PaymeErrors.ORDER_NOT_FOUND}
    
    # Summa tekshirish
    if amount != order.total_amount_tiyin:
        print(f"❌ Summa mos kelmaydi: {amount} != {order.total_amount_tiyin}")
        return {'error': PaymeErrors.INVALID_AMOUNT}
    
    print("✅ CheckPerformTransaction muvaffaqiyatli!")
    return {'result': {'allow': True}}


def create_transaction(params):
    """Tranzaksiya yaratish"""
    transaction_id = params.get('id')
    time = params.get('time')
    amount = params.get('amount')
    account = params.get('account', {})
    
    print(f"🔍 CreateTransaction: transaction_id={transaction_id}, amount={amount}")
    
    # Mavjud tranzaksiyani tekshirish
    try:
        tx = PaymeTransaction.objects.get(transaction_id=transaction_id)
        print(f"✅ Tranzaksiya allaqachon mavjud: {tx.transaction_id}")
        return {
            'result': {
                'create_time': tx.create_time,
                'transaction': tx.transaction_id,
                'state': tx.state,
            }
        }
    except PaymeTransaction.DoesNotExist:
        pass
    
    # Account ID ni olish
    account_id = account.get('id')
    if not account_id:
        print("❌ Account ID topilmadi!")
        return {'error': PaymeErrors.INVALID_ACCOUNT}
    
    # Buyurtmani topish
    try:
        order = Order.objects.get(id=account_id)
        print(f"✅ Buyurtma topildi: {order.order_id}, Status: {order.status}")
    except Order.DoesNotExist:
        print(f"❌ Buyurtma topilmadi: id={account_id}")
        return {'error': PaymeErrors.ORDER_NOT_FOUND}
    
    # Summa tekshirish
    if amount != order.total_amount_tiyin:
        print(f"❌ Summa mos kelmaydi: {amount} != {order.total_amount_tiyin}")
        return {'error': PaymeErrors.INVALID_AMOUNT}
    
    # Buyurtma uchun to'lanmagan tranzaksiya borligini tekshirish
    pending_tx = PaymeTransaction.objects.filter(
        order_id=order.order_id,
        state__in=[PaymeTransaction.STATE_CREATED, PaymeTransaction.STATE_COMPLETED]
    ).exclude(transaction_id=transaction_id).first()
    
    if pending_tx:
        print(f"❌ Buyurtma uchun allaqachon tranzaksiya mavjud: {pending_tx.transaction_id}, state={pending_tx.state}")
        return {
            'error': {
                'code': -31099,
                'message': {
                    'uz': "Buyurtma uchun allaqachon tranzaksiya mavjud",
                    'ru': "Для заказа уже существует транзакция",
                    'en': "Transaction already exists for this order"
                },
                'data': f"transaction_id: {pending_tx.transaction_id}"
            }
        }
    
    # Yangi tranzaksiya yaratish
    create_time = int(timezone.now().timestamp() * 1000)
    tx = PaymeTransaction.objects.create(
        transaction_id=transaction_id,
        order_id=order.order_id,
        amount=amount,
        time=time,
        create_time=create_time,
        state=PaymeTransaction.STATE_CREATED,
        account=account
    )
    
    print(f"✅ Tranzaksiya yaratildi: {tx.transaction_id}")
    return {
        'result': {
            'create_time': tx.create_time,
            'transaction': tx.transaction_id,
            'state': tx.state,
        }
    }


def perform_transaction(params):
    """Tranzaksiyani bajarish"""
    transaction_id = params.get('id')
    
    print(f"🔍 PerformTransaction: transaction_id={transaction_id}")
    
    try:
        tx = PaymeTransaction.objects.get(transaction_id=transaction_id)
    except PaymeTransaction.DoesNotExist:
        print(f"❌ Tranzaksiya topilmadi: {transaction_id}")
        return {'error': PaymeErrors.CANT_PERFORM}
    
    # Bekor qilingan tranzaksiya
    if tx.state in [PaymeTransaction.STATE_CANCELLED, PaymeTransaction.STATE_CANCELLED_AFTER_COMPLETE]:
        print(f"❌ Tranzaksiya bekor qilingan: {transaction_id}")
        return {'error': PaymeErrors.TRANSACTION_NOT_FOUND}
    
    # Allaqachon bajarilgan
    if tx.state == PaymeTransaction.STATE_COMPLETED:
        print(f"✅ Tranzaksiya allaqachon bajarilgan: {transaction_id}")
        return {
            'result': {
                'transaction': tx.transaction_id,
                'perform_time': tx.perform_time,
                'state': tx.state,
            }
        }
    
    # Tranzaksiyani bajarish
    tx.state = PaymeTransaction.STATE_COMPLETED
    tx.perform_time = int(timezone.now().timestamp() * 1000)
    tx.save()
    
    # Buyurtmani to'langan deb belgilash
    try:
        order = Order.objects.get(order_id=tx.order_id)
        order.is_paid = True
        order.status = Order.STATUS_PAID
        order.paid_at = timezone.now()
        order.save()
        print(f"✅ Buyurtma to'langan deb belgilandi: {order.order_id}")
    except Order.DoesNotExist:
        print(f"⚠️ Buyurtma topilmadi: {tx.order_id}")
    
    print(f"✅ Tranzaksiya bajarildi: {transaction_id}")
    return {
        'result': {
            'transaction': tx.transaction_id,
            'perform_time': tx.perform_time,
            'state': tx.state,
        }
    }


def cancel_transaction(params):
    """Tranzaksiyani bekor qilish"""
    transaction_id = params.get('id')
    reason = params.get('reason')
    
    print(f"🔍 CancelTransaction: transaction_id={transaction_id}, reason={reason}")
    
    try:
        tx = PaymeTransaction.objects.get(transaction_id=transaction_id)
    except PaymeTransaction.DoesNotExist:
        print(f"❌ Tranzaksiya topilmadi: {transaction_id}")
        return {'error': PaymeErrors.TRANSACTION_NOT_FOUND}
    
    # Allaqachon bekor qilingan
    if tx.state in [PaymeTransaction.STATE_CANCELLED, PaymeTransaction.STATE_CANCELLED_AFTER_COMPLETE]:
        print(f"✅ Tranzaksiya allaqachon bekor qilingan: {transaction_id}")
        return {
            'result': {
                'transaction': tx.transaction_id,
                'cancel_time': tx.cancel_time,
                'state': tx.state,
            }
        }
    
    # Bekor qilish
    if tx.state == PaymeTransaction.STATE_CREATED:
        tx.state = PaymeTransaction.STATE_CANCELLED
    else:
        tx.state = PaymeTransaction.STATE_CANCELLED_AFTER_COMPLETE
    
    tx.cancel_time = int(timezone.now().timestamp() * 1000)
    tx.reason = reason
    tx.save()
    
    print(f"✅ Tranzaksiya bekor qilindi: {transaction_id}")
    return {
        'result': {
            'transaction': tx.transaction_id,
            'cancel_time': tx.cancel_time,
            'state': tx.state,
        }
    }


def check_transaction(params):
    """Tranzaksiya holatini tekshirish"""
    transaction_id = params.get('id')
    
    print(f"🔍 CheckTransaction: transaction_id={transaction_id}")
    
    try:
        tx = PaymeTransaction.objects.get(transaction_id=transaction_id)
    except PaymeTransaction.DoesNotExist:
        print(f"❌ Tranzaksiya topilmadi: {transaction_id}")
        return {'error': PaymeErrors.TRANSACTION_NOT_FOUND}
    
    print(f"✅ Tranzaksiya topildi: {transaction_id}, state={tx.state}")
    return {
        'result': tx.to_payme_dict()
    }


def get_statement(params):
    """Tranzaksiyalar ro'yxati"""
    from_time = params.get('from')
    to_time = params.get('to')
    
    print(f"🔍 GetStatement: from={from_time}, to={to_time}")
    
    transactions = PaymeTransaction.objects.filter(
        create_time__gte=from_time,
        create_time__lte=to_time
    )
    
    print(f"✅ {transactions.count()} ta tranzaksiya topildi")
    return {
        'result': {
            'transactions': [tx.to_payme_dict() for tx in transactions]
        }
    }
