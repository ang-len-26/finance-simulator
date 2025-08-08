from datetime import timedelta
from rest_framework import serializers

from .models import BudgetAlert, CategorySummary, FinancialMetric

# =====================================================
# SERIALIZERS PARA MÉTRICAS FINANCIERAS
# =====================================================
class FinancialMetricSerializer(serializers.ModelSerializer):
    period_label = serializers.SerializerMethodField()
    
    class Meta:
        model = FinancialMetric
        fields = [
            'id', 'period_type', 'period_start', 'period_end', 'period_label',
            'total_income', 'total_expenses', 'net_balance',
            'checking_balance', 'savings_balance', 'investment_balance', 'credit_balance',
            'transaction_count', 'top_expense_category', 'top_expense_amount',
            'calculated_at'
        ]
    
    def get_period_label(self, obj):
        """Etiqueta legible del período"""
        if obj.period_type == 'monthly':
            return obj.period_start.strftime('%B %Y')
        elif obj.period_type == 'quarterly':
            quarter = (obj.period_start.month - 1) // 3 + 1
            return f"Q{quarter} {obj.period_start.year}"
        elif obj.period_type == 'yearly':
            return str(obj.period_start.year)
        else:
            return f"{obj.period_start} - {obj.period_end}"

# =====================================================
# SERIALIZERS PARA RESUMEN DE CATEGORÍAS
# =====================================================
class CategorySummaryReportSerializer(serializers.ModelSerializer):
    category_name = serializers.CharField(source='category.name', read_only=True)
    category_icon = serializers.CharField(source='category.icon', read_only=True)
    category_color = serializers.CharField(source='category.color', read_only=True)
    most_used_account_name = serializers.CharField(source='most_used_account.name', read_only=True)
    
    class Meta:
        model = CategorySummary
        fields = [
            'id', 'category_name', 'category_icon', 'category_color',
            'period_start', 'period_end', 'period_type',
            'total_amount', 'transaction_count', 'average_amount',
            'previous_period_amount', 'percentage_change',
            'most_used_account_name'
        ]

# =====================================================
# SERIALIZERS PARA ALERTAS DE PRESUPUESTO
# =====================================================
class BudgetAlertSerializer(serializers.ModelSerializer):
    related_transaction_title = serializers.CharField(source='related_transaction.title', read_only=True)
    related_category_name = serializers.CharField(source='related_category.name', read_only=True)
    related_account_name = serializers.CharField(source='related_account.name', read_only=True)
    severity_label = serializers.SerializerMethodField()
    alert_type_label = serializers.SerializerMethodField()
    
    class Meta:
        model = BudgetAlert
        fields = [
            'id', 'alert_type', 'alert_type_label', 'severity', 'severity_label',
            'title', 'message', 'threshold_amount', 'actual_amount',
            'related_transaction_title', 'related_category_name', 'related_account_name',
            'is_read', 'is_dismissed', 'created_at'
        ]
    
    def get_severity_label(self, obj):
        return dict(BudgetAlert.SEVERITY_LEVELS).get(obj.severity, obj.severity)
    
    def get_alert_type_label(self, obj):
        return dict(BudgetAlert.ALERT_TYPES).get(obj.alert_type, obj.alert_type)

# =====================================================
# SERIALIZERS PARA REPORTES AVANZADOS
# =====================================================
class ReportMetricsSerializer(serializers.Serializer):
    """Serializer para métricas de reportes"""
    total_income = serializers.DecimalField(max_digits=15, decimal_places=2)
    total_expenses = serializers.DecimalField(max_digits=15, decimal_places=2)
    net_balance = serializers.DecimalField(max_digits=15, decimal_places=2)
    transaction_count = serializers.IntegerField()
    income_change = serializers.FloatField()
    expense_change = serializers.FloatField()

# =====================================================
# SERIALIZERS PARA GRÁFICOS Y DATOS DE REPORTES
# =====================================================
class ChartDataSerializer(serializers.Serializer):
    """Serializer para datos de gráficos Chart.js"""
    labels = serializers.ListField(child=serializers.CharField())
    datasets = serializers.ListField(child=serializers.DictField())

# =====================================================
# SERIALIZERS PARA REPORTES ESPECÍFICOS
# =====================================================
class TopCategorySerializer(serializers.Serializer):
    """Serializer para top categorías con comparativas"""
    name = serializers.CharField()
    icon = serializers.CharField()
    color = serializers.CharField()
    current_amount = serializers.DecimalField(max_digits=15, decimal_places=2)
    previous_amount = serializers.DecimalField(max_digits=15, decimal_places=2)
    change_percentage = serializers.FloatField()
    transaction_count = serializers.IntegerField()
    average_amount = serializers.DecimalField(max_digits=15, decimal_places=2)

# =====================================================
# SERIALIZERS PARA REPORTES DE TRANSACCIONES RECIENTES
# =====================================================
class RecentTransactionSerializer(serializers.Serializer):
    """Serializer para transacciones recientes en reportes"""
    id = serializers.IntegerField()
    title = serializers.CharField()
    amount = serializers.DecimalField(max_digits=15, decimal_places=2)
    type = serializers.CharField()
    date = serializers.CharField()
    icon = serializers.CharField()
    from_account = serializers.CharField(allow_null=True)
    to_account = serializers.CharField(allow_null=True)
    category = serializers.CharField(allow_null=True)
    is_positive = serializers.BooleanField()

# =====================================================
# SERIALIZERS PARA RATIOS FINANCIEROS
# =====================================================
class FinancialRatiosSerializer(serializers.Serializer):
    """Serializer para ratios financieros"""
    savings_rate = serializers.FloatField()
    expense_ratio = serializers.FloatField()
    investment_rate = serializers.FloatField()
    net_worth_change = serializers.FloatField()

# =====================================================
# SERIALIZER PARA VISTA DE REPORTES COMPLETA
# ====================================================  
class ReportsOverviewSerializer(serializers.Serializer):
    """Serializer completo para la vista de reportes"""
    metrics = ReportMetricsSerializer()
    period = serializers.DictField()
    charts = serializers.DictField()
    insights = serializers.DictField()
    
class FinancialMetricComparisonSerializer(serializers.ModelSerializer):
    """Serializer con comparativas entre períodos"""
    period_label = serializers.SerializerMethodField()
    savings_rate = serializers.ReadOnlyField()
    expense_ratio = serializers.ReadOnlyField()
    previous_period_comparison = serializers.SerializerMethodField()
    
    class Meta:
        model = FinancialMetric
        fields = [
            'id', 'period_type', 'period_start', 'period_end', 'period_label',
            'total_income', 'total_expenses', 'net_balance', 'savings_rate', 'expense_ratio',
            'checking_balance', 'savings_balance', 'investment_balance', 'credit_balance',
            'transaction_count', 'top_expense_category', 'top_expense_amount',
            'previous_period_comparison', 'calculated_at'
        ]
    
    def get_period_label(self, obj):
        """Etiqueta legible del período"""
        if obj.period_type == 'monthly':
            return obj.period_start.strftime('%B %Y')
        elif obj.period_type == 'quarterly':
            quarter = (obj.period_start.month - 1) // 3 + 1
            return f"Q{quarter} {obj.period_start.year}"
        elif obj.period_type == 'yearly':
            return str(obj.period_start.year)
        else:
            return f"{obj.period_start} - {obj.period_end}"
    
    def get_previous_period_comparison(self, obj):
        """Comparación con período anterior"""
        try:
            # Buscar período anterior
            period_length = (obj.period_end - obj.period_start).days
            prev_start = obj.period_start - timedelta(days=period_length)
            prev_end = obj.period_start - timedelta(days=1)
            
            previous = FinancialMetric.objects.filter(
                user=obj.user,
                period_type=obj.period_type,
                period_start=prev_start,
                period_end=prev_end
            ).first()
            
            if previous:
                def calc_change(current, prev):
                    if prev == 0:
                        return 0 if current == 0 else 100
                    return float(((current - prev) / prev) * 100)
                
                return {
                    'income_change': round(calc_change(obj.total_income, previous.total_income), 2),
                    'expense_change': round(calc_change(obj.total_expenses, previous.total_expenses), 2),
                    'balance_change': round(calc_change(obj.net_balance, previous.net_balance), 2),
                    'previous_period': {
                        'total_income': float(previous.total_income),
                        'total_expenses': float(previous.total_expenses),
                        'net_balance': float(previous.net_balance)
                    }
                }
        except:
            pass
        
        return None
 
class BudgetAlertDetailSerializer(serializers.ModelSerializer):
    """Serializer detallado para alertas con relaciones completas"""
    related_transaction_details = serializers.SerializerMethodField()
    related_category_details = serializers.SerializerMethodField()
    related_account_details = serializers.SerializerMethodField()
    severity_label = serializers.SerializerMethodField()
    alert_type_label = serializers.SerializerMethodField()
    days_since_created = serializers.ReadOnlyField()
    is_active = serializers.ReadOnlyField()
    
    class Meta:
        model = BudgetAlert
        fields = '__all__'
    
    def get_related_transaction_details(self, obj):
        if obj.related_transaction:
            return {
                'id': obj.related_transaction.id,
                'title': obj.related_transaction.title,
                'amount': obj.related_transaction.amount,
                'date': obj.related_transaction.date
            }
        return None
    
    def get_related_category_details(self, obj):
        if obj.related_category:
            return {
                'name': obj.related_category.name,
                'icon': obj.related_category.icon,
                'color': obj.related_category.color
            }
        return None
    
    def get_related_account_details(self, obj):
        if obj.related_account:
            return {
                'name': obj.related_account.name,
                'account_type': obj.related_account.account_type,
                'current_balance': obj.related_account.current_balance
            }
        return None
    
    def get_severity_label(self, obj):
        return dict(BudgetAlert.SEVERITY_LEVELS).get(obj.severity, obj.severity)
    
    def get_alert_type_label(self, obj):
        return dict(BudgetAlert.ALERT_TYPES).get(obj.alert_type, obj.alert_type)
