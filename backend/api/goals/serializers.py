from rest_framework import serializers
from django.utils import timezone
from datetime import timedelta

from ..accounts.models import Account
from .models import FinancialGoal, GoalContribution, GoalMilestone, GoalTemplate

    
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