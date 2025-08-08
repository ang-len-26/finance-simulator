from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import (
    FinancialGoalViewSet, GoalContributionViewSet, GoalTemplateViewSet, 
    create_goal_templates, goals_calendar, goals_insights
)

router = DefaultRouter()
router.register(r'goals', FinancialGoalViewSet, basename='goal')
router.register(r'goal-contributions', GoalContributionViewSet, basename='goal-contribution')
router.register(r'goal-templates', GoalTemplateViewSet, basename='goal-template')

urlpatterns = [
    path('', include(router.urls)),
    path('setup/create-goal-templates/', create_goal_templates, name='create-goal-templates'),
    path('goals-calendar/', goals_calendar, name='goals-calendar'),
    path('goals-insights/', goals_insights, name='goals-insights'),
]

"""
ENDPOINTS COMPLETOS - MÓDULO GOALS

============= 🎯 METAS FINANCIERAS (FinancialGoalViewSet) =============
GET    /api/goals/                          -> Listar metas (con filtros)
POST   /api/goals/                          -> Crear nueva meta
GET    /api/goals/{id}/                     -> Obtener meta específica
PUT    /api/goals/{id}/                     -> Actualizar meta completa
PATCH  /api/goals/{id}/                     -> Actualizar meta parcialmente
DELETE /api/goals/{id}/                     -> Eliminar meta

--- ACTIONS PERSONALIZADAS ---
GET    /api/goals/dashboard/                -> Dashboard completo de metas
GET    /api/goals/summary/                  -> Resumen rápido para widgets
POST   /api/goals/{id}/add_contribution/    -> Agregar contribución a meta
GET    /api/goals/{id}/contributions/       -> Ver contribuciones de meta
POST   /api/goals/{id}/add_milestone/       -> Agregar hito a meta
POST   /api/goals/{id}/pause/               -> Pausar meta
POST   /api/goals/{id}/resume/              -> Reanudar meta pausada
POST   /api/goals/{id}/complete/            -> Completar meta manualmente
GET    /api/goals/{id}/analytics/           -> Análisis detallado de meta

============= 💰 CONTRIBUCIONES (GoalContributionViewSet) =============
GET    /api/goal-contributions/             -> Listar todas las contribuciones
POST   /api/goal-contributions/             -> Crear nueva contribución
GET    /api/goal-contributions/{id}/        -> Obtener contribución específica
PUT    /api/goal-contributions/{id}/        -> Actualizar contribución completa
PATCH  /api/goal-contributions/{id}/        -> Actualizar contribución parcial
DELETE /api/goal-contributions/{id}/        -> Eliminar contribución

============= 🏷️ PLANTILLAS (GoalTemplateViewSet) =============
GET    /api/goal-templates/                 -> Listar plantillas disponibles
GET    /api/goal-templates/{id}/            -> Obtener plantilla específica
POST   /api/goal-templates/{id}/create_goal/ -> Crear meta desde plantilla
GET    /api/goal-templates/by_category/     -> Plantillas agrupadas por tipo

============= 🛠️ UTILIDADES =============
POST   /api/setup/create-goal-templates/    -> Crear plantillas por defecto
GET    /api/goals-calendar/                 -> Vista calendario de metas
GET    /api/goals-insights/                 -> Insights inteligentes

============= 🔍 FILTROS DISPONIBLES =============

--- FILTROS PARA METAS (/api/goals/) ---
?title=vacaciones                           -> Buscar en título
?description=auto                           -> Buscar en descripción  
?goal_type=savings,emergency_fund           -> Tipo de meta
?status=active,completed,paused             -> Estado de meta
?priority=high,medium,low                   -> Prioridad
?min_target_amount=1000                     -> Monto objetivo mínimo
?max_target_amount=10000                    -> Monto objetivo máximo
?min_current_amount=500                     -> Progreso mínimo
?max_current_amount=5000                    -> Progreso máximo
?start_date_after=2024-01-01               -> Fecha inicio después de
?start_date_before=2024-12-31              -> Fecha inicio antes de
?target_date_after=2024-06-01              -> Fecha límite después de
?target_date_before=2024-12-31             -> Fecha límite antes de
?associated_account=1                       -> Cuenta asociada específica
?bank=BCP                                   -> Banco de cuenta asociada
?min_progress=25                            -> Progreso % mínimo
?max_progress=75                            -> Progreso % máximo
?days_remaining_less_than=30               -> Días restantes menor a
?days_remaining_more_than=90               -> Días restantes mayor a
?is_overdue=true                           -> Solo metas vencidas
?has_contributions=true                     -> Con/sin contribuciones
?is_on_track=false                         -> En buen/mal camino
?enable_reminders=true                      -> Con recordatorios activos
?related_category=5                         -> Categoría específica relacionada

--- FILTROS PARA CONTRIBUCIONES (/api/goal-contributions/) ---
?goal=1                                     -> Meta específica
?goal_title=vacaciones                      -> Título de meta
?from_account=2                             -> Cuenta origen específica
?bank=BBVA                                  -> Banco de cuenta origen
?min_amount=100                             -> Monto mínimo
?max_amount=500                             -> Monto máximo
?date_after=2024-01-01                     -> Fecha después de
?date_before=2024-12-31                    -> Fecha antes de
?year=2024                                  -> Año específico
?month=12                                   -> Mes específico
?contribution_type=automatic                -> Tipo de contribución
?is_recurring=true                          -> Solo contribuciones recurrentes
?has_transaction=false                      -> Con/sin transacción relacionada
?notes=navidad                              -> Buscar en notas

--- FILTROS PARA CALENDARIO (/api/goals-calendar/) ---
?year=2024                                  -> Año del calendario
?month=12                                   -> Mes del calendario

============= 📊 EJEMPLOS DE USO =============

# Metas activas próximas a vencer
GET /api/goals/?status=active&days_remaining_less_than=30

# Metas de ahorro con buen progreso  
GET /api/goals/?goal_type=savings&min_progress=70

# Contribuciones automáticas del último trimestre
GET /api/goal-contributions/?contribution_type=automatic&date_after=2024-10-01

# Dashboard completo de metas
GET /api/goals/dashboard/

# Plantillas de metas de emergencia
GET /api/goal-templates/?goal_type=emergency_fund

# Calendario de diciembre 2024
GET /api/goals-calendar/?year=2024&month=12

# Insights inteligentes
GET /api/goals-insights/

============= ⚡ RESPUESTAS IMPORTANTES =============

Dashboard incluye:
- Resumen estadístico completo
- Metas recientes, urgentes y destacadas  
- Gráficos de progreso mensual y por tipo
- Métricas de contribuciones

Analytics por meta incluye:
- Tendencia de progreso histórico
- Contribuciones mensuales detalladas
- Fecha proyectada de completación
- Indicador si está en buen camino
- Recomendaciones de contribución mensual

Insights incluye:
- Alertas de metas vencidas
- Detección de progreso lento
- Celebración de metas casi completas
- Sugerencias de nuevas metas
"""