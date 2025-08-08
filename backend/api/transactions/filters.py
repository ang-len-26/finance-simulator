import django_filters
from django.db.models import Q

from ..accounts.models import Account
from .models import Transaction

# =====================================================
# Filtros avanzados para transacciones
# =====================================================
class TransactionFilter(django_filters.FilterSet):
    # Filtros existentes
    min_amount = django_filters.NumberFilter(field_name="amount", lookup_expr='gte')
    max_amount = django_filters.NumberFilter(field_name="amount", lookup_expr='lte')
    type = django_filters.CharFilter(field_name="type", lookup_expr='iexact')
    description = django_filters.CharFilter(field_name="description", lookup_expr='icontains')
    date = django_filters.DateFromToRangeFilter(field_name="date")
    
    # NUEVOS FILTROS: Sistema de cuentas
    from_account = django_filters.ModelChoiceFilter(
        field_name='from_account',
        queryset=None,  # Se define dinámicamente en __init__
        to_field_name='id',
        empty_label="Todas las cuentas origen"
    )
    
    to_account = django_filters.ModelChoiceFilter(
        field_name='to_account',
        queryset=None,  # Se define dinámicamente en __init__
        to_field_name='id',
        empty_label="Todas las cuentas destino"
    )
    
    account = django_filters.ModelChoiceFilter(
        method='filter_by_account',
        queryset=None,  # Se define dinámicamente en __init__
        to_field_name='id',
        label="Cualquier cuenta (origen o destino)"
    )
    
    bank = django_filters.CharFilter(
        method='filter_by_bank',
        label="Banco"
    )
    
    account_type = django_filters.ChoiceFilter(
        method='filter_by_account_type',
        choices=Account.ACCOUNT_TYPES,
        label="Tipo de cuenta"
    )
    
    # Filtros adicionales avanzados
    has_reference = django_filters.BooleanFilter(
        method='filter_has_reference',
        label="Tiene número de referencia"
    )
    
    location = django_filters.CharFilter(
        field_name="location",
        lookup_expr='icontains',
        label="Ubicación"
    )
    
    tags = django_filters.CharFilter(
        method='filter_by_tags',
        label="Etiquetas (separadas por coma)"
    )
    
    is_recurring = django_filters.BooleanFilter(
        field_name="is_recurring",
        label="Es recurrente"
    )
    
    recurring_frequency = django_filters.ChoiceFilter(
        field_name="recurring_frequency",
        choices=[
            ('daily', 'Diario'),
            ('weekly', 'Semanal'), 
            ('monthly', 'Mensual'),
            ('quarterly', 'Trimestral'),
            ('yearly', 'Anual')
        ],
        label="Frecuencia recurrente"
    )
    
    # Filtros de flujo de efectivo
    cash_flow = django_filters.ChoiceFilter(
        method='filter_cash_flow',
        choices=[
            ('positive', 'Entradas de dinero'),
            ('negative', 'Salidas de dinero'),
            ('internal', 'Movimientos internos')
        ],
        label="Flujo de efectivo"
    )
    
    class Meta:
        model = Transaction
        fields = [
            'type', 'min_amount', 'max_amount', 'description', 'date',
            'from_account', 'to_account', 'account', 'bank', 'account_type',
            'has_reference', 'location', 'tags', 'is_recurring', 
            'recurring_frequency', 'cash_flow'
        ]
    
    def __init__(self, *args, **kwargs):
        """Inicializar queryset de cuentas basado en el usuario"""
        super().__init__(*args, **kwargs)
        
        # Obtener usuario de la request
        if hasattr(self, 'request') and self.request.user.is_authenticated:
            user_accounts = Account.objects.filter(user=self.request.user, is_active=True)
            
            # Configurar queryset para filtros de cuentas
            self.filters['from_account'].queryset = user_accounts
            self.filters['to_account'].queryset = user_accounts
            self.filters['account'].queryset = user_accounts
    
    def filter_by_account(self, queryset, name, value):
        """Filtrar por cualquier cuenta (origen o destino)"""
        if value:
            return queryset.filter(
                Q(from_account=value) | Q(to_account=value)
            )
        return queryset
    
    def filter_by_bank(self, queryset, name, value):
        """Filtrar por banco (en cualquier cuenta)"""
        if value:
            return queryset.filter(
                Q(from_account__bank_name__icontains=value) |
                Q(to_account__bank_name__icontains=value)
            )
        return queryset
    
    def filter_by_account_type(self, queryset, name, value):
        """Filtrar por tipo de cuenta"""
        if value:
            return queryset.filter(
                Q(from_account__account_type=value) |
                Q(to_account__account_type=value)
            )
        return queryset
    
    def filter_has_reference(self, queryset, name, value):
        """Filtrar transacciones con/sin número de referencia"""
        if value is True:
            return queryset.exclude(reference_number='')
        elif value is False:
            return queryset.filter(reference_number='')
        return queryset
    
    def filter_by_tags(self, queryset, name, value):
        """Filtrar por etiquetas (buscar en array JSON)"""
        if value:
            tags = [tag.strip() for tag in value.split(',')]
            query = Q()
            for tag in tags:
                query |= Q(tags__contains=[tag])
            return queryset.filter(query)
        return queryset
    
    def filter_cash_flow(self, queryset, name, value):
        """Filtrar por tipo de flujo de efectivo"""
        if value == 'positive':
            # Entradas: ingresos y préstamos recibidos
            return queryset.filter(type__in=['income', 'loan'])
        elif value == 'negative':
            # Salidas: gastos, inversiones, pagos de deuda, ahorros
            return queryset.filter(type__in=['expense', 'investment', 'debt', 'savings'])
        elif value == 'internal':
            # Movimientos internos: transferencias
            return queryset.filter(type='transfer')
        return queryset
