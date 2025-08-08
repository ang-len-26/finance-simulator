from django.core.management.base import BaseCommand
from django.contrib.auth.models import User
from django.utils import timezone
from decimal import Decimal
from datetime import timedelta

from api.analytics.models import FinancialMetric, CategorySummary, BudgetAlert
from api.transactions.models import Category
from api.accounts.models import Account

class Command(BaseCommand):
    help = 'Configurar sistema de analytics y métricas iniciales'
    
    def __init__(self):
        super().__init__()
        self.success_count = 0
        self.error_count = 0
    
    def log_success(self, message):
        self.stdout.write(self.style.SUCCESS(f"✅ {message}"))
        self.success_count += 1
    
    def log_error(self, message):
        self.stdout.write(self.style.ERROR(f"❌ {message}"))
        self.error_count += 1
    
    def log_info(self, message):
        self.stdout.write(self.style.WARNING(f"ℹ️  {message}"))
    
    def handle(self, *args, **options):
        self.stdout.write("📊 ANALYTICS - Configurando sistema de métricas...")
        
        self.setup_demo_metrics()
        self.setup_demo_category_summaries()
        self.setup_demo_alerts()
        self.print_summary()
    
    def setup_demo_metrics(self):
        """Crear métricas financieras para usuario demo"""
        self.stdout.write("\n📈 Creando métricas financieras demo...")
        
        try:
            demo_user = User.objects.filter(username="demo").first()
            if not demo_user:
                self.log_info("Usuario demo no encontrado, saltando métricas demo")
                return
            
            today = timezone.now().date()
            
            # Métricas mensuales de los últimos 3 meses
            monthly_metrics = [
                {
                    'period_type': 'monthly',
                    'period_start': today.replace(day=1) - timedelta(days=60),
                    'period_end': today.replace(day=1) - timedelta(days=31),
                    'total_income': Decimal('5200.00'),
                    'total_expenses': Decimal('2850.00'),
                    'net_balance': Decimal('2350.00'),
                    'checking_balance': Decimal('8500.00'),
                    'savings_balance': Decimal('12000.00'),
                    'investment_balance': Decimal('3500.00'),
                    'transaction_count': 28,
                    'top_expense_amount': Decimal('450.00')
                },
                {
                    'period_type': 'monthly',
                    'period_start': today.replace(day=1) - timedelta(days=31),
                    'period_end': today.replace(day=1) - timedelta(days=1),
                    'total_income': Decimal('4800.00'),
                    'total_expenses': Decimal('3200.00'),
                    'net_balance': Decimal('1600.00'),
                    'checking_balance': Decimal('8200.00'),
                    'savings_balance': Decimal('15200.00'),
                    'investment_balance': Decimal('4300.00'),
                    'transaction_count': 35,
                    'top_expense_amount': Decimal('520.00')
                },
                {
                    'period_type': 'monthly',
                    'period_start': today.replace(day=1),
                    'period_end': today,
                    'total_income': Decimal('4800.00'),
                    'total_expenses': Decimal('2100.00'),
                    'net_balance': Decimal('2700.00'),
                    'checking_balance': Decimal('8800.00'),
                    'savings_balance': Decimal('16500.00'),
                    'investment_balance': Decimal('5100.00'),
                    'transaction_count': 18,
                    'top_expense_amount': Decimal('280.00')
                }
            ]
            
            # Obtener categoría más común para gastos
            alimentacion_category = Category.objects.filter(slug='alimentacion').first()
            
            created_count = 0
            for metric_data in monthly_metrics:
                metric, created = FinancialMetric.objects.get_or_create(
                    user=demo_user,
                    period_type=metric_data['period_type'],
                    period_start=metric_data['period_start'],
                    period_end=metric_data['period_end'],
                    defaults={
                        **metric_data,
                        'top_expense_category': alimentacion_category
                    }
                )
                if created:
                    created_count += 1
            
            # Métricas semanales actuales
            week_start = today - timedelta(days=today.weekday())
            week_end = week_start + timedelta(days=6)
            
            FinancialMetric.objects.get_or_create(
                user=demo_user,
                period_type='weekly',
                period_start=week_start,
                period_end=week_end,
                defaults={
                    'total_income': Decimal('1200.00'),
                    'total_expenses': Decimal('650.00'),
                    'net_balance': Decimal('550.00'),
                    'checking_balance': Decimal('8800.00'),
                    'savings_balance': Decimal('16500.00'),
                    'transaction_count': 8,
                    'top_expense_category': alimentacion_category,
                    'top_expense_amount': Decimal('180.00')
                }
            )
            
            self.log_success(f"Métricas financieras demo creadas: {created_count + 1}")
            
        except Exception as e:
            self.log_error(f"Error al crear métricas demo: {e}")
    
    def setup_demo_category_summaries(self):
        """Crear resúmenes de categorías para usuario demo"""
        self.stdout.write("\n📂 Creando resúmenes de categorías demo...")
        
        try:
            demo_user = User.objects.filter(username="demo").first()
            if not demo_user:
                self.log_info("Usuario demo no encontrado, saltando resúmenes")
                return
            
            today = timezone.now().date()
            month_start = today.replace(day=1)
            month_end = today
            
            # Obtener cuentas demo
            bcp_account = Account.objects.filter(user=demo_user, bank_name="BCP").first()
            
            # Crear resúmenes para categorías principales
            category_summaries = [
                {
                    'category_slug': 'alimentacion',
                    'total_amount': Decimal('580.50'),
                    'transaction_count': 12,
                    'average_amount': Decimal('48.38'),
                    'previous_period_amount': Decimal('620.00'),
                    'percentage_change': Decimal('-6.37')
                },
                {
                    'category_slug': 'transporte',
                    'total_amount': Decimal('285.00'),
                    'transaction_count': 8,
                    'average_amount': Decimal('35.63'),
                    'previous_period_amount': Decimal('245.00'),
                    'percentage_change': Decimal('16.33')
                },
                {
                    'category_slug': 'servicios',
                    'total_amount': Decimal('124.90'),
                    'transaction_count': 3,
                    'average_amount': Decimal('41.63'),
                    'previous_period_amount': Decimal('98.50'),
                    'percentage_change': Decimal('26.80')
                },
                {
                    'category_slug': 'entretenimiento',
                    'total_amount': Decimal('180.00'),
                    'transaction_count': 5,
                    'average_amount': Decimal('36.00'),
                    'previous_period_amount': Decimal('220.00'),
                    'percentage_change': Decimal('-18.18')
                },
                {
                    'category_slug': 'salario',
                    'total_amount': Decimal('4500.00'),
                    'transaction_count': 1,
                    'average_amount': Decimal('4500.00'),
                    'previous_period_amount': Decimal('4500.00'),
                    'percentage_change': Decimal('0.00')
                }
            ]
            
            created_count = 0
            for summary_data in category_summaries:
                category = Category.objects.filter(slug=summary_data['category_slug']).first()
                if category:
                    summary, created = CategorySummary.objects.get_or_create(
                        user=demo_user,
                        category=category,
                        period_start=month_start,
                        period_end=month_end,
                        period_type='monthly',
                        defaults={
                            'total_amount': summary_data['total_amount'],
                            'transaction_count': summary_data['transaction_count'],
                            'average_amount': summary_data['average_amount'],
                            'previous_period_amount': summary_data['previous_period_amount'],
                            'percentage_change': summary_data['percentage_change'],
                            'most_used_account': bcp_account
                        }
                    )
                    if created:
                        created_count += 1
            
            self.log_success(f"Resúmenes de categorías demo creados: {created_count}")
            
        except Exception as e:
            self.log_error(f"Error al crear resúmenes de categorías: {e}")
    
    def setup_demo_alerts(self):
        """Crear alertas de ejemplo para usuario demo"""
        self.stdout.write("\n🚨 Creando alertas demo...")
        
        try:
            demo_user = User.objects.filter(username="demo").first()
            if not demo_user:
                self.log_info("Usuario demo no encontrado, saltando alertas")
                return
            
            # Obtener categorías y cuentas
            alimentacion_category = Category.objects.filter(slug='alimentacion').first()
            bcp_account = Account.objects.filter(user=demo_user, bank_name="BCP").first()
            
            # Crear alertas de ejemplo
            demo_alerts = [
                {
                    'alert_type': 'category_spike',
                    'severity': 'medium',
                    'title': 'Gasto Alto en Alimentación',
                    'message': 'Has gastado 15% más de lo usual en alimentación este mes.',
                    'related_category': alimentacion_category,
                    'threshold_amount': Decimal('500.00'),
                    'actual_amount': Decimal('580.50')
                },
                {
                    'alert_type': 'budget_exceeded',
                    'severity': 'high',
                    'title': 'Presupuesto Mensual Superado',
                    'message': 'Has superado tu presupuesto mensual de gastos por S/.150.',
                    'threshold_amount': Decimal('2000.00'),
                    'actual_amount': Decimal('2150.00')
                },
                {
                    'alert_type': 'account_low',
                    'severity': 'low',
                    'title': 'Saldo Bajo en Efectivo',
                    'message': 'Tu cuenta de efectivo está por debajo de S/.500.',
                    'related_account': Account.objects.filter(
                        user=demo_user, 
                        account_type='cash'
                    ).first(),
                    'threshold_amount': Decimal('500.00'),
                    'actual_amount': Decimal('200.00')
                }
            ]
            
            created_count = 0
            for alert_data in demo_alerts:
                alert, created = BudgetAlert.objects.get_or_create(
                    user=demo_user,
                    alert_type=alert_data['alert_type'],
                    title=alert_data['title'],
                    defaults=alert_data
                )
                if created:
                    created_count += 1
            
            self.log_success(f"Alertas demo creadas: {created_count}")
            
        except Exception as e:
            self.log_error(f"Error al crear alertas demo: {e}")
    
    def print_summary(self):
        """Mostrar resumen de configuración analytics"""
        self.stdout.write("\n" + "="*50)
        self.stdout.write("📊 ANALYTICS - CONFIGURACIÓN COMPLETADA")
        self.stdout.write("="*50)
        self.stdout.write(f"✅ Operaciones exitosas: {self.success_count}")
        self.stdout.write(f"❌ Errores encontrados: {self.error_count}")
        
        if self.success_count > 0:
            self.stdout.write("\n🎯 Sistema de Analytics configurado:")
            self.stdout.write("   • Métricas financieras demo creadas")
            self.stdout.write("   • Resúmenes de categorías configurados")
            self.stdout.write("   • Alertas de ejemplo activadas")
            self.stdout.write("\n💡 Comandos útiles:")
            self.stdout.write("   python manage.py generate_metrics")
        
        self.stdout.write("="*50)