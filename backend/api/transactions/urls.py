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
ENDPOINTS COMPLETOS - DOCUMENTACIÓN PARA FRONTEND

============= 💳 TRANSACCIONES (TransactionViewSet) =============
✅ CRUD BÁSICO:
GET    /api/transactions/                   -> Listar transacciones (paginado)
POST   /api/transactions/                   -> Crear nueva transacción
GET    /api/transactions/{id}/              -> Obtener transacción específica
PUT    /api/transactions/{id}/              -> Actualizar transacción completa
PATCH  /api/transactions/{id}/              -> Actualizar transacción parcialmente
DELETE /api/transactions/{id}/              -> Eliminar transacción

✅ ENDPOINTS ADICIONALES:
GET    /api/transactions/dashboard/         -> Dashboard con métricas del período
GET    /api/transactions/recent/            -> Últimas 10 transacciones
GET    /api/transactions/by_type/           -> Transacciones agrupadas por tipo
GET    /api/transactions/search/?q=netflix  -> Búsqueda avanzada

============= 📂 CATEGORÍAS (CategoryViewSet) =============
✅ CRUD BÁSICO:
GET    /api/categories/                     -> Listar categorías activas
POST   /api/categories/                     -> Crear nueva categoría
GET    /api/categories/{id}/                -> Obtener categoría específica
PUT    /api/categories/{id}/                -> Actualizar categoría completa
PATCH  /api/categories/{id}/                -> Actualizar categoría parcialmente
DELETE /api/categories/{id}/                -> Eliminar categoría

✅ ENDPOINTS ADICIONALES:
GET    /api/categories/by_type/             -> Categorías agrupadas por income/expense
GET    /api/categories/hierarchy/           -> Estructura jerárquica (padres + hijos)
GET    /api/categories/{id}/transactions/   -> Transacciones de una categoría
GET    /api/categories/{id}/monthly_trend/  -> Tendencia mensual (12 meses)
POST   /api/categories/create_defaults/     -> Crear categorías predeterminadas
GET    /api/categories/statistics/          -> Estadísticas generales
GET    /api/categories/summary_report/      -> Reporte de resumen con comparativas

============= 🚨 ALERTAS DE PRESUPUESTO (BudgetAlertViewSet) =============
✅ SOLO LECTURA:
GET    /api/budget-alerts/                  -> Todas las alertas del usuario
GET    /api/budget-alerts/{id}/             -> Alerta específica
POST   /api/budget-alerts/{id}/mark_read/   -> Marcar como leída
GET    /api/budget-alerts/unread/           -> Solo alertas no leídas

============= 🔍 FILTROS DISPONIBLES (TransactionViewSet) =============
✅ MONTOS:
?min_amount=100                            -> Monto mínimo
?max_amount=1000                           -> Monto máximo

✅ TIPOS:
?type=expense                              -> Tipo específico
?cash_flow=positive                        -> Flujo: positive, negative, internal

✅ FECHAS:
?date_after=2024-01-01                     -> Desde fecha
?date_before=2024-12-31                    -> Hasta fecha

✅ CUENTAS:
?from_account=1                            -> Cuenta origen (ID)
?to_account=2                              -> Cuenta destino (ID)
?account=1                                 -> Cualquier cuenta (origen O destino)
?bank=BCP                                  -> Banco específico
?account_type=checking                     -> Tipo de cuenta

✅ CATEGORÍAS:
?category=1                                -> Categoría específica (ID)

✅ BÚSQUEDA:
?description=netflix                       -> Buscar en descripción/título
?location=Lima                             -> Ubicación
?tags=comida,trabajo                       -> Etiquetas (separadas por coma)

✅ RECURRENCIA:
?is_recurring=true                         -> Solo recurrentes
?recurring_frequency=monthly               -> Frecuencia específica

✅ REFERENCIAS:
?has_reference=true                        -> Con/sin número de referencia

✅ ORDENAMIENTO:
?ordering=-date                            -> Por fecha descendente
?ordering=amount                           -> Por monto ascendente
?ordering=-amount,date                     -> Múltiples campos

✅ PAGINACIÓN:
?page=2                                    -> Página específica
?page_size=20                              -> Elementos por página

============= 📋 FILTROS PARA CATEGORÍAS =============
?is_active=true                            -> Solo activas/inactivas
?category_type=expense                     -> Tipo: income, expense, both
?parent=null                               -> Solo categorías padre
?parent=1                                  -> Subcategorías de categoría específica

============= 🎯 EJEMPLOS DE CONSULTAS COMPLEJAS =============

# Gastos en restaurantes del último mes:
GET /api/transactions/?type=expense&category=5&date_after=2024-07-01

# Ingresos mayores a $1000 en cuenta BCP:
GET /api/transactions/?type=income&min_amount=1000&bank=BCP

# Transferencias entre cuentas específicas:
GET /api/transactions/?type=transfer&from_account=1&to_account=2

# Gastos recurrentes mensuales:
GET /api/transactions/?type=expense&is_recurring=true&recurring_frequency=monthly

# Búsqueda de Netflix en cualquier campo:
GET /api/transactions/search/?q=netflix

# Dashboard del trimestre actual:
GET /api/transactions/dashboard/?start_date=2024-07-01&end_date=2024-09-30

# Categorías más usadas del mes:
GET /api/categories/statistics/?start_date=2024-08-01&end_date=2024-08-31

============= ⚠️ ERRORES COMUNES A EVITAR =============
❌ /api/transaction/        -> Usar /api/transactions/ (plural)
❌ /api/category/           -> Usar /api/categories/ (plural)
❌ ?type=income,expense     -> Usar filtros separados o múltiples requests
❌ ?date=2024-08-01         -> Usar ?date_after= y ?date_before=
❌ ?account_id=1            -> Usar ?account=1, ?from_account=1, o ?to_account=1

============= 🔐 AUTENTICACIÓN REQUERIDA =============
Todos los endpoints requieren:
Authorization: Bearer {jwt_token}

Usuarios solo pueden acceder a sus propios datos.
"""