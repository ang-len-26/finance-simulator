from rest_framework import viewsets, status
from rest_framework.permissions import IsAuthenticated
from rest_framework.decorators import api_view, action
from rest_framework.response import Response
from rest_framework.decorators import permission_classes
from django.utils import timezone
from django_filters.rest_framework import DjangoFilterBackend
from decimal import Decimal
from django.db.models import Sum, Count, Q, Avg, F
from datetime import timedelta, date

from .models import FinancialGoal, GoalContribution, GoalTemplate
from .serializers import FinancialGoalSerializer, FinancialGoalSummarySerializer, GoalContributionSerializer, GoalDashboardSerializer, GoalTemplateSerializer

# =====================================================
# GESTIÓN DE METAS FINANCIERAS
# =====================================================
class FinancialGoalViewSet(viewsets.ModelViewSet):
    """ViewSet completo para metas financieras"""
    serializer_class = FinancialGoalSerializer
    permission_classes = [IsAuthenticated]
    filter_backends = [DjangoFilterBackend]
    filterset_class = FinancialGoalFilter
    ordering_fields = ['created_at', 'target_date', 'priority', 'progress_percentage']
    ordering = ['-priority', 'target_date']
    
    def get_queryset(self):
        """Solo metas del usuario actual con filtros"""
        queryset = FinancialGoal.objects.filter(user=self.request.user)
        
        # Filtros opcionales
        status = self.request.query_params.get('status')
        goal_type = self.request.query_params.get('goal_type')
        priority = self.request.query_params.get('priority')
        
        if status:
            queryset = queryset.filter(status=status)
        if goal_type:
            queryset = queryset.filter(goal_type=goal_type)
        if priority:
            queryset = queryset.filter(priority=priority)
        
        return queryset
    
    def get_serializer_class(self):
        """Usar serializer ligero para list"""
        if self.action == 'list':
            return FinancialGoalSummarySerializer
        return FinancialGoalSerializer
    
    def perform_create(self, serializer):
        """Asociar meta con usuario actual"""
        goal = serializer.save(user=self.request.user)
        
        # Calcular monthly_target si no se proporcionó
        if not goal.monthly_target:
            goal.monthly_target = goal.suggested_monthly_amount
            goal.save(update_fields=['monthly_target'])
    
    @action(detail=True, methods=['post'])
    def add_contribution(self, request, pk=None):
        """Agregar contribución a una meta"""
        goal = self.get_object()
        
        serializer = GoalContributionSerializer(
            data=request.data,
            context={'request': request}
        )
        
        if serializer.is_valid():
            contribution = serializer.save(
                goal=goal,
                user=request.user
            )
            
            return Response({
                'message': 'Contribución agregada exitosamente',
                'contribution': GoalContributionSerializer(contribution).data,
                'goal_progress': goal.progress_percentage
            }, status=status.HTTP_201_CREATED)
        
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
    @action(detail=True, methods=['get'])
    def contributions(self, request, pk=None):
        """Obtener todas las contribuciones de una meta"""
        goal = self.get_object()
        contributions = goal.contributions.all()
        
        # Filtros opcionales
        start_date = request.query_params.get('start_date')
        end_date = request.query_params.get('end_date')
        
        if start_date:
            contributions = contributions.filter(date__gte=start_date)
        if end_date:
            contributions = contributions.filter(date__lte=end_date)
        
        serializer = GoalContributionSerializer(contributions, many=True)
        
        # Estadísticas adicionales
        stats = contributions.aggregate(
            total_amount=Sum('amount'),
            contribution_count=Count('id'),
            avg_contribution=Avg('amount')
        )
        
        return Response({
            'contributions': serializer.data,
            'statistics': {
                'total_amount': float(stats['total_amount'] or 0),
                'contribution_count': stats['contribution_count'],
                'average_contribution': float(stats['avg_contribution'] or 0)
            }
        })
    
    @action(detail=True, methods=['post'])
    def add_milestone(self, request, pk=None):
        """Agregar hito a una meta"""
        goal = self.get_object()
        
        serializer = GoalMilestoneSerializer(data=request.data)
        if serializer.is_valid():
            milestone = serializer.save(goal=goal)
            return Response(
                GoalMilestoneSerializer(milestone).data,
                status=status.HTTP_201_CREATED
            )
        
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
    @action(detail=True, methods=['post'])
    def pause(self, request, pk=None):
        """Pausar una meta"""
        goal = self.get_object()
        goal.status = 'paused'
        goal.save(update_fields=['status'])
        
        return Response({
            'message': 'Meta pausada exitosamente',
            'status': goal.status
        })
    
    @action(detail=True, methods=['post'])
    def resume(self, request, pk=None):
        """Reanudar una meta pausada"""
        goal = self.get_object()
        if goal.status != 'paused':
            return Response(
                {'error': 'Solo se pueden reanudar metas pausadas'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        goal.status = 'active'
        goal.save(update_fields=['status'])
        
        return Response({
            'message': 'Meta reanudada exitosamente',
            'status': goal.status
        })
    
    @action(detail=True, methods=['post'])
    def complete(self, request, pk=None):
        """Marcar meta como completada manualmente"""
        goal = self.get_object()
        goal.status = 'completed'
        goal.completed_at = timezone.now()
        goal.current_amount = goal.target_amount  # Asegurar 100%
        goal.save(update_fields=['status', 'completed_at', 'current_amount'])
        
        return Response({
            'message': 'Meta completada exitosamente',
            'status': goal.status,
            'completed_at': goal.completed_at
        })
    
    @action(detail=True, methods=['get'])
    def analytics(self, request, pk=None):
        """Análisis detallado de una meta específica"""
        goal = self.get_object()
        
        # Progreso mensual de los últimos 6 meses
        six_months_ago = timezone.now().date() - timedelta(days=180)
        monthly_contributions = goal.contributions.filter(
            date__gte=six_months_ago
        ).extra(
            select={'month': "DATE_TRUNC('month', date)"}
        ).values('month').annotate(
            total_amount=Sum('amount'),
            contribution_count=Count('id')
        ).order_by('month')
        
        progress_trend = []
        monthly_data = []
        
        for item in monthly_contributions:
            month_str = item['month'].strftime('%Y-%m')
            monthly_data.append({
                'month': month_str,
                'amount': float(item['total_amount']),
                'count': item['contribution_count']
            })
        
        # Calcular fecha proyectada de completación
        if goal.remaining_amount > 0 and goal.suggested_monthly_amount > 0:
            months_remaining = goal.remaining_amount / goal.suggested_monthly_amount
            projected_date = timezone.now().date() + timedelta(days=int(months_remaining * 30))
        else:
            projected_date = goal.target_date
        
        # Determinar si está en buen camino
        expected_progress = 0
        if goal.days_remaining > 0:
            total_days = (goal.target_date - goal.start_date).days
            days_passed = total_days - goal.days_remaining
            expected_progress = (days_passed / total_days) * 100 if total_days > 0 else 0
        
        is_on_track = goal.progress_percentage >= (expected_progress - 10)  # 10% de margen
        
        analytics_data = {
            'goal_id': goal.id,
            'goal_title': goal.title,
            'progress_trend': progress_trend,
            'monthly_contributions': monthly_data,
            'projected_completion_date': projected_date,
            'is_on_track': is_on_track,
            'recommended_monthly_amount': float(goal.suggested_monthly_amount),
            'expected_progress': round(expected_progress, 1),
            'actual_progress': round(goal.progress_percentage, 1)
        }
        serializer = GoalAnalyticsSerializer(analytics_data)
        return Response(serializer.data)

    @action(detail=False, methods=['get'])
    def dashboard(self, request):
        """Dashboard completo de metas financieras"""
        user = request.user
        goals = FinancialGoal.objects.filter(user=user)
        
        # Métricas generales
        summary_stats = goals.aggregate(
            total_goals=Count('id'),
            active_goals=Count('id', filter=Q(status='active')),
            completed_goals=Count('id', filter=Q(status='completed')),
            overdue_goals=Count('id', filter=Q(status='overdue')),
            total_target=Sum('target_amount'),
            total_current=Sum('current_amount')
        )
        
        total_target = summary_stats['total_target'] or Decimal('0.00')
        total_current = summary_stats['total_current'] or Decimal('0.00')
        overall_progress = float((total_current / total_target * 100)) if total_target > 0 else 0
        
        # Contribuciones del último mes
        last_month = timezone.now().date() - timedelta(days=30)
        monthly_contributions = GoalContribution.objects.filter(
            user=user,
            date__gte=last_month
        ).aggregate(total=Sum('amount'))['total'] or Decimal('0.00')
        
        # Metas en buen camino
        goals_on_track = 0
        for goal in goals.filter(status='active'):
            if goal.progress_percentage >= 50:  # Criterio simple
                goals_on_track += 1
        
        summary = {
            'total_goals': summary_stats['total_goals'],
            'active_goals': summary_stats['active_goals'],
            'completed_goals': summary_stats['completed_goals'],
            'overdue_goals': summary_stats['overdue_goals'],
            'total_target_amount': float(total_target),
            'total_current_amount': float(total_current),
            'overall_progress': round(overall_progress, 1),
            'monthly_contributions': float(monthly_contributions),
            'goals_on_track': goals_on_track
        }
        
        # Metas recientes (últimas 5)
        recent_goals = goals.order_by('-created_at')[:5]
        
        # Metas urgentes (próximas a vencer)
        urgent_goals = goals.filter(
            status='active',
            target_date__lte=timezone.now().date() + timedelta(days=30)
        ).order_by('target_date')[:5]
        
        # Metas con mejor progreso
        top_performing = goals.filter(status='active').order_by('-current_amount')[:5]
        
        # Datos para gráficos
        monthly_chart = self._get_monthly_progress_chart(user)
        type_chart = self._get_goals_by_type_chart(goals)
        
        dashboard_data = {
            'summary': summary,
            'recent_goals': FinancialGoalSummarySerializer(recent_goals, many=True).data,
            'urgent_goals': FinancialGoalSummarySerializer(urgent_goals, many=True).data,
            'top_performing_goals': FinancialGoalSummarySerializer(top_performing, many=True).data,
            'monthly_progress_chart': monthly_chart,
            'goals_by_type_chart': type_chart
        }
        serializer = GoalDashboardSerializer(dashboard_data)
        return Response(serializer.data)

    def _get_monthly_progress_chart(self, user):
        """Generar datos para gráfico de progreso mensual"""
        # Contribuciones de los últimos 6 meses
        six_months_ago = timezone.now().date() - timedelta(days=180)
        monthly_data = GoalContribution.objects.filter(
            user=user,
            date__gte=six_months_ago
        ).extra(
            select={'month': "DATE_TRUNC('month', date)"}
        ).values('month').annotate(
            total_amount=Sum('amount')
        ).order_by('month')
        
        labels = []
        data = []
        
        for item in monthly_data:
            labels.append(item['month'].strftime('%b'))
            data.append(float(item['total_amount']))
        
        return {
            'labels': labels,
            'datasets': [{
                'label': 'Contribuciones Mensuales',
                'data': data,
                'backgroundColor': 'rgba(59, 130, 246, 0.5)',
                'borderColor': 'rgb(59, 130, 246)',
                'borderWidth': 2
            }]
        }
    
    def _get_goals_by_type_chart(self, goals):
        """Generar datos para gráfico de metas por tipo"""
        type_data = goals.values('goal_type').annotate(
            count=Count('id'),
            total_amount=Sum('target_amount')
        ).order_by('-count')
        
        labels = []
        data = []
        colors = ['#3b82f6', '#10b981', '#f59e0b', '#ef4444', '#8b5cf6', '#06b6d4']
        
        for i, item in enumerate(type_data):
            goal_type_label = dict(FinancialGoal.GOAL_TYPES).get(
                item['goal_type'], 
                item['goal_type']
            )
            labels.append(goal_type_label)
            data.append(item['count'])
        
        return {
            'labels': labels,
            'datasets': [{
                'data': data,
                'backgroundColor': colors[:len(data)],
                'borderWidth': 2
            }]
        }
    
    @action(detail=False, methods=['get'])
    def summary(self, request):
        """Resumen rápido de metas para widgets"""
        user = request.user
        goals = FinancialGoal.objects.filter(user=user)
        
        # Estadísticas básicas
        stats = goals.aggregate(
            total=Count('id'),
            active=Count('id', filter=Q(status='active')),
            completed=Count('id', filter=Q(status='completed')),
            total_saved=Sum('current_amount'),
            total_target=Sum('target_amount')
        )
        
        # Meta más próxima a completar
        next_to_complete = goals.filter(
            status='active'
        ).order_by('-progress_percentage').first()
        
        return Response({
            'total_goals': stats['total'],
            'active_goals': stats['active'],
            'completed_goals': stats['completed'],
            'total_saved': float(stats['total_saved'] or 0),
            'total_target': float(stats['total_target'] or 0),
            'next_to_complete': FinancialGoalSummarySerializer(
                next_to_complete
            ).data if next_to_complete else None
        })

# =====================================================
# GESTIÓN DE CONTRIBUCIONES A METAS
# =====================================================
class GoalContributionViewSet(viewsets.ModelViewSet):
    """ViewSet para gestión de contribuciones"""
    serializer_class = GoalContributionSerializer
    permission_classes = [IsAuthenticated]
    filter_backends = [DjangoFilterBackend]
    filterset_class = GoalContributionFilter
    ordering = ['-date', '-created_at']
    
    def get_queryset(self):
        return GoalContribution.objects.filter(user=self.request.user)
    
    def perform_create(self, serializer):
        serializer.save(user=self.request.user)

# =====================================================
# GESTIÓN DE PLANTILLAS DE METAS
# =====================================================
class GoalTemplateViewSet(viewsets.ReadOnlyModelViewSet):
    """ViewSet para plantillas de metas (solo lectura)"""
    serializer_class = GoalTemplateSerializer
    permission_classes = [IsAuthenticated]
    queryset = GoalTemplate.objects.filter(is_active=True).order_by('sort_order')
    
    @action(detail=True, methods=['post'])
    def create_goal(self, request, pk=None):
        """Crear meta desde plantilla"""
        template = self.get_object()
        
        serializer = GoalCreateFromTemplateSerializer(
            data={'template_id': template.id, **request.data},
            context={'request': request}
        )
        
        if serializer.is_valid():
            goal = serializer.save()
            return Response(
                FinancialGoalSerializer(goal, context={'request': request}).data,
                status=status.HTTP_201_CREATED
            )
        
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
    @action(detail=False, methods=['get'])
    def by_category(self, request):
        """Plantillas agrupadas por tipo de meta"""
        templates = self.get_queryset()
        
        grouped = {}
        for template in templates:
            goal_type = template.goal_type
            if goal_type not in grouped:
                grouped[goal_type] = []
            
            grouped[goal_type].append(
                GoalTemplateSerializer(
                    template, 
                    context={'request': request}
                ).data
            )
        
        return Response(grouped)

# =====================================================
# PLANTILLAS DE METAS
# =====================================================
@api_view(['POST'])
@permission_classes([IsAuthenticated])
def create_goal_templates(request):
    """Crear plantillas predeterminadas de metas"""
    try:
        from .models import create_default_goal_templates
        create_default_goal_templates()
        
        total_templates = GoalTemplate.objects.count()
        
        return Response({
            'message': 'Plantillas de metas creadas exitosamente',
            'total_templates': total_templates
        })
        
    except Exception as e:
        return Response(
            {'error': f'Error al crear plantillas: {str(e)}'}, 
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )

# =====================================================
# VISTA DE CALENDARIO DE METAS
# =====================================================
@api_view(['GET'])
@permission_classes([IsAuthenticated])
def goals_calendar(request):
    """Vista de calendario con fechas importantes de metas"""
    user = request.user
    
    # Obtener año y mes de los parámetros
    year = int(request.query_params.get('year', timezone.now().year))
    month = int(request.query_params.get('month', timezone.now().month))
    
    # Rango de fechas del mes
    start_date = date(year, month, 1)
    if month == 12:
        end_date = date(year + 1, 1, 1) - timedelta(days=1)
    else:
        end_date = date(year, month + 1, 1) - timedelta(days=1)
    
    # Metas con fechas objetivo en este mes
    goals_this_month = FinancialGoal.objects.filter(
        user=user,
        target_date__range=[start_date, end_date]
    ).order_by('target_date')
    
    # Contribuciones programadas (si hubiera)
    # contributions_this_month = GoalContribution.objects.filter(
    #     user=user,
    #     date__range=[start_date, end_date],
    #     is_recurring=True
    # )
    
    calendar_events = []
    
    # Agregar fechas objetivo de metas
    for goal in goals_this_month:
        calendar_events.append({
            'date': goal.target_date.strftime('%Y-%m-%d'),
            'type': 'goal_deadline',
            'title': f"Meta: {goal.title}",
            'description': f"Fecha límite para completar meta",
            'goal_id': goal.id,
            'status': goal.status,
            'progress': goal.progress_percentage,
            'color': goal.color
        })
    
    return Response({
        'year': year,
        'month': month,
        'events': calendar_events,
        'summary': {
            'goals_due_this_month': len(goals_this_month),
            'urgent_goals': len([g for g in goals_this_month if g.days_remaining <= 7])
        }
    })

# =====================================================
# VISTA DE INSIGHTS INTELIGENTES SOBRE METAS
# =====================================================
@api_view(['GET'])
@permission_classes([IsAuthenticated])
def goals_insights(request):
    """Insights inteligentes sobre las metas del usuario"""
    user = request.user
    goals = FinancialGoal.objects.filter(user=user)
    
    insights = []
    
    # Insight 1: Metas vencidas
    overdue_goals = goals.filter(status='overdue').count()
    if overdue_goals > 0:
        insights.append({
            'type': 'warning',
            'title': 'Metas Vencidas',
            'message': f'Tienes {overdue_goals} meta(s) vencida(s). Considera revisar tus plazos.',
            'action': 'review_overdue_goals',
            'priority': 'high'
        })
    
    # Insight 2: Progreso lento
    slow_progress_goals = []
    for goal in goals.filter(status='active'):
        if goal.progress_percentage < 25 and goal.days_remaining < 90:
            slow_progress_goals.append(goal)
    
    if slow_progress_goals:
        insights.append({
            'type': 'info',
            'title': 'Progreso Lento',
            'message': f'{len(slow_progress_goals)} meta(s) necesitan más contribuciones para completarse a tiempo.',
            'action': 'increase_contributions',
            'priority': 'medium'
        })
    
    # Insight 3: Metas próximas a completar
    almost_complete = goals.filter(
        status='active',
        current_amount__gte=F('target_amount') * 0.9
    ).count()
    
    if almost_complete > 0:
        insights.append({
            'type': 'success',
            'title': '¡Casi lo logras!',
            'message': f'{almost_complete} meta(s) están al 90% o más. ¡Un poco más y las completarás!',
            'action': 'complete_goals',
            'priority': 'low'
        })
    
    # Insight 4: Sugerir nueva meta
    if not goals.filter(goal_type='emergency_fund').exists():
        insights.append({
            'type': 'suggestion',
            'title': 'Fondo de Emergencia',
            'message': 'Te recomendamos crear un fondo de emergencia para imprevistos.',
            'action': 'create_emergency_fund',
            'priority': 'medium'
        })
    
    return Response({
        'insights': insights,
        'generated_at': timezone.now()
    })

