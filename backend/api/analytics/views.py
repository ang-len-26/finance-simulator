from rest_framework import viewsets, status
from rest_framework.permissions import IsAuthenticated
from rest_framework.decorators import api_view, action
from rest_framework.response import Response
from rest_framework.decorators import permission_classes
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework.filters import OrderingFilter
from django.utils import timezone
from decimal import Decimal
from django.db.models import Sum, Count, Q, Avg
from datetime import datetime, timedelta

from ..accounts.models import Account
from ..transactions.models import Transaction
from .models import FinancialMetric, BudgetAlert
from .serializers import (
    FinancialMetricSerializer, 
    BudgetAlertSerializer
)

class ReportsViewSet(viewsets.ViewSet):
    """ViewSet mejorado para reportes financieros avanzados"""
    permission_classes = [IsAuthenticated]
    filter_backends = [DjangoFilterBackend, OrderingFilter]
    filterset_fields = ['period_type']
    ordering_fields = ['period_start', 'total_income', 'total_expenses']
    ordering = ['-period_start']
    
    def _get_date_range(self, request):
        """Utilidad mejorada para obtener rango de fechas desde parámetros"""
        period = request.query_params.get('period', 'monthly')
        
        today = timezone.now().date()
        
        if period == 'monthly':
            start_date = today.replace(day=1)
            end_date = today
        elif period == 'quarterly':
            quarter = (today.month - 1) // 3 + 1
            start_month = (quarter - 1) * 3 + 1
            start_date = today.replace(month=start_month, day=1)
            end_date = today
        elif period == 'yearly':
            start_date = today.replace(month=1, day=1)
            end_date = today
        elif period == 'last_30_days':
            end_date = today
            start_date = today - timedelta(days=30)
        elif period == 'last_90_days':
            end_date = today
            start_date = today - timedelta(days=90)
        elif period == 'custom':
            start_date = datetime.strptime(
                request.query_params.get('start_date', str(today)), '%Y-%m-%d'
            ).date()
            end_date = datetime.strptime(
                request.query_params.get('end_date', str(today)), '%Y-%m-%d'
            ).date()
        else:
            start_date = today.replace(day=1)
            end_date = today
            
        return start_date, end_date, period        
    
    @action(detail=False, methods=['get'])
    def alerts(self, request):
        """Endpoint para obtener alertas de presupuesto"""
        user = request.user
        
        # Filtros
        severity = request.query_params.get('severity')
        alert_type = request.query_params.get('alert_type')
        is_read = request.query_params.get('is_read')
        
        queryset = BudgetAlert.objects.filter(user=user)
        
        if severity:
            queryset = queryset.filter(severity=severity)
        if alert_type:
            queryset = queryset.filter(alert_type=alert_type)
        if is_read is not None:
            queryset = queryset.filter(is_read=is_read.lower() == 'true')
        
        # Obtener solo alertas activas por defecto
        if not request.query_params.get('include_dismissed'):
            queryset = queryset.filter(is_dismissed=False)
        
        alerts = queryset.order_by('-created_at')[:20]
        serializer = BudgetAlertSerializer(alerts, many=True)
        
        return Response({
            'alerts': serializer.data,
            'summary': {
                'total_alerts': queryset.count(),
                'unread_count': queryset.filter(is_read=False).count(),
                'critical_count': queryset.filter(severity='critical').count()
            }
        })
    
    @action(detail=False, methods=['post'], url_path='mark-alert-read')
    def mark_alert_read(self, request):
        """Marcar alertas como leídas"""
        alert_ids = request.data.get('alert_ids', [])
        
        if not alert_ids:
            return Response(
                {'error': 'Se requiere una lista de IDs de alertas'}, 
                status=status.HTTP_400_BAD_REQUEST
            )
        
        updated = BudgetAlert.objects.filter(
            id__in=alert_ids,
            user=request.user
        ).update(is_read=True)
        
        return Response({
            'message': f'{updated} alertas marcadas como leídas',
            'updated_count': updated
        })
    
    @action(detail=False, methods=['get'], url_path='category-trends')
    def category_trends(self, request):
        """Tendencias de categorías a lo largo del tiempo"""
        user = request.user
        start_date, end_date, period = self._get_date_range(request)
        
        # Obtener tendencias de las últimas 6 semanas/meses
        if period == 'monthly':
            periods_back = 6
            delta = timedelta(days=30)
        else:
            periods_back = 8
            delta = timedelta(days=7)
        
        trends_data = []
        current_end = end_date
        
        for i in range(periods_back):
            current_start = current_end - delta
            
            # Gastos por categoría en este período
            category_expenses = Transaction.objects.filter(
                user=user,
                type='expense',
                date__range=[current_start, current_end]
            ).values('category__name', 'category__color').annotate(
                total=Sum('amount')
            ).order_by('-total')[:5]
            
            trends_data.append({
                'period': current_end.strftime('%b %Y' if period == 'monthly' else 'Sem %d'),
                'start_date': current_start,
                'end_date': current_end,
                'categories': list(category_expenses)
            })
            
            current_end = current_start
        
        return Response({
            'trends': trends_data,
            'period_type': period
        })

    @action(detail=False, methods=['get'])
    def metrics(self, request):
        """Métricas principales con comparativas - Para las 4 tarjetas superiores"""
        user = request.user
        start_date, end_date, period = self._get_date_range(request)
        
        # Período actual
        current_transactions = Transaction.objects.filter(
            user=user,
            date__range=[start_date, end_date]
        )
        
        current_metrics = current_transactions.aggregate(
            total_income=Sum('amount', filter=Q(type='income')),
            total_expenses=Sum('amount', filter=Q(type='expense')),
            transaction_count=Count('id')
        )
        
        total_income = current_metrics['total_income'] or Decimal('0.00')
        total_expenses = current_metrics['total_expenses'] or Decimal('0.00')
        net_balance = total_income - total_expenses
        
        # Período anterior para comparación
        period_length = (end_date - start_date).days
        prev_start = start_date - timedelta(days=period_length)
        prev_end = start_date - timedelta(days=1)
        
        prev_transactions = Transaction.objects.filter(
            user=user,
            date__range=[prev_start, prev_end]
        )
        
        prev_metrics = prev_transactions.aggregate(
            total_income=Sum('amount', filter=Q(type='income')),
            total_expenses=Sum('amount', filter=Q(type='expense'))
        )
        
        prev_income = prev_metrics['total_income'] or Decimal('0.00')
        prev_expenses = prev_metrics['total_expenses'] or Decimal('0.00')
        
        # Calcular cambios porcentuales
        def calculate_change(current, previous):
            if previous == 0:
                return 0 if current == 0 else 100
            return float(((current - previous) / previous) * 100)
        
        income_change = calculate_change(total_income, prev_income)
        expense_change = calculate_change(total_expenses, prev_expenses)
        
        return Response({
            'period': {
                'start_date': start_date,
                'end_date': end_date,
                'type': period
            },
            'metrics': {
                'total_income': float(total_income),
                'total_expenses': float(total_expenses),
                'net_balance': float(net_balance),
                'transaction_count': current_metrics['transaction_count'],
                'income_change': round(income_change, 1),
                'expense_change': round(expense_change, 1)
            },
            'previous_period': {
                'total_income': float(prev_income),
                'total_expenses': float(prev_expenses),
                'start_date': prev_start,
                'end_date': prev_end
            }
        })
    
    @action(detail=False, methods=['get'], url_path='income-vs-expenses')
    def income_vs_expenses(self, request):
        """Datos para gráfico Ingresos vs Gastos mensuales"""
        user = request.user
        
        # Obtener últimos 12 meses
        end_date = timezone.now().date()
        start_date = end_date.replace(month=1, day=1)
        
        # Si estamos en enero, incluir año anterior
        if end_date.month <= 6:
            start_date = start_date.replace(year=start_date.year - 1)
        
        # Agrupar por mes
        monthly_data = Transaction.objects.filter(
            user=user,
            date__range=[start_date, end_date]
        ).extra(
            select={'month': "DATE_TRUNC('month', date)"}
        ).values('month').annotate(
            income=Sum('amount', filter=Q(type='income')),
            expenses=Sum('amount', filter=Q(type='expense'))
        ).order_by('month')
        
        # Formatear para Chart.js
        labels = []
        income_data = []
        expense_data = []
        
        for item in monthly_data:
            month_date = item['month']
            labels.append(month_date.strftime('%b'))
            income_data.append(float(item['income'] or 0))
            expense_data.append(float(item['expenses'] or 0))
        
        # Calcular balance neto mensual
        net_balance_data = [
            income - expense 
            for income, expense in zip(income_data, expense_data)
        ]
        
        return Response({
            'chart_data': {
                'labels': labels,
                'datasets': [
                    {
                        'label': 'Ingresos',
                        'data': income_data,
                        'backgroundColor': 'rgba(34, 197, 94, 0.5)',
                        'borderColor': 'rgb(34, 197, 94)',
                        'borderWidth': 2
                    },
                    {
                        'label': 'Gastos',
                        'data': expense_data,
                        'backgroundColor': 'rgba(239, 68, 68, 0.5)',
                        'borderColor': 'rgb(239, 68, 68)',
                        'borderWidth': 2
                    }
                ]
            },
            'net_balance_data': net_balance_data,
            'summary': {
                'total_months': len(labels),
                'avg_income': round(sum(income_data) / len(income_data) if income_data else 0, 2),
                'avg_expenses': round(sum(expense_data) / len(expense_data) if expense_data else 0, 2)
            }
        })
    
    @action(detail=False, methods=['get'], url_path='balance-timeline')
    def balance_timeline(self, request):
        """Balance acumulado en el tiempo - Para gráfico de línea"""
        user = request.user
        start_date, end_date, period = self._get_date_range(request)
        
        # Obtener todas las cuentas activas
        accounts = Account.objects.filter(user=user, is_active=True)
        initial_balance = accounts.aggregate(
            total=Sum('initial_balance')
        )['total'] or Decimal('0.00')
        
        # Obtener transacciones ordenadas por fecha
        transactions = Transaction.objects.filter(
            user=user,
            date__range=[start_date, end_date]
        ).order_by('date')
        
        # Calcular balance acumulado día por día
        balance_data = []
        labels = []
        running_balance = float(initial_balance)
        
        # Agrupar transacciones por día
        current_date = start_date
        daily_transactions = {}
        
        for transaction in transactions:
            date_str = transaction.date.strftime('%Y-%m-%d')
            if date_str not in daily_transactions:
                daily_transactions[date_str] = []
            daily_transactions[date_str].append(transaction)
        
        # Generar datos día por día
        while current_date <= end_date:
            date_str = current_date.strftime('%Y-%m-%d')
            
            # Procesar transacciones del día
            if date_str in daily_transactions:
                for transaction in daily_transactions[date_str]:
                    if transaction.type == 'income':
                        running_balance += float(transaction.amount)
                    elif transaction.type in ['expense', 'investment']:
                        running_balance -= float(transaction.amount)
                    # Las transferencias no afectan el balance total
            
            labels.append(current_date.strftime('%d/%m'))
            balance_data.append(round(running_balance, 2))
            
            current_date += timedelta(days=1)
        
        # Calcular tendencia
        if len(balance_data) >= 2:
            trend = balance_data[-1] - balance_data[0]
            trend_percentage = (trend / balance_data[0] * 100) if balance_data[0] != 0 else 0
        else:
            trend = 0
            trend_percentage = 0
        
        return Response({
            'chart_data': {
                'labels': labels,
                'datasets': [{
                    'label': 'Balance Total',
                    'data': balance_data,
                    'fill': True,
                    'backgroundColor': 'rgba(59, 130, 246, 0.1)',
                    'borderColor': 'rgb(59, 130, 246)',
                    'borderWidth': 2,
                    'tension': 0.4
                }]
            },
            'summary': {
                'current_balance': balance_data[-1] if balance_data else 0,
                'initial_balance': float(initial_balance),
                'trend': round(trend, 2),
                'trend_percentage': round(trend_percentage, 2),
                'highest_balance': max(balance_data) if balance_data else 0,
                'lowest_balance': min(balance_data) if balance_data else 0
            }
        })

    @action(detail=False, methods=['get'], url_path='category-distribution')
    def category_distribution(self, request):
        """Distribución de gastos por categoría - Para gráfico de dona/barras"""
        user = request.user
        start_date, end_date, period = self._get_date_range(request)
        
        # Gastos por categoría (usando el campo category si existe, sino usar tags)
        category_data = Transaction.objects.filter(
            user=user,
            type='expense',
            date__range=[start_date, end_date]
        ).values('category__name', 'category__color', 'category__icon').annotate(
            total_amount=Sum('amount'),
            transaction_count=Count('id')
        ).order_by('-total_amount')
        
        # Si no hay categorías, usar análisis de tags temporalmente
        if not category_data:
            # Análisis temporal usando descripción/título para inferir categorías
            expense_transactions = Transaction.objects.filter(
                user=user,
                type='expense',
                date__range=[start_date, end_date]
            )
            
            # Categorización básica por palabras clave
            category_mapping = {
                'Alimentación': ['super', 'restaurant', 'comida', 'food', 'mercado'],
                'Transporte': ['taxi', 'uber', 'gasolina', 'metro', 'bus'],
                'Servicios': ['netflix', 'spotify', 'internet', 'luz', 'agua'],
                'Entretenimiento': ['cine', 'bar', 'fiesta', 'game'],
                'Otros': []
            }
            
            categorized_expenses = {}
            for transaction in expense_transactions:
                assigned = False
                title_lower = transaction.title.lower()
                
                for category, keywords in category_mapping.items():
                    if any(keyword in title_lower for keyword in keywords):
                        if category not in categorized_expenses:
                            categorized_expenses[category] = 0
                        categorized_expenses[category] += float(transaction.amount)
                        assigned = True
                        break
                
                if not assigned:
                    if 'Otros' not in categorized_expenses:
                        categorized_expenses['Otros'] = 0
                    categorized_expenses['Otros'] += float(transaction.amount)
            
            # Formatear para Chart.js
            labels = list(categorized_expenses.keys())
            data = list(categorized_expenses.values())
            colors = ['#ef4444', '#f97316', '#3b82f6', '#22c55e', '#8b5cf6'][:len(labels)]
            
        else:
            # Usar datos reales de categorías
            labels = [item['category__name'] or 'Sin Categoría' for item in category_data]
            data = [float(item['total_amount']) for item in category_data]
            colors = [item['category__color'] or '#6366f1' for item in category_data]
        
        total_expenses = sum(data)
        
        return Response({
            'chart_data': {
                'labels': labels,
                'datasets': [{
                    'data': data,
                    'backgroundColor': colors,
                    'borderWidth': 2,
                    'borderColor': '#fff'
                }]
            },
            'summary': {
                'total_amount': round(total_expenses, 2),
                'category_count': len(labels),
                'average_per_category': round(total_expenses / len(labels) if labels else 0, 2),
                'top_category': {
                    'name': labels[0] if labels else None,
                    'amount': data[0] if data else 0,
                    'percentage': round((data[0] / total_expenses * 100) if total_expenses > 0 and data else 0, 1)
                }
            }
        })
    
    @action(detail=False, methods=['get'], url_path='top-categories')
    def top_categories(self, request):
        """Top 5 categorías de gastos con detalles"""
        user = request.user
        start_date, end_date, period = self._get_date_range(request)
        
        # Período anterior para comparación
        period_length = (end_date - start_date).days
        prev_start = start_date - timedelta(days=period_length)
        prev_end = start_date - timedelta(days=1)
        
        # Gastos actuales por categoría
        current_categories = Transaction.objects.filter(
            user=user,
            type='expense',
            date__range=[start_date, end_date]
        ).values('category__name', 'category__icon', 'category__color').annotate(
            total_amount=Sum('amount'),
            transaction_count=Count('id'),
            avg_amount=Avg('amount')
        ).order_by('-total_amount')[:5]
        
        # Gastos período anterior
        prev_categories = Transaction.objects.filter(
            user=user,
            type='expense',
            date__range=[prev_start, prev_end]
        ).values('category__name').annotate(
            total_amount=Sum('amount')
        )
        
        # Crear diccionario para comparación rápida
        prev_dict = {item['category__name']: item['total_amount'] for item in prev_categories}
        
        # Preparar datos con comparativas
        categories_with_change = []
        for category in current_categories:
            name = category['category__name'] or 'Sin Categoría'
            current_amount = category['total_amount']
            prev_amount = prev_dict.get(name, Decimal('0.00'))
            
            # Calcular cambio porcentual
            if prev_amount > 0:
                change_percentage = float(((current_amount - prev_amount) / prev_amount) * 100)
            else:
                change_percentage = 100.0 if current_amount > 0 else 0.0
            
            categories_with_change.append({
                'name': name,
                'icon': category['category__icon'] or 'receipt',
                'color': category['category__color'] or '#6366f1',
                'current_amount': float(current_amount),
                'previous_amount': float(prev_amount),
                'change_percentage': round(change_percentage, 1),
                'transaction_count': category['transaction_count'],
                'average_amount': float(category['avg_amount'] or 0)
            })
        
        return Response({
            'categories': categories_with_change,
            'period': {
                'current': {'start': start_date, 'end': end_date},
                'previous': {'start': prev_start, 'end': prev_end}
            }
        })
    
    @action(detail=False, methods=['get'], url_path='recent-transactions')
    def recent_transactions(self, request):
        """Transacciones recientes con iconos y detalles"""
        user = request.user
        limit = int(request.query_params.get('limit', 10))
        
        recent = Transaction.objects.filter(user=user).select_related(
            'from_account', 'to_account', 'category'
        ).order_by('-date', '-created_at')[:limit]
        
        transactions_data = []
        for transaction in recent:
            # Determinar ícono basado en categoría o tipo
            if transaction.category:
                icon = transaction.category.icon
            else:
                # Íconos por defecto según tipo
                icon_mapping = {
                    'income': 'plus-circle',
                    'expense': 'minus-circle',
                    'transfer': 'arrow-right-left',
                    'investment': 'trending-up',
                    'loan': 'hand-coins',
                    'savings': 'piggy-bank'
                }
                icon = icon_mapping.get(transaction.type, 'receipt')
            
            transactions_data.append({
                'id': transaction.id,
                'title': transaction.title,
                'amount': float(transaction.amount),
                'type': transaction.type,
                'date': transaction.date.strftime('%d de %B'),
                'icon': icon,
                'from_account': transaction.from_account.name if transaction.from_account else None,
                'to_account': transaction.to_account.name if transaction.to_account else None,
                'category': transaction.category.name if transaction.category else None,
                'is_positive': transaction.type == 'income'
            })
        
        return Response({
            'transactions': transactions_data,
            'total_count': Transaction.objects.filter(user=user).count()
        })
    
    @action(detail=False, methods=['get'], url_path='financial-metrics')
    def financial_metrics(self, request):
        """Métricas financieras precalculadas por período - VERSIÓN COMPLETA"""
        user = request.user
    
        # Parámetros
        period_type = request.query_params.get('period_type', 'monthly')
        limit = int(request.query_params.get('limit', 12))
    
        # Obtener métricas existentes
        metrics = FinancialMetric.objects.filter(
            user=user,
            period_type=period_type
        ).order_by('-period_start')[:limit]
    
        # Si no hay métricas, generar automáticamente
        if not metrics.exists():
            try:
                # Intentar generar métricas automáticamente
                metrics = self._generate_financial_metrics(user, period_type, limit)
            except Exception as e:
                # Si falla la generación, devolver respuesta informativa
                return Response({
                    'metrics': [],
                    'period_type': period_type,
                    'total_periods': 0,
                    'message': f'No hay métricas precalculadas. Ejecute: python manage.py generate_metrics',
                    'suggestion': 'Use otros endpoints como /reports/metrics/ para datos en tiempo real'
                })

        serializer = FinancialMetricSerializer(metrics, many=True)
        return Response({
            'metrics': serializer.data,
            'period_type': period_type,
            'total_periods': len(serializer.data)
        })

# =====================================================
# ENDPOINT PRINCIPAL DE REPORTES
# =====================================================
@api_view(['GET'])
@permission_classes([IsAuthenticated])
def reports_overview(request):
    """Endpoint unificado para la página de reportes completa"""
    user = request.user
    
    # Crear instancia temporal del ViewSet para reutilizar métodos
    reports_viewset = ReportsViewSet()
    reports_viewset.request = request
    
    # Obtener todos los datos necesarios
    metrics_response = reports_viewset.metrics(request)
    income_vs_expenses_response = reports_viewset.income_vs_expenses(request)
    balance_timeline_response = reports_viewset.balance_timeline(request)
    category_distribution_response = reports_viewset.category_distribution(request)
    top_categories_response = reports_viewset.top_categories(request)
    recent_transactions_response = reports_viewset.recent_transactions(request)
    
    return Response({
        'metrics': metrics_response.data['metrics'],
        'period': metrics_response.data['period'],
        'charts': {
            'income_vs_expenses': income_vs_expenses_response.data['chart_data'],
            'balance_timeline': balance_timeline_response.data['chart_data'],
            'category_distribution': category_distribution_response.data['chart_data']
        },
        'insights': {
            'top_categories': top_categories_response.data['categories'],
            'recent_transactions': recent_transactions_response.data['transactions'][:5],
            'balance_summary': balance_timeline_response.data['summary']
        }
    })

# =====================================================
# UTILIDADES PARA ANÁLISIS PROFESIONAL
# =====================================================
@api_view(['GET'])
@permission_classes([IsAuthenticated])
def financial_ratios(request):
    """Ratios financieros profesionales - CORREGIDO ERROR 500"""
    user = request.user
    
    reports_viewset = ReportsViewSet()
    reports_viewset.request = request
    start_date, end_date, period = reports_viewset._get_date_range(request)
    
    transactions = Transaction.objects.filter(
        user=user,
        date__range=[start_date, end_date]
    )
    
    total_income = transactions.filter(type='income').aggregate(
        total=Sum('amount')
    )['total'] or Decimal('0.00')
    
    total_expenses = transactions.filter(type='expense').aggregate(
        total=Sum('amount')
    )['total'] or Decimal('0.00')
    
    total_savings = transactions.filter(type='savings').aggregate(
        total=Sum('amount')
    )['total'] or Decimal('0.00')
    
    total_investments = transactions.filter(type='investment').aggregate(
        total=Sum('amount')
    )['total'] or Decimal('0.00')
    
    # Calcular ratios
    savings_rate = float((total_savings / total_income * 100)) if total_income > 0 else 0
    expense_ratio = float((total_expenses / total_income * 100)) if total_income > 0 else 0
    investment_rate = float((total_investments / total_income * 100)) if total_income > 0 else 0
    
    return Response({
        'ratios': {
            'savings_rate': round(savings_rate, 2),
            'expense_ratio': round(expense_ratio, 2),
            'investment_rate': round(investment_rate, 2),
            'net_worth_change': round(float(total_income - total_expenses), 2)
        },
        'recommendations': {
            'savings': 'Excelente' if savings_rate >= 20 else 'Bueno' if savings_rate >= 10 else 'Mejorar',
            'expenses': 'Controlado' if expense_ratio <= 70 else 'Revisar' if expense_ratio <= 90 else 'Crítico'
        }
    })
