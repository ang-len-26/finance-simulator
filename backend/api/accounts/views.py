from rest_framework import viewsets, status
from rest_framework.permissions import IsAuthenticated
from rest_framework.decorators import action
from rest_framework.response import Response
from django.utils import timezone
from decimal import Decimal
from django.db.models import Sum, Count, Q
from datetime import timedelta
from django_filters.rest_framework import DjangoFilterBackend

from ..transactions.models import Transaction
from .models import Account
from .serializers import AccountSerializer, AccountSummarySerializer
from .filters import AccountFilter

class AccountViewSet(viewsets.ModelViewSet):
    """ViewSet para gestión completa de cuentas bancarias"""
    serializer_class = AccountSerializer
    permission_classes = [IsAuthenticated]
    
    filter_backends = [DjangoFilterBackend]
    filterset_class = AccountFilter
    
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
        
        from ..transactions.serializers import TransactionSummarySerializer
        
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
        
        # Balance inicial hace 30 días
        initial_transactions = Transaction.objects.filter(
            Q(from_account=account) | Q(to_account=account),
            date__lt=thirty_days_ago
        )
        
        running_balance = account.initial_balance
        for transaction in initial_transactions:
            if transaction.from_account == account:
                running_balance -= transaction.amount
            if transaction.to_account == account:
                running_balance += transaction.amount
        
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
        for account in accounts[:10]:  # Top 10 para calcular
            transaction_count = Transaction.objects.filter(
                Q(from_account=account) | Q(to_account=account)
            ).count()
            
            if transaction_count > 0:  # Solo cuentas con transacciones
                most_used.append({
                    'id': account.id,
                    'name': account.name,
                    'bank_name': account.bank_name,
                    'account_type': account.account_type,
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
