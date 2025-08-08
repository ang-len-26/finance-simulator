import django_filters
from django.db.models import Q

from .models import  Account

# =====================================================
# Filtro adicional para cuentas
# =====================================================
class AccountFilter(django_filters.FilterSet):
    name = django_filters.CharFilter(
        field_name="name",
        lookup_expr='icontains',
        label="Nombre de cuenta"
    )
    
    bank_name = django_filters.CharFilter(
        field_name="bank_name",
        lookup_expr='icontains',
        label="Banco"
    )
    
    account_type = django_filters.ChoiceFilter(
        field_name="account_type",
        choices=Account.ACCOUNT_TYPES,
        label="Tipo de cuenta"
    )
    
    min_balance = django_filters.NumberFilter(
        field_name="current_balance",
        lookup_expr='gte',
        label="Balance mínimo"
    )
    
    max_balance = django_filters.NumberFilter(
        field_name="current_balance",
        lookup_expr='lte',
        label="Balance máximo"
    )
    
    is_active = django_filters.BooleanFilter(
        field_name="is_active",
        label="Cuenta activa"
    )
    
    include_in_reports = django_filters.BooleanFilter(
        field_name="include_in_reports",
        label="Incluir en reportes"
    )
    
    currency = django_filters.CharFilter(
        field_name="currency",
        lookup_expr='iexact',
        label="Moneda"
    )
    
    has_transactions = django_filters.BooleanFilter(
        method='filter_has_transactions',
        label="Tiene transacciones"
    )
    
    class Meta:
        model = Account
        fields = [
            'name', 'bank_name', 'account_type', 'min_balance', 'max_balance',
            'is_active', 'include_in_reports', 'currency', 'has_transactions'
        ]
    
    def filter_has_transactions(self, queryset, name, value):
        """Filtrar cuentas que tienen/no tienen transacciones"""
        if value is True:
            return queryset.filter(
                Q(outgoing_transactions__isnull=False) |
                Q(incoming_transactions__isnull=False)
            ).distinct()
        elif value is False:
            return queryset.filter(
                outgoing_transactions__isnull=True,
                incoming_transactions__isnull=True
            )
        return queryset
