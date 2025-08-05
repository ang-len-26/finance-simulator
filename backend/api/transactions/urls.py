from django.urls import path, include
from rest_framework.routers import DefaultRouter

from .views import TransactionViewSet, CategoryViewSet, BudgetAlertViewSet

router = DefaultRouter()
router.register(r'transactions', TransactionViewSet, basename='transaction')
router.register(r'categories', CategoryViewSet, basename='category')
router.register(r'budget-alerts', BudgetAlertViewSet, basename='budget-alerts')

urlpatterns = [
    path('', include(router.urls)),
]

"""
ENDPOINTS

============= 💳 TRANSACCIONES (TransactionViewSet) =============
GET    /api/transactions/                   -> Listar transacciones
POST   /api/transactions/                   -> Crear nueva transacción
GET    /api/transactions/{id}/              -> Obtener transacción específica
PUT    /api/transactions/{id}/              -> Actualizar transacción completa
PATCH  /api/transactions/{id}/              -> Actualizar transacción parcialmente
DELETE /api/transactions/{id}/              -> Eliminar transacción
GET    /api/transactions/dashboard/         -> Dashboard con métricas

============= 📂 CATEGORÍAS (CategoryViewSet) =============
GET    /api/categories/                     -> Listar categorías
POST   /api/categories/                     -> Crear nueva categoría
GET    /api/categories/{id}/                -> Obtener categoría específica
PUT    /api/categories/{id}/                -> Actualizar categoría completa
PATCH  /api/categories/{id}/                -> Actualizar categoría parcialmente
DELETE /api/categories/{id}/                -> Eliminar categoría
GET    /api/categories/summary/             -> Resumen gastos por categoría

============= 🚨 ALERTAS DE PRESUPUESTO (BudgetAlertViewSet) =============
GET    /api/budget-alerts/                  -> Listar alertas de presupuesto
POST   /api/budget-alerts/                  -> Crear nueva alerta de presupuesto
GET    /api/budget-alerts/{id}/             -> Obtener alerta de presupuesto específica
PUT    /api/budget-alerts/{id}/             -> Actualizar alerta de presupuesto completa
PATCH  /api/budget-alerts/{id}/             -> Actualizar alerta de presupuesto parcialmente
DELETE /api/budget-alerts/{id}/             -> Eliminar alerta de presupuesto

============= 🔍 FILTROS DISPONIBLES =============

- ?min_amount=100&max_amount=1000          -> Rango montos
- ?type=expense,income                     -> Tipos específicos
- ?description=netflix                     -> Buscar en descripción/título
- ?date_after=2024-01-01&date_before=2024-12-31 -> Rango fechas
- ?from_account=1                          -> Cuenta origen
- ?to_account=2                            -> Cuenta destino  
- ?account=1                               -> Cualquier cuenta
- ?bank=BCP                                -> Filtrar por banco
- ?account_type=checking                   -> Tipo de cuenta
- ?location=Lima                           -> Ubicación
- ?tags=comida,trabajo                     -> Etiquetas (JSON)
- ?is_recurring=true                       -> Solo recurrentes
- ?cash_flow=positive,negative             -> Flujo efectivo
- ?category=1  

"""