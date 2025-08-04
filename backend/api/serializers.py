from rest_framework import serializers
from django.db import models
from django.db.models import Sum
from decimal import Decimal
from django.utils import timezone
from datetime import timedelta
from .models import Transaction, Account, Category, FinancialMetric, CategorySummary, BudgetAlert, FinancialGoal, GoalContribution, GoalMilestone, GoalTemplate

# =====================================================
# SERIALIZERS PARA CUENTAS
# =====================================================
class AccountSerializer(serializers.ModelSerializer):
    current_balance = serializers.DecimalField(max_digits=12, decimal_places=2, read_only=True)
    transaction_count = serializers.SerializerMethodField()
    last_transaction_date = serializers.SerializerMethodField()
    
    class Meta:
        model = Account
        fields = [
            'id', 'name', 'bank_name', 'account_number', 'account_type',
            'initial_balance', 'current_balance', 'currency', 'is_active',
            'include_in_reports', 'transaction_count', 'last_transaction_date',
            'created_at', 'updated_at'
        ]
        read_only_fields = ['current_balance', 'created_at', 'updated_at']
    
    def get_transaction_count(self, obj):
        """Número total de transacciones de esta cuenta"""
        return Transaction.objects.filter(
            models.Q(from_account=obj) | models.Q(to_account=obj)
        ).count()
    
    def get_last_transaction_date(self, obj):
        """Fecha de la última transacción"""
        last_transaction = Transaction.objects.filter(
            models.Q(from_account=obj) | models.Q(to_account=obj)
        ).order_by('-date').first()
        
        return last_transaction.date if last_transaction else None
    
    def validate_name(self, value):
        """Validar que el nombre de cuenta sea único por usuario"""
        user = self.context['request'].user
        
        # Si es actualización, excluir la cuenta actual
        if self.instance:
            existing = Account.objects.filter(
                user=user, name=value
            ).exclude(pk=self.instance.pk)
        else:
            existing = Account.objects.filter(user=user, name=value)
        
        if existing.exists():
            raise serializers.ValidationError("Ya tienes una cuenta con este nombre.")
        return value
    
    def validate_initial_balance(self, value):
        """Validar balance inicial"""
        if value < 0:
            raise serializers.ValidationError("El balance inicial no puede ser negativo.")
        return value

# =====================================================
# SERIALIZERS PARA LISTADOS DE CUENTAS
# =====================================================
class AccountSummarySerializer(serializers.ModelSerializer):
    """Serializer ligero para listados"""
    class Meta:
        model = Account
        fields = ['id', 'name', 'bank_name', 'account_type', 'current_balance', 'currency']

# =====================================================
# SERIALIZERS PARA TRANSACCIONES
# =====================================================
class TransactionSerializer(serializers.ModelSerializer):
    from_account_name = serializers.CharField(source='from_account.name', read_only=True)
    to_account_name = serializers.CharField(source='to_account.name', read_only=True)
    category_name = serializers.CharField(source='category.name', read_only=True)  # NUEVO
    category_icon = serializers.CharField(source='category.icon', read_only=True)  # NUEVO
    category_color = serializers.CharField(source='category.color', read_only=True)  # NUEVO
    
    class Meta:
        model = Transaction
        fields = [
            'id', 'title', 'amount', 'type', 'date', 'description',
            'from_account', 'to_account', 'from_account_name', 'to_account_name',
            'category', 'category_name', 'category_icon', 'category_color',  # NUEVO
            'reference_number', 'location', 'tags', 'is_recurring', 
            'recurring_frequency', 'parent_transaction', 'created_at', 'updated_at'
        ]
        read_only_fields = ['created_at', 'updated_at']
    
    def validate_amount(self, value):
        """Validar monto"""
        if value <= 0:
            raise serializers.ValidationError("El monto debe ser mayor que cero.")
        return value
    
    def validate_type(self, value):
        """Validar tipo de transacción"""
        if value not in dict(Transaction.TRANSACTION_TYPES):
            raise serializers.ValidationError("Tipo de transacción inválido.")
        return value
    
    def validate_from_account(self, value):
        """Validar que la cuenta pertenezca al usuario"""
        if value and value.user != self.context['request'].user:
            raise serializers.ValidationError("La cuenta de origen no te pertenece.")
        return value
    
    def validate_to_account(self, value):
        """Validar cuenta destino si existe"""
        if value and value.user != self.context['request'].user:
            raise serializers.ValidationError("La cuenta destino no te pertenece.")
        return value
    
    def validate_category(self, value):
        """Validar que la categoría sea apropiada para el tipo de transacción"""
        if value:
            # Verificar que la categoría esté activa
            if not value.is_active:
                raise serializers.ValidationError("Esta categoría no está disponible.")
        return value
    
    def validate(self, data):
        """Validaciones complejas"""
        transaction_type = data.get('type')
        from_account = data.get('from_account')
        to_account = data.get('to_account')
        amount = data.get('amount', 0)
        category = data.get('category')
        
        # Validar compatibilidad categoría-tipo
        if category:
            if transaction_type == 'income' and category.category_type == 'expense':
                raise serializers.ValidationError("No puedes asignar una categoría de gasto a un ingreso.")
            elif transaction_type == 'expense' and category.category_type == 'income':
                raise serializers.ValidationError("No puedes asignar una categoría de ingreso a un gasto.")
        
        # Validaciones por tipo de transacción (las mismas de antes)
        if transaction_type == 'transfer':
            if not to_account:
                raise serializers.ValidationError("Las transferencias requieren cuenta destino.")
            if from_account == to_account:
                raise serializers.ValidationError("No puedes transferir a la misma cuenta.")
        
        elif transaction_type == 'income':
            if not to_account:
                raise serializers.ValidationError("Los ingresos requieren cuenta destino.")
        
        elif transaction_type in ['expense', 'investment', 'loan', 'debt', 'savings']:
            if not from_account:
                raise serializers.ValidationError(f"{transaction_type.title()} requiere cuenta de origen.")
        
        # Validaciones de negocio (las mismas de antes)
        if transaction_type == 'investment' and amount < 100:
            raise serializers.ValidationError("Las inversiones deben ser de al menos $100.")
        
        if transaction_type == 'loan' and amount > 10000:
            raise serializers.ValidationError("Los préstamos no pueden exceder $10,000.")
        
        if transaction_type == 'expense' and amount > 5000:
            raise serializers.ValidationError("Los gastos no pueden exceder $5,000.")
        
        return data

# =====================================================
# SERIALIZERS PARA LISTADOS Y REPORTES DE TRANSACCIONES
# =====================================================
class TransactionSummarySerializer(serializers.ModelSerializer):
    """Serializer ligero para listados y reportes"""
    from_account_name = serializers.CharField(source='from_account.name', read_only=True)
    to_account_name = serializers.CharField(source='to_account.name', read_only=True)
    category_name = serializers.CharField(source='category.name', read_only=True)  # NUEVO
    category_icon = serializers.CharField(source='category.icon', read_only=True)  # NUEVO
    category_color = serializers.CharField(source='category.color', read_only=True)  # NUEVO
    is_positive = serializers.SerializerMethodField()  # NUEVO
    
    class Meta:
        model = Transaction
        fields = [
            'id', 'title', 'amount', 'type', 'date', 
            'from_account_name', 'to_account_name',
            'category_name', 'category_icon', 'category_color', 'is_positive'  # NUEVO
        ]
    
    def get_is_positive(self, obj):
        """Determinar si es ingreso (positivo) o gasto (negativo)"""
        return obj.type == 'income'
       
# =====================================================
# SERIALIZERS PARA ANÁLISIS FINANCIERO
# =====================================================
class CategorySerializer(serializers.ModelSerializer):
    transaction_count = serializers.SerializerMethodField()
    subcategories = serializers.SerializerMethodField()
    parent_name = serializers.CharField(source='parent.name', read_only=True)
    
    class Meta:
        model = Category
        fields = [
            'id', 'name', 'slug', 'icon', 'color', 'category_type',
            'parent', 'parent_name', 'is_active', 'sort_order',
            'transaction_count', 'subcategories', 'created_at', 'updated_at'
        ]
        read_only_fields = ['slug', 'created_at', 'updated_at']
    
    def get_transaction_count(self, obj):
        """Número de transacciones en esta categoría"""
        user = self.context.get('request').user if self.context.get('request') else None
        if user:
            return Transaction.objects.filter(category=obj, user=user).count()
        return 0
    
    def get_subcategories(self, obj):
        """Subcategorías anidadas"""
        if obj.subcategories.exists():
            return CategorySummarySerializer(
                obj.subcategories.filter(is_active=True), 
                many=True, 
                context=self.context
            ).data
        return []
    
    def validate_color(self, value):
        """Validar formato hexadecimal"""
        if not value.startswith('#') or len(value) != 7:
            raise serializers.ValidationError("Color debe estar en formato hexadecimal (#ffffff)")
        return value

# =====================================================
# SERIALIZERS PARA REPORTES FINANCIEROS
# =====================================================    
class CategorySummarySerializer(serializers.ModelSerializer):
    """Serializer ligero para categorías"""
    class Meta:
        model = Category
        fields = ['id', 'name', 'icon', 'color', 'category_type']

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
    
# =====================================================
# SERIALIZERS PARA HITOS DE METAS
# =====================================================
class GoalMilestoneSerializer(serializers.ModelSerializer):
    progress_percentage = serializers.ReadOnlyField()
    
    class Meta:
        model = GoalMilestone
        fields = [
            'id', 'title', 'description', 'target_amount', 'target_date',
            'is_completed', 'completed_at', 'icon', 'order', 'progress_percentage'
        ]

# =====================================================
# SERIALIZERS PARA CONTRIBUCIONES A METAS
# =====================================================
class GoalContributionSerializer(serializers.ModelSerializer):
    from_account_name = serializers.CharField(source='from_account.name', read_only=True)
    related_transaction_title = serializers.CharField(source='related_transaction.title', read_only=True)
    
    class Meta:
        model = GoalContribution
        fields = [
            'id', 'amount', 'contribution_type', 'date', 'from_account', 'from_account_name',
            'related_transaction', 'related_transaction_title', 'notes', 'is_recurring',
            'created_at'
        ]
        read_only_fields = ['created_at']
    
    def validate_amount(self, value):
        if value <= 0:
            raise serializers.ValidationError("El monto debe ser positivo.")
        return value
    
    def validate_from_account(self, value):
        if value.user != self.context['request'].user:
            raise serializers.ValidationError("La cuenta no te pertenece.")
        return value

# =====================================================
# SERIALIZERS PARA METAS FINANCIERAS
# =====================================================
class FinancialGoalSerializer(serializers.ModelSerializer):
    # Campos calculados
    progress_percentage = serializers.ReadOnlyField()
    remaining_amount = serializers.ReadOnlyField()
    days_remaining = serializers.ReadOnlyField()
    is_overdue = serializers.ReadOnlyField()
    suggested_monthly_amount = serializers.ReadOnlyField()
    
    # Relaciones
    associated_account_name = serializers.CharField(source='associated_account.name', read_only=True)
    milestones = GoalMilestoneSerializer(many=True, read_only=True)
    contributions = GoalContributionSerializer(many=True, read_only=True)
    
    # Campos adicionales para el frontend
    goal_type_label = serializers.SerializerMethodField()
    status_label = serializers.SerializerMethodField()
    priority_label = serializers.SerializerMethodField()
    contributions_count = serializers.SerializerMethodField()
    last_contribution_date = serializers.SerializerMethodField()
    
    class Meta:
        model = FinancialGoal
        fields = [
            'id', 'title', 'description', 'goal_type', 'goal_type_label',
            'target_amount', 'current_amount', 'progress_percentage', 'remaining_amount',
            'start_date', 'target_date', 'days_remaining', 'is_overdue',
            'monthly_target', 'auto_contribution', 'suggested_monthly_amount',
            'associated_account', 'associated_account_name', 'related_categories',
            'status', 'status_label', 'priority', 'priority_label', 'is_public',
            'icon', 'color', 'enable_reminders', 'reminder_frequency',
            'milestones', 'contributions', 'contributions_count', 'last_contribution_date',
            'created_at', 'updated_at', 'completed_at'
        ]
        read_only_fields = [
            'current_amount', 'progress_percentage', 'remaining_amount', 
            'days_remaining', 'is_overdue', 'suggested_monthly_amount',
            'created_at', 'updated_at', 'completed_at'
        ]
    
    def get_goal_type_label(self, obj):
        return obj.get_goal_type_display()
    
    def get_status_label(self, obj):
        return obj.get_status_display()
    
    def get_priority_label(self, obj):
        return obj.get_priority_display()
    
    def get_contributions_count(self, obj):
        return obj.contributions.count()
    
    def get_last_contribution_date(self, obj):
        last_contribution = obj.contributions.first()
        return last_contribution.date if last_contribution else None
    
    def validate_target_amount(self, value):
        if value <= 0:
            raise serializers.ValidationError("El monto objetivo debe ser positivo.")
        return value
    
    def validate_target_date(self, value):
        if value <= timezone.now().date():
            raise serializers.ValidationError("La fecha objetivo debe ser futura.")
        return value
    
    def validate_associated_account(self, value):
        if value and value.user != self.context['request'].user:
            raise serializers.ValidationError("La cuenta asociada no te pertenece.")
        return value
    
    def validate(self, data):
        # Validar que start_date sea anterior a target_date
        start_date = data.get('start_date')
        target_date = data.get('target_date')
        
        if start_date and target_date and start_date >= target_date:
            raise serializers.ValidationError("La fecha de inicio debe ser anterior a la fecha objetivo.")
        
        return data

# =====================================================
# SERIALIZERS PARA LISTADOS DE METAS
# =====================================================
class FinancialGoalSummarySerializer(serializers.ModelSerializer):
    """Serializer ligero para listados"""
    progress_percentage = serializers.ReadOnlyField()
    remaining_amount = serializers.ReadOnlyField()
    days_remaining = serializers.ReadOnlyField()
    goal_type_label = serializers.SerializerMethodField()
    status_label = serializers.SerializerMethodField()
    
    class Meta:
        model = FinancialGoal
        fields = [
            'id', 'title', 'goal_type', 'goal_type_label', 'target_amount', 
            'current_amount', 'progress_percentage', 'remaining_amount',
            'target_date', 'days_remaining', 'status', 'status_label',
            'priority', 'icon', 'color'
        ]
    
    def get_goal_type_label(self, obj):
        return obj.get_goal_type_display()
    
    def get_status_label(self, obj):
        return obj.get_status_display()

# =====================================================
# SERIALIZERS PARA PLANTILLAS DE METAS
# =====================================================
class GoalTemplateSerializer(serializers.ModelSerializer):
    suggested_amount_calculated = serializers.SerializerMethodField()
    
    class Meta:
        model = GoalTemplate
        fields = [
            'id', 'name', 'description', 'goal_type', 'suggested_amount',
            'suggested_amount_calculated', 'suggested_timeframe_months',
            'icon', 'color', 'tips'
        ]
    
    def get_suggested_amount_calculated(self, obj):
        request = self.context.get('request')
        if request and request.user.is_authenticated:
            calculated = obj.calculate_suggested_amount(request.user)
            return float(calculated)
        return float(obj.suggested_amount or 0)

# =====================================================
# SERIALIZERS PARA CREAR METAS DESDE PLANTILLAS
# =====================================================
class GoalCreateFromTemplateSerializer(serializers.Serializer):
    """Serializer para crear meta desde plantilla"""
    template_id = serializers.IntegerField()
    title = serializers.CharField(max_length=200, required=False)
    target_amount = serializers.DecimalField(max_digits=15, decimal_places=2, required=False)
    target_date = serializers.DateField(required=False)
    associated_account = serializers.PrimaryKeyRelatedField(
        queryset=Account.objects.none(), 
        required=False
    )
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        request = self.context.get('request')
        if request:
            self.fields['associated_account'].queryset = Account.objects.filter(
                user=request.user
            )
    
    def validate_template_id(self, value):
        try:
            template = GoalTemplate.objects.get(id=value, is_active=True)
            return value
        except GoalTemplate.DoesNotExist:
            raise serializers.ValidationError("Plantilla no encontrada.")
    
    def create(self, validated_data):
        template = GoalTemplate.objects.get(id=validated_data['template_id'])
        user = self.context['request'].user
        
        # Calcular valores por defecto
        target_amount = validated_data.get('target_amount')
        if not target_amount:
            target_amount = template.calculate_suggested_amount(user)
        
        target_date = validated_data.get('target_date')
        if not target_date:
            target_date = timezone.now().date() + timedelta(
                days=template.suggested_timeframe_months * 30
            )
        
        title = validated_data.get('title', template.name)
        
        # Crear la meta
        goal = FinancialGoal.objects.create(
            user=user,
            title=title,
            description=template.description,
            goal_type=template.goal_type,
            target_amount=target_amount,
            target_date=target_date,
            associated_account=validated_data.get('associated_account'),
            icon=template.icon,
            color=template.color
        )
        
        return goal

# =====================================================
# SERIALIZERS PARA REPORTES DE METAS
# =====================================================
class GoalProgressReportSerializer(serializers.Serializer):
    """Reporte de progreso de todas las metas"""
    total_goals = serializers.IntegerField()
    active_goals = serializers.IntegerField()
    completed_goals = serializers.IntegerField()
    overdue_goals = serializers.IntegerField()
    total_target_amount = serializers.DecimalField(max_digits=15, decimal_places=2)
    total_current_amount = serializers.DecimalField(max_digits=15, decimal_places=2)
    overall_progress = serializers.FloatField()
    monthly_contributions = serializers.DecimalField(max_digits=15, decimal_places=2)
    goals_on_track = serializers.IntegerField()

# =====================================================
# SERIALIZERS PARA ANÁLISIS AVANZADO DE METAS
# =====================================================
class GoalAnalyticsSerializer(serializers.Serializer):
    """Análisis avanzado de metas financieras"""
    goal_id = serializers.IntegerField()
    goal_title = serializers.CharField()
    progress_trend = serializers.ListField(child=serializers.DictField())
    monthly_contributions = serializers.ListField(child=serializers.DictField())
    projected_completion_date = serializers.DateField()
    is_on_track = serializers.BooleanField()
    recommended_monthly_amount = serializers.DecimalField(max_digits=12, decimal_places=2)

# =====================================================
# SERIALIZERS PARA DASHBOARD DE METAS
# =====================================================
class GoalDashboardSerializer(serializers.Serializer):
    """Serializer para dashboard completo de metas"""
    summary = GoalProgressReportSerializer()
    recent_goals = FinancialGoalSummarySerializer(many=True)
    urgent_goals = FinancialGoalSummarySerializer(many=True)
    top_performing_goals = FinancialGoalSummarySerializer(many=True)
    monthly_progress_chart = serializers.DictField()
    goals_by_type_chart = serializers.DictField()