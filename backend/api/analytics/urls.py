from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import ReportsViewSet, reports_overview, financial_ratios

router = DefaultRouter()
router.register(r'reports', ReportsViewSet, basename='reports')

urlpatterns = [
    path('', include(router.urls)),
    path('reports-overview/', reports_overview, name='reports-overview'),
    path('financial-ratios/', financial_ratios, name='financial-ratios'),
]

"""
ENDPOINTS

============= 📊 REPORTES (ReportsViewSet) =============
GET    /api/reports/                     -> Listar reportes
POST   /api/reports/                     -> Crear nuevo reporte
GET    /api/reports/{id}/                -> Obtener reporte específico
PUT    /api/reports/{id}/                -> Actualizar reporte completo
PATCH  /api/reports/{id}/                -> Actualizar reporte parcialmente
DELETE /api/reports/{id}/                -> Eliminar reporte
GET    /api/reports/overview/            -> Resumen de reportes
GET    /api/reports/financial-ratios/    -> Ratios financieros
GET    /api/reports/metrics/               -> Métricas principales + comparativas
GET    /api/reports/income-vs-expenses/    -> Datos para gráfico ingresos vs gastos
GET    /api/reports/balance-timeline/      -> Timeline balance acumulado
GET    /api/reports/category-distribution/ -> Distribución por categorías (pie chart)
GET    /api/reports/top-categories/        -> Top 5 categorías con tendencias
GET    /api/reports/recent-transactions/   -> Transacciones recientes con íconos

============= 📈 REPORTES ESPECIALES =============
GET    /api/reports-overview/              -> Todos los reportes en 1 llamada
GET    /api/financial-ratios/              -> Ratios financieros profesionales

============= 🔍 FILTROS DISPONIBLES =============
- ?period=monthly,quarterly,yearly,custom  -> Período análisis
- ?start_date=2024-01-01                   -> Fecha inicio (custom)
- ?end_date=2024-12-31                     -> Fecha fin (custom)
- ?limit=10                                -> Límite resultados

"""