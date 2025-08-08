from django.core.management.base import BaseCommand
from django.contrib.auth.models import User
from decimal import Decimal
from datetime import datetime, timedelta

from api.goals.models import FinancialGoal, GoalContribution, GoalMilestone
from api.accounts.models import Account

class Command(BaseCommand):
    help = 'Crear metas financieras demo con contribuciones y hitos'
    
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
        self.stdout.write("🎯 GOALS - Creando metas financieras demo...")
        
        self.create_demo_goals()
        self.print_summary()
    
    def create_demo_goals(self):
        """Crear metas financieras demo con contribuciones"""
        try:
            demo_user = User.objects.filter(username="demo").first()
            if not demo_user:
                self.log_error("Usuario demo no encontrado. Ejecuta primero setup_demo")
                return
            
            # Obtener cuentas demo
            accounts = self.get_demo_accounts(demo_user)
            if not accounts:
                self.log_error("Cuentas demo no encontradas. Ejecuta primero setup_demo_accounts")
                return
            
            # Limpiar metas existentes del demo
            FinancialGoal.objects.filter(user=demo_user).delete()
            self.log_info("Metas demo anteriores eliminadas")
            
            today = datetime.now().date()
            
            # META 1: Vacaciones a Cusco (en progreso)
            goal_vacaciones = FinancialGoal.objects.create(
                user=demo_user,
                title="Vacaciones a Cusco",
                description="Viaje familiar a Machu Picchu para el próximo verano. Incluye vuelos, hotel, tours y gastos personales para 4 días.",
                goal_type="vacation",
                target_amount=Decimal('3500.00'),
                current_amount=Decimal('1200.00'),
                start_date=today - timedelta(days=60),
                target_date=today + timedelta(days=180),  # 6 meses
                monthly_target=Decimal('400.00'),
                associated_account=accounts.get('bbva'),
                priority="medium",
                icon="plane",
                color="#22c55e",
                enable_reminders=True,
                reminder_frequency="weekly"
            )
            
            # Contribuciones para vacaciones
            GoalContribution.objects.create(
                goal=goal_vacaciones,
                user=demo_user,
                amount=Decimal('500.00'),
                contribution_type="manual",
                date=today - timedelta(days=45),
                from_account=accounts['bcp'],
                notes="Primer aporte para vacaciones - bono navideño"
            )
            
            GoalContribution.objects.create(
                goal=goal_vacaciones,
                user=demo_user,
                amount=Decimal('400.00'),
                contribution_type="automatic",
                date=today - timedelta(days=15),
                from_account=accounts['bcp'],
                notes="Aporte automático mensual"
            )
            
            GoalContribution.objects.create(
                goal=goal_vacaciones,
                user=demo_user,
                amount=Decimal('300.00'),
                contribution_type="manual",
                date=today - timedelta(days=5),
                from_account=accounts['bcp'],
                notes="Aporte extra - freelance completado"
            )
            
            # Hitos para vacaciones
            GoalMilestone.objects.create(
                goal=goal_vacaciones,
                title="25% Completado",
                description="Primeros S/. 875 ahorrados",
                target_amount=Decimal('875.00'),
                target_date=today + timedelta(days=30),
                is_completed=True,
                completed_at=datetime.now() - timedelta(days=30),
                icon="flag",
                order=1
            )
            
            GoalMilestone.objects.create(
                goal=goal_vacaciones,
                title="50% Completado", 
                description="S/. 1,750 ahorrados - reservar vuelos",
                target_amount=Decimal('1750.00'),
                target_date=today + timedelta(days=90),
                icon="plane-takeoff",
                order=2
            )
            
            # META 2: Fondo de Emergencia (activa - alta prioridad)
            goal_emergencia = FinancialGoal.objects.create(
                user=demo_user,
                title="Fondo de Emergencia",
                description="6 meses de gastos básicos para emergencias. Calculado en base a gastos promedio mensuales de S/. 3,000.",
                goal_type="emergency_fund",
                target_amount=Decimal('18000.00'),
                current_amount=Decimal('4500.00'),
                start_date=today - timedelta(days=90),
                target_date=today + timedelta(days=300),  # 10 meses más
                monthly_target=Decimal('1500.00'),
                associated_account=accounts.get('bbva'),
                priority="high",
                icon="shield-check",
                color="#ef4444",
                enable_reminders=True,
                reminder_frequency="monthly"
            )
            
            # Contribuciones para fondo emergencia
            GoalContribution.objects.create(
                goal=goal_emergencia,
                user=demo_user,
                amount=Decimal('2000.00'),
                contribution_type="manual",
                date=today - timedelta(days=85),
                from_account=accounts['bcp'],
                notes="Aporte inicial - reestructuración financiera"
            )
            
            GoalContribution.objects.create(
                goal=goal_emergencia,
                user=demo_user,
                amount=Decimal('1500.00'),
                contribution_type="automatic",
                date=today - timedelta(days=55),
                from_account=accounts['bcp'],
                notes="Aporte automático mes 1"
            )
            
            GoalContribution.objects.create(
                goal=goal_emergencia,
                user=demo_user,
                amount=Decimal('1000.00'),
                contribution_type="automatic",
                date=today - timedelta(days=25),
                from_account=accounts['bcp'],
                notes="Aporte automático mes 2"
            )
            
            # Hitos para fondo emergencia
            GoalMilestone.objects.create(
                goal=goal_emergencia,
                title="1 mes de gastos",
                description="S/. 3,000 - primer hito de emergencia",
                target_amount=Decimal('3000.00'),
                target_date=today - timedelta(days=60),
                is_completed=True,
                completed_at=datetime.now() - timedelta(days=60),
                icon="shield",
                order=1
            )
            
            GoalMilestone.objects.create(
                goal=goal_emergencia,
                title="3 meses de gastos",
                description="S/. 9,000 - seguridad básica alcanzada",
                target_amount=Decimal('9000.00'),
                target_date=today + timedelta(days=60),
                icon="shield-check",
                order=2
            )
            
            # META 3: Auto nuevo (a largo plazo)
            goal_auto = FinancialGoal.objects.create(
                user=demo_user,
                title="Auto Nuevo",
                description="Cuota inicial para Toyota Yaris 2025. Total del auto S/. 65,000, necesitamos 40% de inicial.",
                goal_type="purchase",
                target_amount=Decimal('25000.00'),
                current_amount=Decimal('3200.00'),
                start_date=today - timedelta(days=30),
                target_date=today + timedelta(days=720),  # 2 años
                monthly_target=Decimal('900.00'),
                priority="medium",
                icon="car",
                color="#3b82f6",
                enable_reminders=True,
                reminder_frequency="monthly"
            )
            
            # Contribuciones para auto
            GoalContribution.objects.create(
                goal=goal_auto,
                user=demo_user,
                amount=Decimal('2000.00'),
                contribution_type="manual",
                date=today - timedelta(days=25),
                from_account=accounts['bbva'],
                notes="Aporte inicial - venta de auto anterior"
            )
            
            GoalContribution.objects.create(
                goal=goal_auto,
                user=demo_user,
                amount=Decimal('600.00'),
                contribution_type="automatic",
                date=today - timedelta(days=10),
                from_account=accounts['bcp'],
                notes="Primer aporte mensual automático"
            )
            
            GoalContribution.objects.create(
                goal=goal_auto,
                user=demo_user,
                amount=Decimal('600.00'),
                contribution_type="automatic", 
                date=today - timedelta(days=5),
                from_account=accounts['bcp'],
                notes="Aporte mensual freelance"
            )
            
            # META 4: Educación/Curso (completada recientemente)
            goal_curso = FinancialGoal.objects.create(
                user=demo_user,
                title="Curso de Python Avanzado",
                description="Bootcamp intensivo de desarrollo Python y Django para mejorar habilidades profesionales.",
                goal_type="education",
                target_amount=Decimal('1200.00'),
                current_amount=Decimal('1200.00'),
                start_date=today - timedelta(days=120),
                target_date=today - timedelta(days=30),
                monthly_target=Decimal('400.00'),
                priority="high",
                status="completed",
                completed_at=datetime.now() - timedelta(days=30),
                icon="graduation-cap",
                color="#8b5cf6"
            )
            
            # Contribuciones para curso (ya completado)
            GoalContribution.objects.create(
                goal=goal_curso,
                user=demo_user,
                amount=Decimal('600.00'),
                contribution_type="manual",
                date=today - timedelta(days=90),
                from_account=accounts['bcp'],
                notes="Primera cuota del curso"
            )
            
            GoalContribution.objects.create(
                goal=goal_curso,
                user=demo_user,
                amount=Decimal('600.00'),
                contribution_type="manual",
                date=today - timedelta(days=60),
                from_account=accounts['bcp'],
                notes="Segunda y última cuota del curso"
            )
            
            # Actualizar progreso de todas las metas
            for goal in FinancialGoal.objects.filter(user=demo_user):
                goal.update_progress()
            
            goal_count = FinancialGoal.objects.filter(user=demo_user).count()
            contribution_count = GoalContribution.objects.filter(user=demo_user).count()
            milestone_count = GoalMilestone.objects.filter(goal__user=demo_user).count()
            
            self.log_success(f"Metas financieras demo creadas: {goal_count}")
            self.log_success(f"Contribuciones creadas: {contribution_count}")
            self.log_success(f"Hitos creados: {milestone_count}")
            
        except Exception as e:
            self.log_error(f"Error al crear metas demo: {e}")
    
    def get_demo_accounts(self, user):
        """Obtener cuentas del usuario demo"""
        try:
            accounts = {}
            accounts['bcp'] = Account.objects.get(user=user, bank_name="BCP")
            accounts['bbva'] = Account.objects.get(user=user, bank_name="BBVA") 
            accounts['interbank'] = Account.objects.get(user=user, bank_name="Interbank")
            accounts['efectivo'] = Account.objects.get(user=user, account_type="cash")
            accounts['yape'] = Account.objects.get(user=user, account_type="digital_wallet")
            return accounts
        except Account.DoesNotExist:
            return {}
    
    def print_summary(self):
        """Mostrar resumen final"""
        self.stdout.write("\n" + "="*50)
        self.stdout.write(self.style.SUCCESS("🎯 METAS FINANCIERAS DEMO - COMPLETADO"))
        self.stdout.write("="*50)
        self.stdout.write(f"✅ Operaciones exitosas: {self.success_count}")
        self.stdout.write(f"❌ Errores encontrados: {self.error_count}")
        
        try:
            demo_user = User.objects.get(username="demo")
            
            # Mostrar resumen de metas
            self.stdout.write("\n🎯 RESUMEN DE METAS:")
            for goal in FinancialGoal.objects.filter(user=demo_user):
                progress = goal.progress_percentage
                status_emoji = {
                    'active': '🔥',
                    'completed': '✅',
                    'paused': '⏸️',
                    'cancelled': '❌',
                    'overdue': '⚠️'
                }.get(goal.status, '📋')
                
                self.stdout.write(
                    f"   {status_emoji} {goal.title}: {progress:.1f}% "
                    f"(S/.{goal.current_amount}/S/.{goal.target_amount})"
                )
                
        except Exception as e:
            self.stdout.write(f"Error en resumen: {e}")
        
        self.stdout.write("\n🔧 Próximo paso:")
        self.stdout.write("   python manage.py setup_all (para ejecutar todo)")
        self.stdout.write("="*50)