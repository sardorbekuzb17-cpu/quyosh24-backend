import base64
import json
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_http_methods
from django.utils import timezone
from .models import PaymeTransaction

# Payme konfiguratsiyasi
PAYME_MERCHANT_ID = '69d6d6113663bd982443630d'
PAYME_SECRET_KEY = '4EkYNKATgBk2tyBENNfCaAn&QPVRSGjP2FAj'  # TEST MODE

# Payme xato kodlari
ERRORS = {
    'INVALID_AMOUNT': {
        'code': -31001,
        'message': {
            'uz': "Noto'g'ri summa",
            'ru': "Неверная сумма",
            'en': "Invalid amount"
        }
    },
    'ORDER_NOT_FOUND': {
        'code': -31050,
        'message': {
            'uz': "Buyurtma topilmadi",
            'ru': "Заказ не найден",
            'en': "Order not found"
        }
    },
    'INVALID_ACCOUNT': {
        'code': -31053,
        'message': {
            'uz': "Noto'g'ri hisob",
            'ru': "Неверный счет",
            'en': "Invalid account"
        }
    },
    'TRANSACTION_NOT_FOUND': {
        'code': -31003,
        'message': {
            'uz': "Tranzaksiya topilmadi",
            'ru': "Транзакция не найдена",
            'en': "Transaction not found"
        }
    },
    'CANT_PERFORM': {
        'code': -31008,
        'message': {
            'uz': "Amalga oshirib bo'lmaydi",
            'ru': "Невозможно выполнить",
            'en': "Cannot perform transaction"
        }
    },
}


def check_auth(request):
    """Authorization tekshirish"""
    auth = request.META.get('HTTP_AUTHORIZATION', '')
    if not auth or not auth.startswith('Basic '):
        return False
    
    try:
        credentials = base64.b64decode(auth.split(' ')[1]).decode('utf-8')
        username, password = credentials.split(':')
        return username == 'Paycom' and password == PAYME_SECRET_KEY
    except:
        return False


@csrf_exempt
@require_http_methods(["POST"])
def payme_callback(request):
    """Payme Merchant API callback"""
    
    # Authorization tekshirish
    if not check_auth(request):
        return JsonResponse({
            'jsonrpc': '2.0',
            'id': None,
            'error': {
                'code': -32504,
                'message': {
                    'uz': 'Avtorizatsiya xatosi',
                    'ru': 'Ошибка авторизации',
                    'en': 'Authorization error'
                }
            }
        })
    
    try:
        data = json.loads(request.body)
        method = data.get('method')
        params = data.get('params', {})
        request_id = data.get('id')
        
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
        
        return JsonResponse({
            'jsonrpc': '2.0',
            'id': request_id,
            **result
        })
    
    except Exception as e:
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
    
    # Account tekshirish
    if not account:
        return {'error': ERRORS['INVALID_ACCOUNT']}
    
    # Order ID ni olish (Quyosh24 yoki id)
    order_id = account.get('Quyosh24') or account.get('order_id') or account.get('id', '')
    if not order_id:
        return {'error': ERRORS['INVALID_ACCOUNT']}
    
    # Amount tekshirish
    if not amount or amount < 1:
        return {'error': ERRORS['INVALID_AMOUNT']}
    
    # Database'dan order tekshirish
    try:
        from .order_models import Order
        order = Order.objects.get(id=int(order_id))
        # Summa mos kelishi kerak (tiyin formatda)
        expected_amount = int(order.total_amount * 100)
        if expected_amount != amount:
            return {'error': ERRORS['INVALID_AMOUNT']}
    except (Order.DoesNotExist, ValueError):
        return {'error': ERRORS['ORDER_NOT_FOUND']}
    
    return {'result': {'allow': True}}


def create_transaction(params):
    """Tranzaksiya yaratish"""
    transaction_id = params.get('id')
    time = params.get('time')
    amount = params.get('amount')
    account = params.get('account', {})
    
    # Mavjud tranzaksiyani tekshirish
    try:
        tx = PaymeTransaction.objects.get(transaction_id=transaction_id)
        return {
            'result': {
                'create_time': tx.create_time,
                'transaction': tx.transaction_id,
                'state': tx.state,
            }
        }
    except PaymeTransaction.DoesNotExist:
        pass
    
    # Order ID ni olish (Quyosh24 yoki id)
    order_id = account.get('Quyosh24') or account.get('order_id') or account.get('id', '')
    if not order_id:
        return {'error': ERRORS['INVALID_ACCOUNT']}
    
    # Amount tekshirish
    if not amount or amount < 1:
        return {'error': ERRORS['INVALID_AMOUNT']}
    
    # Database'dan order tekshirish
    try:
        from .order_models import Order
        order = Order.objects.get(id=int(order_id))
        # Summa mos kelishi kerak (tiyin formatda)
        expected_amount = int(order.total_amount * 100)
        if expected_amount != amount:
            return {'error': ERRORS['INVALID_AMOUNT']}
    except (Order.DoesNotExist, ValueError):
        return {'error': ERRORS['ORDER_NOT_FOUND']}
    
    # Yangi tranzaksiya yaratish
    create_time = int(timezone.now().timestamp() * 1000)
    tx = PaymeTransaction.objects.create(
        transaction_id=transaction_id,
        order_id=str(order_id),
        amount=amount,
        time=time,
        create_time=create_time,
        state=PaymeTransaction.STATE_CREATED,
        account=account
    )
    
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
    
    try:
        tx = PaymeTransaction.objects.get(transaction_id=transaction_id)
    except PaymeTransaction.DoesNotExist:
        return {'error': ERRORS['CANT_PERFORM']}
    
    # Bekor qilingan tranzaksiya
    if tx.state in [PaymeTransaction.STATE_CANCELLED, PaymeTransaction.STATE_CANCELLED_AFTER_COMPLETE]:
        return {'error': ERRORS['TRANSACTION_NOT_FOUND']}
    
    # Allaqachon bajarilgan
    if tx.state == PaymeTransaction.STATE_COMPLETED:
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
    
    try:
        tx = PaymeTransaction.objects.get(transaction_id=transaction_id)
    except PaymeTransaction.DoesNotExist:
        return {'error': ERRORS['TRANSACTION_NOT_FOUND']}
    
    # Allaqachon bekor qilingan
    if tx.state in [PaymeTransaction.STATE_CANCELLED, PaymeTransaction.STATE_CANCELLED_AFTER_COMPLETE]:
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
    
    try:
        tx = PaymeTransaction.objects.get(transaction_id=transaction_id)
    except PaymeTransaction.DoesNotExist:
        return {'error': ERRORS['TRANSACTION_NOT_FOUND']}
    
    return {
        'result': tx.to_payme_dict()
    }


def get_statement(params):
    """Tranzaksiyalar ro'yxati"""
    from_time = params.get('from')
    to_time = params.get('to')
    
    transactions = PaymeTransaction.objects.filter(
        create_time__gte=from_time,
        create_time__lte=to_time
    )
    
    return {
        'result': {
            'transactions': [tx.to_payme_dict() for tx in transactions]
        }
    }



# ============================================
# PAYME Integration - Custom Implementation Only
# ============================================

import logging

# Logger sozlash
logger = logging.getLogger(__name__)
