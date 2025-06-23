from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import TransactionViewSet

# api/urls.py
from .views import run_migrations

router = DefaultRouter()
router.register(r'transactions', TransactionViewSet, basename='transaction')

urlpatterns = [
    path('', include(router.urls)),
	path('run-migrations/', run_migrations),
]