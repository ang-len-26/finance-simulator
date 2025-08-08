from django.core.management.base import BaseCommand
from django.contrib.auth.models import User
from django.utils import timezone
from datetime import datetime, timedelta
from decimal import Decimal
from django.db.models import Sum, Count, Q

from api.analytics.models import FinancialMetric
from api.transactions.models import Transaction

class Command(BaseCommand):
    help = 'Generar métricas financieras para todos los usuarios'
    
    def add_arguments(self, parser):
        parser.add_argument(
            '--period-type',
            type=str,
            default='monthly',
            choices=['monthly', 'quarterly', 'yearly'],
            help='Tipo de período para generar'
        )
        parser.add_argument(
            '--months-back',
            type=int,
            default=12,
            help='Número de meses hacia atrás para generar'
        )
        parser.add_argument(
            '--user-id',
            type=int,
            help='ID específico de usuario (opcional)'
        )
    
    def handle(self, *args, **options):
        period_type = options['period_type']
        months_back = options['months_back']
        user_id = options.get('user_id')
        
        # Filtrar usuarios
        if user_id:
            users = User.objects.filter(id=user_id)
        else:
            users = User.objects.filter(is_active=True)
        
        self.stdout.write(f'Generando métricas {period_type} para {users.count()} usuarios...')
        
        total_created = 0
        
        for user in users:
            created_count = self.generate_user_metrics(user, period_type, months_back)
            total_created += created_count
            
            self.stdout.write(f'Usuario {user.username}: {created_count} métricas generadas')
        
        self.stdout.write(
            self.style.SUCCESS(f'Completado! {total_created} métricas generadas en total')
        )
    
    def generate_user_metrics(self, user, period_type, months_back):
        """Generar métricas para un usuario específico"""
        created_count = 0
        today = timezone.now().date()
        
        for i in range(months_back):
            if period_type == 'monthly':
                # Calcular fechas del mes
                target_date = today.replace(day=1) - timedelta(days=i*30)
                period_start = target_date.replace(day=1)
                
                # Último día del mes
                if target_date.month == 12:
                    next_month = target_date.replace(year=target_date.year + 1, month=1, day=1)
                else:
                    next_month = target_date.replace(month=target_date.month + 1, day=1)
                period_end = next_month - timedelta(days=1)
                
            elif period_type == 'quarterly':
                # Lógica para trimestres
                quarter = ((today.month - 1) // 3) - i
                year = today.year
                
                if quarter < 0:
                    quarter = 4 + quarter
                    year -= 1
                
                start_month = quarter * 3 + 1
                period_start = datetime(year, start_month, 1).date()
                
                if start_month + 2 == 12:
                    period_end = datetime(year, 12, 31).date()
                else:
                    period_end = datetime(year, start_month + 3, 1).date() - timedelta(days=1)
            
            # Verificar si ya existe
            existing = FinancialMetric.objects.filter(
                user=user,
                period_type=period_type,
                period_start=period_start,
                period_end=period_end
            ).first()
            
            if existing:
                continue
            
            # Calcular métricas
            transactions = Transaction.objects.filter(
                user=user,
                date__range=[period_start, period_end]
            )
            
            if not transactions.exists():
                continue
            
            totals = transactions.aggregate(
                income=Sum('amount', filter=Q(type='income')),
                expenses=Sum('amount', filter=Q(type='expense')),
                count=Count('id')
            )
            
            total_income = totals['income'] or Decimal('0.00')
            total_expenses = totals['expenses'] or Decimal('0.00')
            
            # Crear métrica
            metric = FinancialMetric.objects.create(
                user=user,
                period_type=period_type,
                period_start=period_start,
                period_end=period_end,
                total_income=total_income,
                total_expenses=total_expenses,
                net_balance=total_income - total_expenses,
                transaction_count=totals['count']
            )
            
            created_count += 1
        
        return created_count