from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import (
    TransactionViewSet,
    AccountViewSet,
    ReportsViewSet,
    CategoryViewSet,
    FinancialGoalViewSet,
    GoalContributionViewSet, 
    GoalTemplateViewSet,
    BudgetAlertViewSet,
    # Funciones de utilidad
    run_migrations,
    create_superuser,
    register_user,
    create_demo_user,
    reports_overview,
    financial_ratios,
    create_goal_templates,
    goals_calendar,
    goals_insights,
)

# =====================================================
# CONFIGURACIÓN DEL ROUTER
# =====================================================
router = DefaultRouter()

# ViewSets principales - CRUD automático
router.register(r'transactions', TransactionViewSet, basename='transaction')
router.register(r'accounts', AccountViewSet, basename='account')
router.register(r'categories', CategoryViewSet, basename='category')

# ViewSets de reportes
router.register(r'reports', ReportsViewSet, basename='reports')

# ViewSets de metas financieras
router.register(r'goals', FinancialGoalViewSet, basename='goal')
router.register(r'goal-contributions', GoalContributionViewSet, basename='goal-contribution')
router.register(r'goal-templates', GoalTemplateViewSet, basename='goal-template')

# ViewSets de alertas
router.register(r'budget-alerts', BudgetAlertViewSet, basename='budget-alerts')


# =====================================================
# URLS PATTERNS - ENDPOINTS PERSONALIZADOS
# =====================================================
urlpatterns = [
    # 🔥 IMPORTANTE: Router debe ir PRIMERO para evitar conflictos
    path('', include(router.urls)),
    
    # ============= AUTENTICACIÓN =============
    path('auth/register/', register_user, name='register'),
    path('auth/demo/', create_demo_user, name='demo'),
    
    # ============= REPORTES ESPECIALES =============
    path('reports-overview/', reports_overview, name='reports-overview'),
    path('financial-ratios/', financial_ratios, name='financial-ratios'),
    
    # ============= METAS FINANCIERAS - ENDPOINTS ESPECIALES =============
    path('setup/create-goal-templates/', create_goal_templates, name='create-goal-templates'),
    path('goals-calendar/', goals_calendar, name='goals-calendar'),
    path('goals-insights/', goals_insights, name='goals-insights'),
    
    # ============= UTILIDADES DE SETUP =============
    path('setup/run-migrations/', run_migrations, name='run-migrations'),
    path('setup/create-superuser/', create_superuser, name='create-superuser'),
]

# =====================================================
# 📋 DOCUMENTACIÓN DE ENDPOINTS DISPONIBLES
# =====================================================

"""
ENDPOINTS FINALES DESPUÉS DE OPTIMIZACIÓN:

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

============= 💸 TRANSACCIONES (TransactionViewSet) =============
GET    /api/transactions/                  -> Listar con filtros avanzados
POST   /api/transactions/                  -> Crear transacción
GET    /api/transactions/{id}/             -> Obtener transacción específica
PUT    /api/transactions/{id}/             -> Actualizar transacción
PATCH  /api/transactions/{id}/             -> Actualizar parcialmente
DELETE /api/transactions/{id}/             -> Eliminar transacción
GET    /api/transactions/dashboard/        -> Dashboard con métricas

============= 🏷️ CATEGORÍAS (CategoryViewSet) =============
GET    /api/categories/                    -> Listar categorías activas
POST   /api/categories/                    -> Crear categoría personalizada
GET    /api/categories/{id}/               -> Obtener categoría específica
PUT    /api/categories/{id}/               -> Actualizar categoría
DELETE /api/categories/{id}/               -> Eliminar categoría
GET    /api/categories/summary/            -> Resumen gastos por categoría

============= 📊 REPORTES (ReportsViewSet) =============
GET    /api/reports/metrics/               -> Métricas principales + comparativas
GET    /api/reports/income-vs-expenses/    -> Datos para gráfico ingresos vs gastos
GET    /api/reports/balance-timeline/      -> Timeline balance acumulado
GET    /api/reports/category-distribution/ -> Distribución por categorías (pie chart)
GET    /api/reports/top-categories/        -> Top 5 categorías con tendencias
GET    /api/reports/recent-transactions/   -> Transacciones recientes con íconos

============= 🎯 METAS FINANCIERAS (FinancialGoalViewSet) =============
GET    /api/goals/                         -> Listar metas del usuario
POST   /api/goals/                         -> Crear nueva meta
GET    /api/goals/{id}/                    -> Obtener meta específica
PUT    /api/goals/{id}/                    -> Actualizar meta
PATCH  /api/goals/{id}/                    -> Actualizar parcialmente
DELETE /api/goals/{id}/                    -> Eliminar meta
GET    /api/goals/dashboard/               -> Dashboard completo metas
GET    /api/goals/summary/                 -> Resumen para widgets
POST   /api/goals/{id}/add_contribution/   -> Agregar contribución
GET    /api/goals/{id}/contributions/      -> Ver contribuciones
POST   /api/goals/{id}/add_milestone/      -> Agregar hito
POST   /api/goals/{id}/pause/              -> Pausar meta
POST   /api/goals/{id}/resume/             -> Reanudar meta
POST   /api/goals/{id}/complete/           -> Completar meta
GET    /api/goals/{id}/analytics/          -> Análisis detallado

============= 💰 CONTRIBUCIONES (GoalContributionViewSet) =============
GET    /api/goal-contributions/            -> Listar contribuciones usuario
POST   /api/goal-contributions/            -> Crear contribución manual
GET    /api/goal-contributions/{id}/       -> Obtener contribución específica
PUT    /api/goal-contributions/{id}/       -> Actualizar contribución
DELETE /api/goal-contributions/{id}/       -> Eliminar contribución

============= 📋 PLANTILLAS METAS (GoalTemplateViewSet) =============
GET    /api/goal-templates/                -> Listar plantillas disponibles
GET    /api/goal-templates/{id}/           -> Obtener plantilla específica
POST   /api/goal-templates/{id}/create_goal/ -> Crear meta desde plantilla
GET    /api/goal-templates/by_category/    -> Plantillas por categoría

============= 🚨 ALERTAS (BudgetAlertViewSet) =============
GET    /api/budget-alerts/                 -> Listar alertas del usuario
POST   /api/budget-alerts/                 -> Crear alerta personalizada
GET    /api/budget-alerts/{id}/            -> Obtener alerta específica
PATCH  /api/budget-alerts/{id}/            -> Marcar como leída/despedida
DELETE /api/budget-alerts/{id}/            -> Eliminar alerta

============= 🔐 AUTENTICACIÓN =============
POST   /api/auth/register/                 -> Registro de usuario
POST   /api/auth/demo/                     -> Crear usuario demo

============= 📈 REPORTES ESPECIALES =============
GET    /api/reports-overview/              -> Todos los reportes en 1 llamada
GET    /api/financial-ratios/              -> Ratios financieros profesionales

============= 🎯 METAS - ENDPOINTS ESPECIALES =============
POST   /api/setup/create-goal-templates/   -> Crear plantillas predeterminadas
GET    /api/goals-calendar/                -> Vista calendario fechas importantes
GET    /api/goals-insights/                -> Insights inteligentes sobre metas

============= 🛠️ UTILIDADES SETUP =============
POST   /api/setup/run-migrations/          -> Ejecutar migraciones
POST   /api/setup/create-superuser/        -> Crear superusuario

============= 🔍 FILTROS DISPONIBLES =============

Transacciones (/api/transactions/):
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
- ?category=1                              -> Categoría específica

Cuentas (/api/accounts/):

Metas (/api/goals/):
- ?status=active,completed                 -> Estado meta
- ?goal_type=savings,emergency_fund        -> Tipo meta
- ?priority=high,medium,low                -> Prioridad

Reportes (todos):
- ?period=monthly,quarterly,yearly,custom  -> Período análisis
- ?start_date=2024-01-01                   -> Fecha inicio (custom)
- ?end_date=2024-12-31                     -> Fecha fin (custom)
- ?limit=10                                -> Límite resultados

"""