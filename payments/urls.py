from django.urls import path
from . import views

urlpatterns = [
    path('payme/', views.payme_callback, name='payme_callback'),  # Payme webhook
]
