from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import (
    TransactionViewSet,
    AccountViewSet,
    ReportsViewSet,
    CategoryViewSet,
    run_migrations,
    create_superuser,
    register_user,
    create_demo_user,
    reports_overview,
    financial_ratios,
	FinancialGoalViewSet,
    GoalContributionViewSet, 
    GoalTemplateViewSet,
    create_goal_templates,
    goals_calendar,
    goals_insights,
)

# AGREGAR en router.register():
router = DefaultRouter()
router.register(r'transactions', TransactionViewSet, basename='transaction')
router.register(r'accounts', AccountViewSet, basename='account')
router.register(r'reports', ReportsViewSet, basename='reports')
router.register(r'categories', CategoryViewSet, basename='category')
router.register(r'goals', FinancialGoalViewSet, basename='goal')
router.register(r'goal-contributions', GoalContributionViewSet, basename='goal-contribution')
router.register(r'goal-templates', GoalTemplateViewSet, basename='goal-template')


urlpatterns = [
    # Endpoints del router (CRUD automático)
    path('', include(router.urls)),
    
    # Endpoints de autenticación
    path('register/', register_user, name='register'),
    path('demo/', create_demo_user, name='demo'),
    
    # NUEVOS ENDPOINTS DE REPORTES
    path('reports-overview/', reports_overview, name='reports-overview'),
    path('financial-ratios/', financial_ratios, name='financial-ratios'),
    
    # Endpoints de utilidades
    path('run-migrations/', run_migrations),
    path('create-superuser/', create_superuser),

	# Endpoints de metas financieras
	path('create-goal-templates/', create_goal_templates, name='create-goal-templates'),
    path('goals-calendar/', goals_calendar, name='goals-calendar'),
    path('goals-insights/', goals_insights, name='goals-insights'),
]

# =====================================================
# ENDPOINTS DISPONIBLES COMPLETOS:
# =====================================================

# ============= CUENTAS =============
# GET    /api/accounts/                    -> Listar cuentas
# POST   /api/accounts/                    -> Crear cuenta
# GET    /api/accounts/{id}/               -> Obtener cuenta específica
# PUT    /api/accounts/{id}/               -> Actualizar cuenta
# PATCH  /api/accounts/{id}/               -> Actualizar parcialmente
# DELETE /api/accounts/{id}/               -> Eliminar cuenta
# GET    /api/accounts/summary/            -> Resumen financiero de todas las cuentas
# GET    /api/accounts/{id}/transactions/  -> Transacciones de una cuenta específica
# GET    /api/accounts/{id}/balance_history/ -> Historial de balance (30 días)
# POST   /api/accounts/{id}/reconcile/     -> Conciliar cuenta con balance real

# ============= TRANSACCIONES =============
# GET    /api/transactions/                -> Listar transacciones (con filtros)
# POST   /api/transactions/                -> Crear transacción
# GET    /api/transactions/{id}/           -> Obtener transacción específica
# PUT    /api/transactions/{id}/           -> Actualizar transacción
# PATCH  /api/transactions/{id}/           -> Actualizar parcialmente
# DELETE /api/transactions/{id}/           -> Eliminar transacción
# GET    /api/transactions/dashboard/      -> Dashboard con métricas clave

# ============= 🆕 REPORTES AVANZADOS =============
# GET    /api/reports/metrics/             -> Métricas principales con comparativas
# GET    /api/reports/income-vs-expenses/  -> Datos gráfico Ingresos vs Gastos
# GET    /api/reports/balance-timeline/    -> Balance acumulado en el tiempo
# GET    /api/reports/category-distribution/ -> Distribución gastos por categoría
# GET    /api/reports/top-categories/      -> Top 5 categorías con comparativas
# GET    /api/reports/recent-transactions/ -> Transacciones recientes con íconos

# ============= 🆕 ENDPOINTS ESPECIALES =============
# GET    /api/reports-overview/            -> Todos los datos de reportes en 1 llamada
# GET    /api/financial-ratios/            -> Ratios financieros profesionales

# ============= METAS FINANCIERAS =============
# GET    /api/goals/                           -> Listar metas del usuario
# POST   /api/goals/                           -> Crear nueva meta
# GET    /api/goals/{id}/                      -> Obtener meta específica
# PUT    /api/goals/{id}/                      -> Actualizar meta completa
# PATCH  /api/goals/{id}/                      -> Actualizar meta parcialmente
# DELETE /api/goals/{id}/                      -> Eliminar meta
# GET    /api/goals/dashboard/                 -> Dashboard completo de metas
# GET    /api/goals/summary/                   -> Resumen rápido para widgets
# POST   /api/goals/{id}/add_contribution/     -> Agregar contribución a meta
# GET    /api/goals/{id}/contributions/        -> Ver contribuciones de meta
# POST   /api/goals/{id}/add_milestone/        -> Agregar hito a meta
# POST   /api/goals/{id}/pause/                -> Pausar meta
# POST   /api/goals/{id}/resume/               -> Reanudar meta pausada
# POST   /api/goals/{id}/complete/             -> Marcar meta como completada
# GET    /api/goals/{id}/analytics/            -> Análisis detallado de meta

# ============= CONTRIBUCIONES =============
# GET    /api/goal-contributions/              -> Listar contribuciones del usuario
# POST   /api/goal-contributions/              -> Crear contribución manual
# GET    /api/goal-contributions/{id}/         -> Obtener contribución específica
# PUT    /api/goal-contributions/{id}/         -> Actualizar contribución
# DELETE /api/goal-contributions/{id}/         -> Eliminar contribución

# ============= PLANTILLAS DE METAS =============
# GET    /api/goal-templates/                  -> Listar plantillas disponibles
# GET    /api/goal-templates/{id}/             -> Obtener plantilla específica
# POST   /api/goal-templates/{id}/create_goal/ -> Crear meta desde plantilla
# GET    /api/goal-templates/by_category/      -> Plantillas agrupadas por tipo

# ============= ENDPOINTS ESPECIALES =============
# POST   /api/create-goal-templates/           -> Crear plantillas predeterminadas
# GET    /api/goals-calendar/                  -> Vista calendario con fechas importantes
# GET    /api/goals-insights/                  -> Insights inteligentes sobre metas

# ============= 📊 PARÁMETROS PARA REPORTES =============
# Todos los endpoints de reportes soportan:
# ?period=monthly|quarterly|yearly|custom  -> Período de análisis
# ?start_date=2024-01-01                   -> Fecha inicio (para custom)
# ?end_date=2024-12-31                     -> Fecha fin (para custom)
# ?limit=10                                -> Límite resultados (donde aplique)

# ============= FILTROS EXISTENTES =============
# Transacciones:
# ?min_amount=100&max_amount=1000          -> Rango de montos
# ?type=expense                            -> Tipo de transacción
# ?description=netflix                     -> Buscar en descripción
# ?date_after=2024-01-01&date_before=2024-12-31  -> Rango de fechas
# ?from_account=1                          -> Cuenta origen
# ?to_account=2                            -> Cuenta destino
# ?account=1                               -> Cualquier cuenta (origen o destino)
# ?bank=BCP                                -> Filtrar por banco
# ?account_type=checking                   -> Tipo de cuenta
# ?location=Lima                           -> Ubicación
# ?tags=comida,trabajo                     -> Etiquetas
# ?is_recurring=true                       -> Solo recurrentes
# ?cash_flow=positive                      -> Flujo de efectivo
# ?category=1                              -> 🆕 Filtrar por categoría

# Cuentas:
# ?name=corriente                          -> Nombre de cuenta
# ?bank_name=BCP                           -> Banco
# ?account_type=checking                   -> Tipo de cuenta
# ?min_balance=1000                        -> Balance mínimo
# ?is_active=true                          -> Solo cuentas activas

# Metas:
# ?status=active                              -> Filtrar por estado
# ?goal_type=savings                          -> Filtrar por tipo de meta
# ?priority=high                              -> Filtrar por prioridad

# Contribuciones:
# ?start_date=2024-01-01                      -> Desde fecha
# ?end_date=2024-12-31                        -> Hasta fecha
# ?goal=1                                     -> De meta específica

# Calendario:
# ?year=2024                                  -> Año específico
# ?month=12                                   -> Mes específico
