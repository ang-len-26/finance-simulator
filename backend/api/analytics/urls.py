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
ENDPOINTS MEJORADOS - MÓDULO ANALYTICS

============= 📊 REPORTES PRINCIPALES (ReportsViewSet) =============
GET    /api/reports/                     -> Listar métricas financieras
POST   /api/reports/                     -> Crear nueva métrica
GET    /api/reports/{id}/                -> Obtener métrica específica
PUT    /api/reports/{id}/                -> Actualizar métrica completa
PATCH  /api/reports/{id}/                -> Actualizar métrica parcialmente
DELETE /api/reports/{id}/                -> Eliminar métrica

============= 📈 ENDPOINTS DE ANÁLISIS =============
GET    /api/reports/metrics/               -> Métricas principales + comparativas
GET    /api/reports/income-vs-expenses/    -> Gráfico ingresos vs gastos mensual
GET    /api/reports/balance-timeline/      -> Timeline balance acumulado
GET    /api/reports/category-distribution/ -> Distribución por categorías (pie)
GET    /api/reports/top-categories/        -> Top 5 categorías con tendencias
GET    /api/reports/recent-transactions/   -> Transacciones recientes con íconos
GET    /api/reports/financial-metrics/     -> Métricas precalculadas por período

============= 🚨 SISTEMA DE ALERTAS =============
GET    /api/reports/alerts/               -> Obtener alertas de presupuesto
POST   /api/reports/mark-alert-read/      -> Marcar alertas como leídas

============= 📊 ANÁLISIS AVANZADO =============
GET    /api/reports/category-trends/      -> Tendencias de categorías en tiempo
GET    /api/reports-overview/             -> Dashboard completo (1 llamada)
GET    /api/financial-ratios/             -> Ratios financieros profesionales

============= 🔍 FILTROS DISPONIBLES =============
PERÍODOS:
- ?period=monthly,quarterly,yearly,custom,last_30_days,last_90_days
- ?start_date=2024-01-01                   -> Fecha inicio (custom)
- ?end_date=2024-12-31                     -> Fecha fin (custom)

ALERTAS:
- ?severity=low,medium,high,critical       -> Filtrar por severidad
- ?alert_type=budget_exceeded,unusual_expense,income_drop,account_low
- ?is_read=true,false                      -> Filtrar por estado leído
- ?include_dismissed=true                  -> Incluir alertas descartadas

OTROS:
- ?limit=10                                -> Límite de resultados
- ?ordering=-period_start,total_income     -> Ordenamiento

============= 💡 RESPUESTAS DE EJEMPLO =============
Métricas principales:
{
  "metrics": {
    "total_income": 3000.00,
    "total_expenses": 1500.00,
    "net_balance": 1500.00,
    "income_change": 15.5,
    "expense_change": -5.2
  }
}

Alertas:
{
  "alerts": [...],
  "summary": {
    "total_alerts": 5,
    "unread_count": 2,
    "critical_count": 1
  }
}

Dashboard completo:
{
  "metrics": {...},
  "charts": {
    "income_vs_expenses": {...},
    "balance_timeline": {...},
    "category_distribution": {...}
  },
  "insights": {
    "top_categories": [...],
    "recent_transactions": [...]
  }
}
"""