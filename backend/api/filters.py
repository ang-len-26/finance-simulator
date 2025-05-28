import django_filters
from .models import Transaction

class TransactionFilter(django_filters.FilterSet):
    min_amount = django_filters.NumberFilter(field_name="amount", lookup_expr='gte')
    max_amount = django_filters.NumberFilter(field_name="amount", lookup_expr='lte')
    type = django_filters.CharFilter(field_name="type", lookup_expr='iexact')
    description = django_filters.CharFilter(field_name="description", lookup_expr='icontains')
    created_at = django_filters.DateFromToRangeFilter(field_name="created_at")  # Rango de fechas

    class Meta:
        model = Transaction
        fields = ['type', 'min_amount', 'max_amount', 'description', 'created_at']
