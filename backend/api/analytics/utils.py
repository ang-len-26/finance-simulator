from decimal import Decimal
from django.db.models import Sum, Avg, Q
from datetime import timedelta
from django.utils import timezone

from ..transactions.models import Transaction
from .models import BudgetAlert

def generate_budget_alerts(user):
    """Generar alertas automáticas para un usuario"""
    today = timezone.now().date()
    alerts_created = []
    
    # 1. Verificar gastos inusuales (>150% del promedio)
    last_30_days = today - timedelta(days=30)
    avg_daily_expense = Transaction.objects.filter(
        user=user,
        type='expense',
        date__gte=last_30_days
    ).aggregate(avg=Avg('amount'))['avg'] or Decimal('0.00')
    
    recent_high_expenses = Transaction.objects.filter(
        user=user,
        type='expense',
        date=today,
        amount__gt=avg_daily_expense * Decimal('1.5')
    )
    
    for transaction in recent_high_expenses:
        alert = BudgetAlert.objects.create(
            user=user,
            alert_type='unusual_expense',
            severity='medium',
            title=f'Gasto inusual detectado',
            message=f'El gasto "{transaction.title}" de ${transaction.amount} es 50% mayor al promedio diario.',
            related_transaction=transaction,
            threshold_amount=avg_daily_expense * Decimal('1.5'),
            actual_amount=transaction.amount
        )
        alerts_created.append(alert)
    
    # 2. Verificar saldos bajos en cuentas
    from ..accounts.models import Account
    low_balance_accounts = Account.objects.filter(
        user=user,
        is_active=True,
        current_balance__lt=Decimal('100.00')  # Menos de $100
    )
    
    for account in low_balance_accounts:
        # Verificar si ya existe alerta reciente
        existing_alert = BudgetAlert.objects.filter(
            user=user,
            alert_type='account_low',
            related_account=account,
            created_at__gte=today - timedelta(days=7)
        ).first()
        
        if not existing_alert:
            severity = 'critical' if account.current_balance < Decimal('50.00') else 'high'
            alert = BudgetAlert.objects.create(
                user=user,
                alert_type='account_low',
                severity=severity,
                title=f'Saldo bajo en {account.name}',
                message=f'Tu cuenta {account.name} tiene un saldo de solo ${account.current_balance}.',
                related_account=account,
                threshold_amount=Decimal('100.00'),
                actual_amount=account.current_balance
            )
            alerts_created.append(alert)
    
    # 3. Verificar caída en ingresos (comparar con mes anterior)
    current_month_start = today.replace(day=1)
    prev_month_start = (current_month_start - timedelta(days=1)).replace(day=1)
    prev_month_end = current_month_start - timedelta(days=1)
    
    current_income = Transaction.objects.filter(
        user=user,
        type='income',
        date__gte=current_month_start
    ).aggregate(total=Sum('amount'))['total'] or Decimal('0.00')
    
    prev_income = Transaction.objects.filter(
        user=user,
        type='income',
        date__range=[prev_month_start, prev_month_end]
    ).aggregate(total=Sum('amount'))['total'] or Decimal('0.00')
    
    if prev_income > 0 and current_income < prev_income * Decimal('0.7'):  # 30% menos
        alert = BudgetAlert.objects.create(
            user=user,
            alert_type='income_drop',
            severity='high',
            title='Caída significativa en ingresos',
            message=f'Tus ingresos este mes (${current_income}) son 30% menores que el mes anterior (${prev_income}).',
            threshold_amount=prev_income * Decimal('0.7'),
            actual_amount=current_income
        )
        alerts_created.append(alert)
    
    return alerts_created

def cleanup_old_alerts(days_old=30):
    """Limpiar alertas antiguas leídas o descartadas"""
    cutoff_date = timezone.now() - timedelta(days=days_old)
    
    deleted_count = BudgetAlert.objects.filter(
        Q(is_dismissed=True) | Q(is_read=True),
        created_at__lt=cutoff_date
    ).delete()[0]
    
    return deleted_count