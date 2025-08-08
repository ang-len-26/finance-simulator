from django.urls import path, include
from rest_framework.routers import DefaultRouter

from .views import AccountViewSet

router = DefaultRouter()
router.register(r'accounts', AccountViewSet, basename='account')

urlpatterns = [
    path('', include(router.urls)),
]

"""
ENDPOINTS ACTUALIZADOS

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

============= 🔍 FILTROS DISPONIBLES (IMPLEMENTADOS) =============
- ?name=corriente                          -> Buscar por nombre (contiene)
- ?bank_name=BCP                           -> Buscar por banco (contiene)
- ?account_type=checking                   -> Filtrar por tipo
- ?account_type=checking,savings           -> Múltiples tipos
- ?min_balance=1000                        -> Balance mínimo
- ?max_balance=5000                        -> Balance máximo
- ?is_active=true                          -> Solo cuentas activas
- ?include_in_reports=true                 -> Solo en reportes
- ?currency=PEN                            -> Por moneda
- ?has_transactions=true                   -> Con/sin transacciones

============= 📊 EJEMPLOS DE USO =============
GET /api/accounts/?account_type=checking&is_active=true
GET /api/accounts/?min_balance=1000&max_balance=10000
GET /api/accounts/?name=ahorro&bank_name=bbva
GET /api/accounts/?has_transactions=false    -> Cuentas sin usar

"""