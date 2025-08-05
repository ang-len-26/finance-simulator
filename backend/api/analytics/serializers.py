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
 