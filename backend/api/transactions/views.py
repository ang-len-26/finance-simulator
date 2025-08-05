from rest_framework import viewsets, status
from rest_framework.permissions import IsAuthenticated
from rest_framework.decorators import action
from rest_framework.response import Response
from django.utils import timezone
from django_filters.rest_framework import DjangoFilterBackend
from decimal import Decimal
from django.db.models import Sum, Count, Q, Avg, Max, Min
from datetime import datetime, timedelta

from backend.api.accounts.models import Account
from backend.api.analytics.models import BudgetAlert, CategorySummary
from .models import Transaction, Category
from .serializers import TransactionSerializer, TransactionSummarySerializer, CategorySerializer, CategorySummarySerializer, CategorySummaryReportSerializer

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

