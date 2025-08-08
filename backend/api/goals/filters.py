import django_filters

from .models import FinancialGoal, GoalContribution

# =====================================================
# Filtros avanzados para metas financieras
# =====================================================
class FinancialGoalFilter(django_filters.FilterSet):
    """Filtros avanzados para metas financieras"""
    
    # Filtros de texto
    title = django_filters.CharFilter(lookup_expr='icontains', help_text="Buscar en título")
    description = django_filters.CharFilter(lookup_expr='icontains', help_text="Buscar en descripción")
    
    # Filtros de selección
    goal_type = django_filters.ChoiceFilter(choices=FinancialGoal.GOAL_TYPES)
    status = django_filters.ChoiceFilter(choices=FinancialGoal.GOAL_STATUS)
    priority = django_filters.ChoiceFilter(choices=FinancialGoal.PRIORITY_LEVELS)
    
    # Filtros de rango de montos
    min_target_amount = django_filters.NumberFilter(field_name='target_amount', lookup_expr='gte')
    max_target_amount = django_filters.NumberFilter(field_name='target_amount', lookup_expr='lte')
    min_current_amount = django_filters.NumberFilter(field_name='current_amount', lookup_expr='gte')
    max_current_amount = django_filters.NumberFilter(field_name='current_amount', lookup_expr='lte')
    
    # Filtros de fechas
    start_date_after = django_filters.DateFilter(field_name='start_date', lookup_expr='gte')
    start_date_before = django_filters.DateFilter(field_name='start_date', lookup_expr='lte')
    target_date_after = django_filters.DateFilter(field_name='target_date', lookup_expr='gte')
    target_date_before = django_filters.DateFilter(field_name='target_date', lookup_expr='lte')
    
    # Filtros de relaciones
    associated_account = django_filters.NumberFilter(field_name='associated_account__id')
    bank = django_filters.CharFilter(field_name='associated_account__bank_name', lookup_expr='icontains')
    
    # Filtros de progreso
    min_progress = django_filters.NumberFilter(method='filter_min_progress')
    max_progress = django_filters.NumberFilter(method='filter_max_progress')
    
    # Filtros de tiempo restante
    days_remaining_less_than = django_filters.NumberFilter(method='filter_days_remaining_less')
    days_remaining_more_than = django_filters.NumberFilter(method='filter_days_remaining_more')
    
    # Filtros booleanos
    is_overdue = django_filters.BooleanFilter(method='filter_is_overdue')
    has_contributions = django_filters.BooleanFilter(method='filter_has_contributions')
    is_on_track = django_filters.BooleanFilter(method='filter_is_on_track')
    enable_reminders = django_filters.BooleanFilter()
    
    # Filtros de categorías relacionadas
    related_category = django_filters.NumberFilter(field_name='related_categories__id')
    
    class Meta:
        model = FinancialGoal
        fields = []  # Todos los filtros están definidos explícitamente arriba
    
    def filter_min_progress(self, queryset, name, value):
        """Filtrar por progreso mínimo"""
        if value is not None:
            # Filtrar metas donde current_amount/target_amount >= value/100
            
            filtered_ids = []
            for goal in queryset:
                if goal.progress_percentage >= value:
                    filtered_ids.append(goal.id)
            
            return queryset.filter(id__in=filtered_ids)
        return queryset
    
    def filter_max_progress(self, queryset, name, value):
        """Filtrar por progreso máximo"""
        if value is not None:
            filtered_ids = []
            for goal in queryset:
                if goal.progress_percentage <= value:
                    filtered_ids.append(goal.id)
            
            return queryset.filter(id__in=filtered_ids)
        return queryset
    
    def filter_days_remaining_less(self, queryset, name, value):
        """Filtrar metas con menos de X días restantes"""
        if value is not None:
            filtered_ids = []
            for goal in queryset:
                if goal.days_remaining <= value:
                    filtered_ids.append(goal.id)
            
            return queryset.filter(id__in=filtered_ids)
        return queryset
    
    def filter_days_remaining_more(self, queryset, name, value):
        """Filtrar metas con más de X días restantes"""
        if value is not None:
            filtered_ids = []
            for goal in queryset:
                if goal.days_remaining >= value:
                    filtered_ids.append(goal.id)
            
            return queryset.filter(id__in=filtered_ids)
        return queryset
    
    def filter_is_overdue(self, queryset, name, value):
        """Filtrar metas vencidas"""
        if value is not None:
            filtered_ids = []
            for goal in queryset:
                if goal.is_overdue == value:
                    filtered_ids.append(goal.id)
            
            return queryset.filter(id__in=filtered_ids)
        return queryset
    
    def filter_has_contributions(self, queryset, name, value):
        """Filtrar metas que tienen/no tienen contribuciones"""
        if value is True:
            return queryset.filter(contributions__isnull=False).distinct()
        elif value is False:
            return queryset.filter(contributions__isnull=True)
        return queryset
    
    def filter_is_on_track(self, queryset, name, value):
        """Filtrar metas que están/no están en buen camino"""
        if value is not None:
            filtered_ids = []
            for goal in queryset:
                # Lógica simple: si tiene más del 50% de progreso, está en buen camino
                is_on_track = goal.progress_percentage >= 50
                if is_on_track == value:
                    filtered_ids.append(goal.id)
            
            return queryset.filter(id__in=filtered_ids)
        return queryset

# =====================================================
# Filtros avanzados para contribuciones de metas
# =====================================================
class GoalContributionFilter(django_filters.FilterSet):
    """Filtros para contribuciones de metas"""
    
    # Filtros de relaciones
    goal = django_filters.NumberFilter(field_name='goal__id')
    goal_title = django_filters.CharFilter(field_name='goal__title', lookup_expr='icontains')
    from_account = django_filters.NumberFilter(field_name='from_account__id')
    bank = django_filters.CharFilter(field_name='from_account__bank_name', lookup_expr='icontains')
    
    # Filtros de montos
    min_amount = django_filters.NumberFilter(field_name='amount', lookup_expr='gte')
    max_amount = django_filters.NumberFilter(field_name='amount', lookup_expr='lte')
    
    # Filtros de fechas
    date_after = django_filters.DateFilter(field_name='date', lookup_expr='gte')
    date_before = django_filters.DateFilter(field_name='date', lookup_expr='lte')
    
    # Filtro por mes/año específico
    year = django_filters.NumberFilter(field_name='date__year')
    month = django_filters.NumberFilter(field_name='date__month')
    
    # Filtros de tipo
    contribution_type = django_filters.ChoiceFilter(choices=GoalContribution.CONTRIBUTION_TYPES)
    
    # Filtros booleanos
    is_recurring = django_filters.BooleanFilter()
    has_transaction = django_filters.BooleanFilter(method='filter_has_transaction')
    
    # Filtro de búsqueda en notas
    notes = django_filters.CharFilter(lookup_expr='icontains')
    
    class Meta:
        model = GoalContribution
        fields = []
    
    def filter_has_transaction(self, queryset, name, value):
        """Filtrar contribuciones que tienen/no tienen transacción relacionada"""
        if value is True:
            return queryset.filter(related_transaction__isnull=False)
        elif value is False:
            return queryset.filter(related_transaction__isnull=True)
        return queryset


# =====================================================
# EJEMPLOS DE USO DE FILTROS
# =====================================================

# Ejemplos de URLs con filtros para metas:
# GET /api/goals/?status=active&goal_type=savings
# GET /api/goals/?min_progress=50&max_progress=90
# GET /api/goals/?days_remaining_less_than=30
# GET /api/goals/?is_overdue=true
# GET /api/goals/?min_target_amount=1000&max_target_amount=10000
# GET /api/goals/?title=vacaciones&priority=high
# GET /api/goals/?target_date_after=2024-01-01&target_date_before=2024-12-31
# GET /api/goals/?bank=BCP&has_contributions=true
# GET /api/goals/?is_on_track=false&enable_reminders=true

# Ejemplos de URLs con filtros para contribuciones:
# GET /api/goal-contributions/?goal=1&month=12&year=2024
# GET /api/goal-contributions/?min_amount=100&max_amount=500
# GET /api/goal-contributions/?date_after=2024-01-01&contribution_type=automatic
# GET /api/goal-contributions/?bank=BBVA&is_recurring=true
# GET /api/goal-contributions/?goal_title=vacaciones&has_transaction=false
# GET /api/goal-contributions/?notes=navidad&date_before=2024-12-25