import uuid
from rest_framework import viewsets, status
from rest_framework.permissions import IsAuthenticated
from rest_framework.decorators import api_view, action
from rest_framework.response import Response
from rest_framework.decorators import permission_classes
from rest_framework.permissions import AllowAny
from rest_framework_simplejwt.tokens import RefreshToken
from django.core.management import call_command
from django.contrib.auth.models import User
from django.utils import timezone
from django_filters.rest_framework import DjangoFilterBackend
from decimal import Decimal
from django.db.models import Sum, Count, Q, Avg, Max, Min, F
from datetime import datetime, timedelta, date

# Imports locales
from .models import Transaction, Account, Category, FinancialGoal, GoalContribution, BudgetAlert, GoalTemplate, CategorySummary, FinancialMetric
from .serializers import (
    TransactionSerializer,
    AccountSerializer,
    AccountSummarySerializer,
    TransactionSummarySerializer,
    CategorySerializer,
	CategorySummarySerializer,
    CategorySummaryReportSerializer,
    FinancialGoalSerializer, 
    FinancialGoalSummarySerializer,
    FinancialMetricSerializer,
    GoalContributionSerializer, 
    GoalMilestoneSerializer, 
    GoalTemplateSerializer,
    GoalCreateFromTemplateSerializer, 
    GoalAnalyticsSerializer, 
    GoalDashboardSerializer,
    BudgetAlertSerializer
)
from .filters import TransactionFilter, FinancialGoalFilter, GoalContributionFilter

# =====================================================
# GESTION PARA CUENTAS BANCARIAS
# =====================================================
class AccountViewSet(viewsets.ModelViewSet):
    """ViewSet para gestión completa de cuentas bancarias"""
    serializer_class = AccountSerializer
    permission_classes = [IsAuthenticated]
    ordering_fields = ['name', 'bank_name', 'current_balance', 'created_at']
    ordering = ['bank_name', 'name']
    
    def get_queryset(self):
        """Solo cuentas del usuario actual"""
        return Account.objects.filter(user=self.request.user)
    
    def get_serializer_class(self):
        """Usar serializer ligero para list"""
        if self.action == 'list':
            return AccountSummarySerializer
        return AccountSerializer
    
    def perform_create(self, serializer):
        """Asociar cuenta con usuario actual"""
        account = serializer.save(user=self.request.user)
        # Calcular balance inicial
        account.current_balance = account.initial_balance
        account.save()
    
    @action(detail=True, methods=['get'])
    def transactions(self, request, pk=None):
        """Obtener todas las transacciones de una cuenta"""
        account = self.get_object()
        transactions = Transaction.objects.filter(
            Q(from_account=account) | Q(to_account=account)
        ).order_by('-date')
        
        serializer = TransactionSummarySerializer(transactions, many=True)
        return Response(serializer.data)
    
    @action(detail=True, methods=['get'])
    def balance_history(self, request, pk=None):
        """Historial de balance de la cuenta (últimos 30 días)"""
        account = self.get_object()
        
        # Obtener transacciones de los últimos 30 días
        thirty_days_ago = timezone.now().date() - timedelta(days=30)
        transactions = Transaction.objects.filter(
            Q(from_account=account) | Q(to_account=account),
            date__gte=thirty_days_ago
        ).order_by('date')
        
        # Calcular balance día por día
        balance_history = []
        running_balance = account.initial_balance
        
        # Agrupar transacciones por día
        daily_transactions = {}
        for transaction in transactions:
            date_str = transaction.date.strftime('%Y-%m-%d')
            if date_str not in daily_transactions:
                daily_transactions[date_str] = []
            daily_transactions[date_str].append(transaction)
        
        # Generar historial día por día
        current_date = thirty_days_ago
        while current_date <= timezone.now().date():
            date_str = current_date.strftime('%Y-%m-%d')
            
            if date_str in daily_transactions:
                for transaction in daily_transactions[date_str]:
                    if transaction.from_account == account:
                        running_balance -= transaction.amount
                    if transaction.to_account == account:
                        running_balance += transaction.amount
            
            balance_history.append({
                'date': date_str,
                'balance': float(running_balance)
            })
            
            current_date += timedelta(days=1)
        
        return Response(balance_history)
    
    @action(detail=True, methods=['post'])
    def reconcile(self, request, pk=None):
        """Conciliar cuenta con balance real"""
        account = self.get_object()
        real_balance = request.data.get('real_balance')
        
        if real_balance is None:
            return Response(
                {'error': 'Se requiere el balance real'}, 
                status=status.HTTP_400_BAD_REQUEST
            )
        
        try:
            real_balance = Decimal(str(real_balance))
            difference = real_balance - account.current_balance
            
            if difference != 0:
                # Crear transacción de ajuste
                Transaction.objects.create(
                    user=account.user,
                    title=f"Ajuste de conciliación - {account.name}",
                    amount=abs(difference),
                    type='income' if difference > 0 else 'expense',
                    date=timezone.now().date(),
                    description=f"Ajuste automático. Balance calculado: {account.current_balance}, Balance real: {real_balance}",
                    from_account=account if difference < 0 else None,
                    to_account=account if difference > 0 else None,
                )
                
                # Actualizar balance
                account.update_balance()
            
            return Response({
                'message': 'Conciliación completada',
                'difference': float(difference),
                'new_balance': float(account.current_balance)
            })
            
        except (ValueError, TypeError):
            return Response(
                {'error': 'Balance inválido'}, 
                status=status.HTTP_400_BAD_REQUEST
            )
    
    @action(detail=False, methods=['get'])
    def summary(self, request):
        """Resumen financiero de todas las cuentas"""
        accounts = self.get_queryset().filter(is_active=True)
        
        summary = accounts.aggregate(
            total_balance=Sum('current_balance'),
            total_accounts=Count('id')
        )
        
        # Balance por tipo de cuenta
        by_type = {}
        for account_type, _ in Account.ACCOUNT_TYPES:
            type_balance = accounts.filter(account_type=account_type).aggregate(
                balance=Sum('current_balance')
            )['balance'] or Decimal('0.00')
            
            if type_balance > 0:
                by_type[account_type] = float(type_balance)
        
        # Cuentas más utilizadas (por número de transacciones)
        most_used = []
        for account in accounts[:5]:  # Top 5
            transaction_count = Transaction.objects.filter(
                Q(from_account=account) | Q(to_account=account)
            ).count()
            
            most_used.append({
                'id': account.id,
                'name': account.name,
                'bank_name': account.bank_name,
                'transaction_count': transaction_count,
                'balance': float(account.current_balance)
            })
        
        most_used.sort(key=lambda x: x['transaction_count'], reverse=True)
        
        return Response({
            'total_balance': float(summary['total_balance'] or 0),
            'total_accounts': summary['total_accounts'],
            'balance_by_type': by_type,
            'most_used_accounts': most_used[:5]
        })

# =====================================================
# GESTION PARA TRANSACCIONES
# =====================================================
class TransactionViewSet(viewsets.ModelViewSet):
    """ViewSet actualizado con sistema de cuentas"""
    serializer_class = TransactionSerializer
    permission_classes = [IsAuthenticated]
    filter_backends = [DjangoFilterBackend]
    filterset_class = TransactionFilter
    ordering_fields = ['date', 'amount', 'title']
    ordering = ['-date']
    
    def get_queryset(self):
        """Solo transacciones del usuario actual"""
        return Transaction.objects.filter(user=self.request.user)
    
    def get_serializer_class(self):
        """Usar serializer ligero para list"""
        if self.action == 'list':
            return TransactionSummarySerializer
        return TransactionSerializer
    
    def perform_create(self, serializer):
        """Asociar transacción con usuario actual"""
        serializer.save(user=self.request.user)
    
    @action(detail=False, methods=['get'])
    def dashboard(self, request):
        """Dashboard de transacciones con métricas clave"""
        user = request.user
        
        # Rango de fechas (último mes por defecto)
        end_date = timezone.now().date()
        start_date = end_date - timedelta(days=30)
        
        # Obtener parámetros de consulta
        start_param = request.query_params.get('start_date')
        end_param = request.query_params.get('end_date')
        
        if start_param:
            start_date = datetime.strptime(start_param, '%Y-%m-%d').date()
        if end_param:
            end_date = datetime.strptime(end_param, '%Y-%m-%d').date()
        
        transactions = Transaction.objects.filter(
            user=user,
            date__range=[start_date, end_date]
        )
        
        # Métricas básicas
        summary = transactions.aggregate(
            total_income=Sum('amount', filter=Q(type='income')),
            total_expenses=Sum('amount', filter=Q(type='expense')),
            total_investments=Sum('amount', filter=Q(type='investment')),
            total_savings=Sum('amount', filter=Q(type='savings')),
            transaction_count=Count('id')
        )
        
        # Calcular flujo neto
        total_income = summary['total_income'] or Decimal('0.00')
        total_expenses = summary['total_expenses'] or Decimal('0.00')
        net_flow = total_income - total_expenses
        
        # Gastos por cuenta
        expenses_by_account = transactions.filter(
            type='expense'
        ).values(
            'from_account__name', 'from_account__bank_name'
        ).annotate(
            total=Sum('amount')
        ).order_by('-total')[:5]
        
        # Ingresos por cuenta
        income_by_account = transactions.filter(
            type='income'
        ).values(
            'to_account__name', 'to_account__bank_name'
        ).annotate(
            total=Sum('amount')
        ).order_by('-total')[:5]
        
        return Response({
            'period': {
                'start_date': start_date,
                'end_date': end_date
            },
            'summary': {
                'total_income': float(total_income),
                'total_expenses': float(total_expenses),
                'total_investments': float(summary['total_investments'] or 0),
                'total_savings': float(summary['total_savings'] or 0),
                'net_flow': float(net_flow),
                'transaction_count': summary['transaction_count']
            },
            'top_expense_accounts': [
                {
                    'account': item['from_account__name'],
                    'bank': item['from_account__bank_name'],
                    'total': float(item['total'])
                }
                for item in expenses_by_account
            ],
            'top_income_accounts': [
                {
                    'account': item['to_account__name'],
                    'bank': item['to_account__bank_name'],
                    'total': float(item['total'])
                }
                for item in income_by_account
            ]
        })

# =====================================================
# SISTEMA DE REPORTES AVANZADOS
# =====================================================
class ReportsViewSet(viewsets.ViewSet):
    """ViewSet para reportes financieros avanzados"""
    permission_classes = [IsAuthenticated]
    
    def _get_date_range(self, request):
        """Utilidad para obtener rango de fechas desde parámetros"""
        period = request.query_params.get('period', 'monthly')  # monthly, quarterly, yearly, custom
        
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
    
    @action(detail=False, methods=['get'])
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
    
    @action(detail=False, methods=['get'])
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
    
    @action(detail=False, methods=['get'])
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
    
    @action(detail=False, methods=['get'])
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
    
    @action(detail=False, methods=['get'])
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
    
    @action(detail=False, methods=['get'])
    def financial_metrics(self, request):
        """Métricas financieras precalculadas por período"""
        user = request.user
    
        # Parámetros
        period_type = request.query_params.get('period_type', 'monthly')
        limit = int(request.query_params.get('limit', 12))
    
        # Obtener métricas existentes
        metrics = FinancialMetric.objects.filter(
            user=user,
            period_type=period_type
        ).order_by('-period_start')[:limit]
    
        # Si no hay métricas, calcular automáticamente
        if not metrics.exists():
            # Crear métricas para los últimos períodos
            metrics = self._generate_financial_metrics(user, period_type, limit)
    
        serializer = FinancialMetricSerializer(metrics, many=True)
        return Response({
            'metrics': serializer.data,
            'period_type': period_type,
            'total_periods': len(serializer.data)
        })

# =====================================================
# GESTION PARA CATEGORÍAS
# =====================================================
class CategoryViewSet(viewsets.ModelViewSet):
    """ViewSet para gestión de categorías"""
    serializer_class = CategorySerializer
    permission_classes = [IsAuthenticated]
    ordering_fields = ['name', 'sort_order', 'created_at']
    ordering = ['sort_order', 'name']
    
    def get_queryset(self):
        """Solo categorías activas por defecto"""
        queryset = Category.objects.all()
        
        # Filtros opcionales
        is_active = self.request.query_params.get('is_active')
        category_type = self.request.query_params.get('category_type')
        parent_id = self.request.query_params.get('parent')
        
        if is_active is not None:
            queryset = queryset.filter(is_active=is_active.lower() == 'true')
        else:
            # Por defecto solo categorías activas
            queryset = queryset.filter(is_active=True)
            
        if category_type:
            queryset = queryset.filter(category_type=category_type)
            
        if parent_id:
            if parent_id.lower() == 'null':
                queryset = queryset.filter(parent__isnull=True)
            else:
                queryset = queryset.filter(parent_id=parent_id)
        
        return queryset
    
    def get_serializer_class(self):
        """Usar serializer ligero para list"""
        if self.action == 'list':
            return CategorySummarySerializer
        return CategorySerializer
    	
    def _generate_category_summaries(self, user, start_date, end_date, period_type):
        """Generar resúmenes de categorías automáticamente"""
        summaries = []
        categories = Category.objects.filter(is_active=True)

        for category in categories:
            # Calcular métricas para esta categoría
            transactions = Transaction.objects.filter(
                user=user,
                category=category,
                date__range=[start_date, end_date]
            )
            
            stats = transactions.aggregate(
                total_amount=Sum('amount'),
                transaction_count=Count('id'),
                avg_amount=Avg('amount')
            )
            
            # Período anterior para comparación
            period_length = (end_date - start_date).days
            prev_start = start_date - timedelta(days=period_length)
            prev_end = start_date - timedelta(days=1)
            
            prev_stats = Transaction.objects.filter(
                user=user,
                category=category,
                date__range=[prev_start, prev_end]
            ).aggregate(total=Sum('amount'))['total'] or Decimal('0.00')
            
            # Calcular porcentaje de cambio
            current_amount = stats['total_amount'] or Decimal('0.00')
            percentage_change = 0
            if prev_stats > 0:
                percentage_change = float(((current_amount - prev_stats) / prev_stats) * 100)
            
            # Cuenta más utilizada
            most_used_account = transactions.values('from_account').annotate(
                count=Count('from_account')
            ).order_by('-count').first()
            
            account_obj = None
            if most_used_account:
                account_obj = Account.objects.get(id=most_used_account['from_account'])
            
            # Crear o actualizar summary
            summary, created = CategorySummary.objects.get_or_create(
                user=user,
                category=category,
                period_start=start_date,
                period_end=end_date,
                period_type=period_type,
                defaults={
                    'total_amount': current_amount,
                    'transaction_count': stats['transaction_count'] or 0,
                    'average_amount': stats['avg_amount'] or Decimal('0.00'),
                    'previous_period_amount': prev_stats,
                    'percentage_change': Decimal(str(percentage_change)),
                    'most_used_account': account_obj
                }
            )
            summaries.append(summary)
        
        return CategorySummary.objects.filter(id__in=[s.id for s in summaries])

    @action(detail=False, methods=['get'])
    def by_type(self, request):
        """Categorías agrupadas por tipo (income/expense)"""
        categories = Category.objects.filter(is_active=True).order_by('sort_order', 'name')
        
        grouped = {
            'income': CategorySummarySerializer(
                categories.filter(category_type__in=['income', 'both']), 
                many=True,
                context={'request': request}
            ).data,
            'expense': CategorySummarySerializer(
                categories.filter(category_type__in=['expense', 'both']), 
                many=True,
                context={'request': request}
            ).data
        }
        
        return Response(grouped)
    
    @action(detail=False, methods=['get'])
    def hierarchy(self, request):
        """Categorías en estructura jerárquica"""
        # Solo categorías padre (sin parent)
        parent_categories = Category.objects.filter(
            is_active=True, 
            parent__isnull=True
        ).order_by('sort_order', 'name')
        
        hierarchy_data = []
        for parent in parent_categories:
            parent_data = CategorySerializer(parent, context={'request': request}).data
            
            # Agregar subcategorías
            subcategories = parent.subcategories.filter(is_active=True).order_by('sort_order', 'name')
            parent_data['subcategories'] = CategorySummarySerializer(
                subcategories, 
                many=True,
                context={'request': request}
            ).data
            
            hierarchy_data.append(parent_data)
        
        return Response(hierarchy_data)
    
    @action(detail=True, methods=['get'])
    def transactions(self, request, pk=None):
        """Transacciones de una categoría específica"""
        category = self.get_object()
        
        # Parámetros de filtrado
        start_date = request.query_params.get('start_date')
        end_date = request.query_params.get('end_date')
        limit = int(request.query_params.get('limit', 20))
        
        transactions = Transaction.objects.filter(
            user=request.user,
            category=category
        ).order_by('-date')
        
        if start_date:
            transactions = transactions.filter(date__gte=start_date)
        if end_date:
            transactions = transactions.filter(date__lte=end_date)
        
        # Paginación manual
        transactions = transactions[:limit]
        
        serializer = TransactionSummarySerializer(transactions, many=True)
        
        # Estadísticas adicionales
        stats = Transaction.objects.filter(
            user=request.user,
            category=category
        ).aggregate(
            total_amount=Sum('amount'),
            transaction_count=Count('id'),
            avg_amount=Avg('amount'),
            max_amount=Max('amount'),
            min_amount=Min('amount')
        )
        
        return Response({
            'transactions': serializer.data,
            'statistics': {
                'total_amount': float(stats['total_amount'] or 0),
                'transaction_count': stats['transaction_count'],
                'average_amount': float(stats['avg_amount'] or 0),
                'max_amount': float(stats['max_amount'] or 0),
                'min_amount': float(stats['min_amount'] or 0)
            }
        })
    
    @action(detail=True, methods=['get'])
    def monthly_trend(self, request, pk=None):
        """Tendencia mensual de gastos/ingresos por categoría"""
        category = self.get_object()
        
        # Últimos 12 meses
        end_date = timezone.now().date()
        start_date = end_date.replace(year=end_date.year - 1, month=end_date.month)
        
        monthly_data = Transaction.objects.filter(
            user=request.user,
            category=category,
            date__range=[start_date, end_date]
        ).extra(
            select={'month': "DATE_TRUNC('month', date)"}
        ).values('month').annotate(
            total_amount=Sum('amount'),
            transaction_count=Count('id')
        ).order_by('month')
        
        # Formatear datos
        trend_data = []
        for item in monthly_data:
            trend_data.append({
                'month': item['month'].strftime('%Y-%m'),
                'month_label': item['month'].strftime('%b %Y'),
                'amount': float(item['total_amount']),
                'transaction_count': item['transaction_count']
            })
        
        return Response({
            'category': CategorySummarySerializer(category).data,
            'trend_data': trend_data,
            'period': {
                'start_date': start_date,
                'end_date': end_date
            }
        })
    
    @action(detail=False, methods=['post'])
    def create_defaults(self, request):
        """Crear categorías predeterminadas"""
        try:
            from .models import create_default_categories
            create_default_categories()
            
            # Contar categorías creadas
            total_categories = Category.objects.count()
            
            return Response({
                'message': 'Categorías predeterminadas creadas exitosamente',
                'total_categories': total_categories
            })
            
        except Exception as e:
            return Response(
                {'error': f'Error al crear categorías: {str(e)}'}, 
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
    
    @action(detail=False, methods=['get'])
    def statistics(self, request):
        """Estadísticas generales de categorías"""
        user = request.user
        
        # Período de análisis
        start_date = request.query_params.get('start_date')
        end_date = request.query_params.get('end_date')
        
        if not start_date or not end_date:
            end_date = timezone.now().date()
            start_date = end_date.replace(day=1)  # Primer día del mes actual
        else:
            start_date = datetime.strptime(start_date, '%Y-%m-%d').date()
            end_date = datetime.strptime(end_date, '%Y-%m-%d').date()
        
        # Estadísticas por categoría
        category_stats = Transaction.objects.filter(
            user=user,
            date__range=[start_date, end_date],
            category__isnull=False
        ).values(
            'category__name',
            'category__icon',
            'category__color',
            'category__category_type'
        ).annotate(
            total_amount=Sum('amount'),
            transaction_count=Count('id'),
            avg_amount=Avg('amount')
        ).order_by('-total_amount')
        
        # Categorías más usadas
        most_used = category_stats[:5]
        
        # Transacciones sin categoría
        uncategorized_count = Transaction.objects.filter(
            user=user,
            date__range=[start_date, end_date],
            category__isnull=True
        ).count()
        
        return Response({
            'period': {
                'start_date': start_date,
                'end_date': end_date
            },
            'most_used_categories': [
                {
                    'name': item['category__name'],
                    'icon': item['category__icon'],
                    'color': item['category__color'],
                    'type': item['category__category_type'],
                    'total_amount': float(item['total_amount']),
                    'transaction_count': item['transaction_count'],
                    'average_amount': float(item['avg_amount'])
                }
                for item in most_used
            ],
            'summary': {
                'total_categories_used': len(category_stats),
                'uncategorized_transactions': uncategorized_count,
                'total_active_categories': Category.objects.filter(is_active=True).count()
            }
        })
    
    @action(detail=False, methods=['get'])
    def summary_report(self, request):
        """Reporte de resumen por categorías con comparativas"""
        user = request.user

        # Parámetros
        period_type = request.query_params.get('period_type', 'monthly')
        start_date = request.query_params.get('start_date')
        end_date = request.query_params.get('end_date')

        if not start_date or not end_date:
            end_date = timezone.now().date()
            if period_type == 'monthly':
                start_date = end_date.replace(day=1)
            else:
                start_date = end_date - timedelta(days=30)
        else:
            start_date = datetime.strptime(start_date, '%Y-%m-%d').date()
            end_date = datetime.strptime(end_date, '%Y-%m-%d').date()

        # Obtener o crear resúmenes
        summaries = CategorySummary.objects.filter(
            user=user,
            period_type=period_type,
            period_start=start_date,
            period_end=end_date
        )

        # Si no existen, generarlos automáticamente
        if not summaries.exists():
            summaries = self._generate_category_summaries(user, start_date, end_date, period_type)

        serializer = CategorySummaryReportSerializer(summaries, many=True)
        return Response({
            'category_summaries': serializer.data,
            'period': {
                'start_date': start_date,
                'end_date': end_date,
                'type': period_type
            }
        })

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
# ALERTAS FINANCIERAS
# =====================================================
class BudgetAlertViewSet(viewsets.ReadOnlyModelViewSet):
    """ViewSet para alertas financieras"""
    serializer_class = BudgetAlertSerializer  # Crear este serializer
    permission_classes = [IsAuthenticated]
    ordering = ['-created_at']
    
    def get_queryset(self):
        return BudgetAlert.objects.filter(user=self.request.user)
    
    @action(detail=True, methods=['post'])
    def mark_read(self, request, pk=None):
        """Marcar alerta como leída"""
        alert = self.get_object()
        alert.is_read = True
        alert.save(update_fields=['is_read'])
        return Response({'status': 'marked_as_read'})
    
    @action(detail=False, methods=['get'])
    def unread(self, request):
        """Solo alertas no leídas"""
        alerts = self.get_queryset().filter(is_read=False)
        serializer = self.get_serializer(alerts, many=True)
        return Response(serializer.data)


# =====================================================
# ENDPOINTS DE AUTENTICACIÓN Y UTILIDADES
# =====================================================
@api_view(['POST'])
@permission_classes([AllowAny])
def register_user(request):
    """Endpoint para 'Crear Cuenta'"""
    data = request.data
    
    if User.objects.filter(username=data['username']).exists():
        return Response({'error': 'Usuario ya existe'}, status=400)
    
    try:
        user = User.objects.create_user(
            username=data['username'],
            email=data['email'],
            password=data['password']
        )
        
        # Crear cuenta por defecto (Efectivo)
        Account.objects.create(
            user=user,
            name="Efectivo",
            account_type="cash",
            initial_balance=Decimal('0.00')
        )
        
        return Response({
            'message': 'Usuario creado exitosamente',
            'user_id': user.id
        }, status=201)
    except Exception as e:
        return Response({'error': str(e)}, status=400)

@api_view(['POST'])
@permission_classes([AllowAny])
def create_demo_user(request):
    """Para 'Probar demo sin registrarse'"""
    demo_user = User.objects.create_user(
        username=f"demo_{uuid.uuid4()}",
        password="demo123"
    )
    
    # Crear cuentas demo
    bcp_account = Account.objects.create(
        user=demo_user,
        name="Cuenta Corriente",
        bank_name="BCP",
        account_type="checking",
        initial_balance=Decimal('5000.00')
    )
    
    savings_account = Account.objects.create(
        user=demo_user,
        name="Cuenta Ahorros",
        bank_name="BBVA",
        account_type="savings", 
        initial_balance=Decimal('10000.00')
    )
    
    cash_account = Account.objects.create(
        user=demo_user,
        name="Efectivo",
        account_type="cash",
        initial_balance=Decimal('500.00')
    )
    
    # Transacciones demo actualizadas
    sample_transactions = [
        {'title': 'Sueldo', 'amount': 3000, 'type': 'income', 'date': '2024-08-01', 'to_account': bcp_account},
        {'title': 'Supermercado', 'amount': 150, 'type': 'expense', 'date': '2024-08-02', 'from_account': bcp_account},
        {'title': 'Netflix', 'amount': 15.99, 'type': 'expense', 'date': '2024-08-03', 'from_account': bcp_account},
        {'title': 'Transferencia a Ahorros', 'amount': 500, 'type': 'transfer', 'date': '2024-08-04', 'from_account': bcp_account, 'to_account': savings_account},
        {'title': 'Retiro ATM', 'amount': 200, 'type': 'transfer', 'date': '2024-08-05', 'from_account': bcp_account, 'to_account': cash_account},
        {'title': 'Inversión', 'amount': 1000, 'type': 'investment', 'date': '2024-08-06', 'from_account': savings_account},
        {'title': 'Pago servicios', 'amount': 100, 'type': 'expense', 'date': '2024-08-07', 'from_account': bcp_account},
        {'title': 'Freelance', 'amount': 800, 'type': 'income', 'date': '2024-08-08', 'to_account': bcp_account},
        {'title': 'Restaurante', 'amount': 60, 'type': 'expense', 'date': '2024-08-09', 'from_account': cash_account},
        {'title': 'Gasolina', 'amount': 35, 'type': 'expense', 'date': '2024-08-10', 'from_account': bcp_account},
    ]
    
    for trans_data in sample_transactions:
        Transaction.objects.create(**trans_data, user=demo_user)
    
    # Actualizar balances
    bcp_account.update_balance()
    savings_account.update_balance()
    cash_account.update_balance()
    
    # Retornar tokens para acceso inmediato
    refresh = RefreshToken.for_user(demo_user)
    return Response({
        'access': str(refresh.access_token),
        'refresh': str(refresh),
        'demo_user': True
    })

@api_view(["POST"])
def create_superuser(request):
    """Endpoint para crear un superusuario"""
    try:
        if User.objects.filter(username="AngelAdminFindTrack").exists():
            return Response({"status": "error", "message": "User already exists"}, status=400)

        User.objects.create_superuser(
            username="AngelAdminFindTrack",
            email="adminfindTrack@findtrack.com",
            password="@FindTrack2025"
        )
        return Response({"status": "success", "message": "Superuser created"}, status=201)

    except Exception as e:
        return Response({"status": "error", "message": str(e)}, status=500)

@api_view(["POST"])
def run_migrations(request):
    """Endpoint para ejecutar migraciones manualmente"""
    try:
        call_command('migrate')
        return Response({"status": "success", "message": "Migrations applied"})
    except Exception as e:
        return Response({"status": "error", "message": str(e)})
    
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
    """Ratios financieros profesionales"""
    user = request.user
    start_date, end_date, period = ReportsViewSet()._get_date_range(ReportsViewSet(), request)
    
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

# ==========================================================================================================
# ENDPOINTS ADICIONALES PARA METAS
# ==========================================================================================================

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


