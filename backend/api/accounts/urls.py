from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import AccountViewSet

router = DefaultRouter()
router.register(r'accounts', AccountViewSet, basename='account')

urlpatterns = [
    path('', include(router.urls)),
]


"""
ENDPOINTS

============= 🏦 CUENTAS (AccountViewSet) =============
GET    /api/accounts/                      -> Listar cuentas del usuario
POST   /api/accounts/                      -> Crear nueva cuenta
GET    /api/accounts/{id}/                 -> Obtener cuenta específica  
PUT    /api/accounts/{id}/                 -> Actualizar cuenta completa
PATCH  /api/accounts/{id}/                 -> Actualizar cuenta parcialmente
DELETE /api/accounts/{id}/                 -> Eliminar cuenta
GET    /api/accounts/summary/              -> Resumen financiero global
GET    /api/accounts/{id}/transactions/    -> Transacciones de cuenta específica
GET    /api/accounts/{id}/balance_history/ -> Historial balance (30 días)
POST   /api/accounts/{id}/reconcile/       -> Conciliar balance real

============= 🔍 FILTROS DISPONIBLES =============
- ?name=corriente                          -> Nombre cuenta
- ?bank_name=BCP                           -> Banco específico
- ?account_type=checking,savings           -> Tipos cuenta
- ?min_balance=1000                        -> Balance mínimo
- ?is_active=true                          -> Solo activas

"""