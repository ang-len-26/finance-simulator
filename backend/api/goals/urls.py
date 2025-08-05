from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import FinancialGoalViewSet, GoalContributionViewSet, GoalTemplateViewSet, create_goal_templates, goals_calendar, goals_insights
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
ENDPOINTS

============= 🎯 METAS (FinancialGoalViewSet) =============
GET    /api/goals/		                   -> Listar metas
POST   /api/goals/		                   -> Crear nueva meta
GET    /api/goals/{id}/                    -> Obtener meta específica
PUT    /api/goals/{id}/                    -> Actualizar meta completa
PATCH  /api/goals/{id}/                    -> Actualizar meta parcialmente
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

============= 💰 APORTES (GoalContributionViewSet) =============
GET    /api/goal-contributions/                     -> Listar aportes
POST   /api/goal-contributions/                     -> Crear nuevo aporte
GET    /api/goal-contributions/{id}/                -> Obtener aporte específico
PUT    /api/goal-contributions/{id}/                -> Actualizar aporte completo
PATCH  /api/goal-contributions/{id}/                -> Actualizar aporte parcialmente
DELETE /api/goal-contributions/{id}/                -> Eliminar aporte

============= 🏷️ PLANTILLAS (GoalTemplateViewSet) =============
GET    /api/goal-templates/                     -> Listar plantillas
POST   /api/goal-templates/                     -> Crear nueva plantilla
GET    /api/goal-templates/{id}/                -> Obtener plantilla específica
PUT    /api/goal-templates/{id}/                -> Actualizar plantilla completa
PATCH  /api/goal-templates/{id}/                -> Actualizar plantilla parcialmente
DELETE /api/goal-templates/{id}/                -> Eliminar plantilla
POST   /api/goal-templates/{id}/create_goal/ 	-> Crear meta desde plantilla
GET    /api/goal-templates/by_category/    		-> Plantillas por categoría

============= 🔍 FILTROS DISPONIBLES =============
- ?status=active,completed                 -> Estado meta
- ?goal_type=savings,emergency_fund        -> Tipo meta
- ?priority=high,medium,low                -> Prioridad


"""