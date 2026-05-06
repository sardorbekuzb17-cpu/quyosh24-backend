from django.urls import path
from . import views
from .payme_custom_view import payme_custom_webhook

urlpatterns = [
    path('payme/', views.payme_callback, name='payme_callback'),  # Old callback
    path('payme-pkg/', views.PaymeCallBackAPIView.as_view(), name='payme_pkg_callback'),  # payme-pkg callback
    path('payme-custom/', payme_custom_webhook, name='payme_custom_webhook'),  # Custom webhook
]
