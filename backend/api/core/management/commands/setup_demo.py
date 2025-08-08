from django.core.management.base import BaseCommand
from django.contrib.auth.models import User
from decimal import Decimal
from datetime import timedelta
from django.utils import timezone

from api.core.models import UserProfile
from api.accounts.models import Account
from api.transactions.models import Transaction, Category
from api.goals.models import FinancialGoal, GoalContribution

class Command(BaseCommand):
    help = 'Crear usuario demo con datos completos de muestra'
    
    def __init__(self):
        super().__init__()
        self.success_count = 0
        self.error_count = 0
        self.demo_user = None
        self.cuentas = {}
    
    def log_success(self, message):
        self.stdout.write(self.style.SUCCESS(f"✅ {message}"))
        self.success_count += 1
    
    def log_error(self, message):
        self.stdout.write(self.style.ERROR(f"❌ {message}"))
        self.error_count += 1
    
    def log_info(self, message):
        self.stdout.write(self.style.WARNING(f"ℹ️  {message}"))
    
    def handle(self, *args, **options):
        self.stdout.write("🎭 DEMO - Creando usuario demo completo...")
        
        self.create_demo_user()
        if self.demo_user:
            self.create_demo_accounts()
            self.create_demo_transactions()
            self.create_demo_goals()
            self.update_account_balances()
        
        self.print_summary()
    
    def create_demo_user(self):
        """Crear usuario demo con perfil"""
        self.stdout.write("\n👤 Creando usuario demo...")
        try:
            # Verificar si ya existe y limpiar datos anteriores
            if User.objects.filter(username="demo").exists():
                self.log_info("Usuario demo ya existe, limpiando datos anteriores...")
                self.demo_user = User.objects.get(username="demo")
                
                # Limpiar datos anteriores
                Account.objects.filter(user=self.demo_user).delete()
                Transaction.objects.filter(user=self.demo_user).delete()
                FinancialGoal.objects.filter(user=self.demo_user).delete()
                
                # Actualizar perfil
                profile, _ = UserProfile.objects.get_or_create(
                    user=self.demo_user,
                    defaults={
                        'is_demo': True,
                        'demo_expires': timezone.now() + timedelta(days=30)
                    }
                )
                if not profile.is_demo:
                    profile.is_demo = True
                    profile.demo_expires = timezone.now() + timedelta(days=30)
                    profile.save()
                    
            else:
                # Crear nuevo usuario demo
                self.demo_user = User.objects.create_user(
                    username="demo",
                    email="demo@fintrack.com",
                    password="demo123",
                    first_name="Usuario",
                    last_name="Demo"
                )
                
                # Crear perfil de usuario demo
                UserProfile.objects.create(
                    user=self.demo_user,
                    is_demo=True,
                    demo_expires=timezone.now() + timedelta(days=30)
                )
            
            self.log_success("Usuario demo configurado correctamente")
            self.log_info("Credenciales - Username: demo, Password: demo123")
            
        except Exception as e:
            self.log_error(f"Error al crear usuario demo: {e}")
    
    def create_demo_accounts(self):
        """Crear cuentas demo realistas"""
        self.stdout.write("\n💰 Creando cuentas demo...")
        try:
            accounts_data = [
                {
                    'key': 'bcp_corriente',
                    'name': 'Cuenta Corriente',
                    'bank_name': 'BCP',
                    'account_number': '****1234',
                    'account_type': 'checking',
                    'initial_balance': Decimal('8500.00'),
                    'currency': 'PEN'
                },
                {
                    'key': 'bbva_ahorros',
                    'name': 'Cuenta Ahorros',
                    'bank_name': 'BBVA',
                    'account_number': '****5678',
                    'account_type': 'savings',
                    'initial_balance': Decimal('15200.00'),
                    'currency': 'PEN'
                },
                {
                    'key': 'interbank_credito',
                    'name': 'Tarjeta Crédito',
                    'bank_name': 'Interbank',
                    'account_number': '****9012',
                    'account_type': 'credit',
                    'initial_balance': Decimal('0.00'),
                    'currency': 'PEN'
                },
                {
                    'key': 'efectivo',
                    'name': 'Efectivo',
                    'bank_name': '',
                    'account_number': '',
                    'account_type': 'cash',
                    'initial_balance': Decimal('850.00'),
                    'currency': 'PEN'
                },
                {
                    'key': 'yape',
                    'name': 'Yape',
                    'bank_name': 'BCP',
                    'account_number': '',
                    'account_type': 'digital_wallet',
                    'initial_balance': Decimal('280.00'),
                    'currency': 'PEN'
                },
                {
                    'key': 'scotiabank_usd',
                    'name': 'Ahorros USD',
                    'bank_name': 'Scotiabank',
                    'account_number': '****3456',
                    'account_type': 'savings',
                    'initial_balance': Decimal('1200.00'),
                    'currency': 'USD'
                }
            ]
            
            for account_data in accounts_data:
                key = account_data.pop('key')
                account = Account.objects.create(
                    user=self.demo_user,
                    **account_data
                )
                self.cuentas[key] = account
            
            self.log_success(f"Cuentas demo creadas: {len(self.cuentas)}")
            
        except Exception as e:
            self.log_error(f"Error al crear cuentas demo: {e}")
    
    def create_demo_transactions(self):
        """Crear transacciones demo realistas de los últimos 3 meses"""
        self.stdout.write("\n💸 Creando transacciones demo...")
        try:
            # Obtener categorías disponibles
            categorias = {
                'salario': Category.objects.filter(slug='salario').first(),
                'freelance': Category.objects.filter(slug='freelance').first(),
                'alimentacion': Category.objects.filter(slug='alimentacion').first(),
                'transporte': Category.objects.filter(slug='transporte').first(),
                'servicios': Category.objects.filter(slug='servicios').first(),
                'entretenimiento': Category.objects.filter(slug='entretenimiento').first(),
                'salud': Category.objects.filter(slug='salud').first(),
                'compras': Category.objects.filter(slug='compras').first(),
                'inversiones': Category.objects.filter(slug='inversiones').first(),
            }
            
            today = timezone.now().date()
            
            # Transacciones de muestra - últimos 3 meses
            transacciones = [
                # === ENERO 2025 ===
                # Ingresos
                {
                    'title': 'Sueldo Enero 2025',
                    'amount': Decimal('4800.00'),
                    'type': 'income',
                    'date': today - timedelta(days=32),
                    'to_account': self.cuentas['bcp_corriente'],
                    'category': categorias['salario'],
                    'description': 'Salario mensual - Empresa TechCorp SAC',
                    'reference_number': 'SUE-202501-001'
                },
                {
                    'title': 'Freelance App Móvil',
                    'amount': Decimal('1500.00'),
                    'type': 'income',
                    'date': today - timedelta(days=28),
                    'to_account': self.cuentas['bcp_corriente'],
                    'category': categorias['freelance'],
                    'description': 'Desarrollo app móvil para startup',
                    'reference_number': 'FREE-001'
                },
                
                # Gastos Enero
                {
                    'title': 'Supermercado Tottus',
                    'amount': Decimal('320.80'),
                    'type': 'expense',
                    'date': today - timedelta(days=30),
                    'from_account': self.cuentas['bcp_corriente'],
                    'category': categorias['alimentacion'],
                    'location': 'Lima Centro',
                    'tags': ['supermercado', 'familia']
                },
                {
                    'title': 'Recarga Tarjeta Metro',
                    'amount': Decimal('50.00'),
                    'type': 'expense',
                    'date': today - timedelta(days=29),
                    'from_account': self.cuentas['bcp_corriente'],
                    'category': categorias['transporte'],
                    'is_recurring': True,
                    'recurring_frequency': 'weekly'
                },
                {
                    'title': 'Netflix + Spotify',
                    'amount': Decimal('44.90'),
                    'type': 'expense',
                    'date': today - timedelta(days=28),
                    'from_account': self.cuentas['bcp_corriente'],
                    'category': categorias['servicios'],
                    'is_recurring': True,
                    'recurring_frequency': 'monthly',
                    'tags': ['suscripción']
                },
                
                # === FEBRERO 2025 ===
                # Ingresos
                {
                    'title': 'Sueldo Febrero 2025',
                    'amount': Decimal('4800.00'),
                    'type': 'income',
                    'date': today - timedelta(days=2),
                    'to_account': self.cuentas['bcp_corriente'],
                    'category': categorias['salario'],
                    'description': 'Salario mensual - Empresa TechCorp SAC',
                    'reference_number': 'SUE-202502-001'
                },
                
                # Gastos Febrero
                {
                    'title': 'Cena Romántica - Valentín',
                    'amount': Decimal('185.00'),
                    'type': 'expense',
                    'date': today - timedelta(days=7),
                    'from_account': self.cuentas['interbank_credito'],
                    'category': categorias['entretenimiento'],
                    'location': 'Miraflores - Restaurante Central',
                    'tags': ['san_valentin', 'pareja']
                },
                {
                    'title': 'Consulta Médica',
                    'amount': Decimal('120.00'),
                    'type': 'expense',
                    'date': today - timedelta(days=5),
                    'from_account': self.cuentas['bcp_corriente'],
                    'category': categorias['salud'],
                    'location': 'Clínica Anglo Americana',
                    'tags': ['salud', 'consulta']
                },
                {
                    'title': 'Compras Mall',
                    'amount': Decimal('280.50'),
                    'type': 'expense',
                    'date': today - timedelta(days=3),
                    'from_account': self.cuentas['bcp_corriente'],
                    'category': categorias['compras'],
                    'location': 'Jockey Plaza',
                    'tags': ['ropa', 'personal']
                },
                
                # Transferencias
                {
                    'title': 'Ahorro Mensual',
                    'amount': Decimal('1200.00'),
                    'type': 'transfer',
                    'date': today - timedelta(days=25),
                    'from_account': self.cuentas['bcp_corriente'],
                    'to_account': self.cuentas['bbva_ahorros'],
                    'description': 'Transferencia automática mensual a ahorros',
                    'tags': ['ahorro', 'automatico']
                },
                {
                    'title': 'Inversión Fondo Mutuo',
                    'amount': Decimal('800.00'),
                    'type': 'investment',
                    'date': today - timedelta(days=20),
                    'from_account': self.cuentas['bbva_ahorros'],
                    'category': categorias['inversiones'],
                    'description': 'Fondo mutuo BCP - Perfil conservador',
                    'reference_number': 'INV-BCP-001'
                },
                
                # Gastos menores con Yape/Efectivo
                {
                    'title': 'Café Starbucks',
                    'amount': Decimal('15.50'),
                    'type': 'expense',
                    'date': today - timedelta(days=1),
                    'from_account': self.cuentas['yape'],
                    'category': categorias['alimentacion'],
                    'location': 'San Isidro',
                    'tags': ['café', 'trabajo']
                },
                {
                    'title': 'Taxi a casa',
                    'amount': Decimal('35.00'),
                    'type': 'expense',
                    'date': today - timedelta(days=1),
                    'from_account': self.cuentas['efectivo'],
                    'category': categorias['transporte'],
                    'location': 'Lima Centro - San Borja'
                },
                
                # Transacciones en USD
                {
                    'title': 'Compra Amazon US',
                    'amount': Decimal('89.99'),
                    'type': 'expense',
                    'date': today - timedelta(days=12),
                    'from_account': self.cuentas['scotiabank_usd'],
                    'category': categorias['compras'],
                    'description': 'Libros técnicos programación',
                    'location': 'Online - Amazon.com',
                    'tags': ['educacion', 'libros', 'usd']
                }
            ]
            
            # Crear transacciones
            created_count = 0
            for trans_data in transacciones:
                try:
                    transaction = Transaction.objects.create(
                        user=self.demo_user,
                        **trans_data
                    )
                    created_count += 1
                except Exception as e:
                    self.log_error(f"Error creando transacción {trans_data['title']}: {e}")
            
            self.log_success(f"Transacciones demo creadas: {created_count}")
            
        except Exception as e:
            self.log_error(f"Error general en transacciones demo: {e}")
    
    def create_demo_goals(self):
        """Crear metas financieras demo con progreso realista"""
        self.stdout.write("\n🎯 Creando metas financieras demo...")
        try:
            today = timezone.now().date()
            
            # Meta 1: Vacaciones a Europa (en progreso activo)
            goal_europa = FinancialGoal.objects.create(
                user=self.demo_user,
                title="Vacaciones a Europa 2025",
                description="Viaje de 15 días por España, Francia e Italia. Incluye vuelos, hoteles y gastos.",
                goal_type="vacation",
                target_amount=Decimal('8500.00'),
                current_amount=Decimal('3200.00'),
                start_date=today - timedelta(days=120),
                target_date=today + timedelta(days=150),  # 5 meses
                monthly_target=Decimal('1100.00'),
                associated_account=self.cuentas['bbva_ahorros'],
                priority="high",
                icon="plane",
                color="#22c55e",
                enable_reminders=True,
                reminder_frequency="weekly"
            )
            
            # Contribuciones para Europa
            contributions_europa = [
                {
                    'amount': Decimal('1000.00'),
                    'contribution_type': 'manual',
                    'date': today - timedelta(days=90),
                    'from_account': self.cuentas['bcp_corriente'],
                    'notes': 'Aporte inicial para vacaciones'
                },
                {
                    'amount': Decimal('800.00'),
                    'contribution_type': 'automatic',
                    'date': today - timedelta(days=60),
                    'from_account': self.cuentas['bcp_corriente'],
                    'notes': 'Aporte automático mensual'
                },
                {
                    'amount': Decimal('700.00'),
                    'contribution_type': 'manual',
                    'date': today - timedelta(days=30),
                    'from_account': self.cuentas['bcp_corriente'],
                    'notes': 'Aporte extra de freelance'
                },
                {
                    'amount': Decimal('700.00'),
                    'contribution_type': 'automatic',
                    'date': today - timedelta(days=5),
                    'from_account': self.cuentas['bcp_corriente'],
                    'notes': 'Aporte mensual febrero'
                }
            ]
            
            for contrib_data in contributions_europa:
                GoalContribution.objects.create(
                    goal=goal_europa,
                    user=self.demo_user,
                    **contrib_data
                )
            
            # Meta 2: Fondo de Emergencia (en construcción)
            goal_emergencia = FinancialGoal.objects.create(
                user=self.demo_user,
                title="Fondo de Emergencia",
                description="Reserva de 6 meses de gastos para situaciones imprevistas (pérdida de trabajo, salud, etc.)",
                goal_type="emergency_fund",
                target_amount=Decimal('24000.00'),
                current_amount=Decimal('8500.00'),
                start_date=today - timedelta(days=180),
                target_date=today + timedelta(days=365),  # 1 año
                monthly_target=Decimal('1300.00'),
                associated_account=self.cuentas['bbva_ahorros'],
                priority="critical",
                icon="shield-check",
                color="#ef4444",
                enable_reminders=True,
                reminder_frequency="monthly"
            )
            
            # Contribuciones para fondo emergencia
            GoalContribution.objects.create(
                goal=goal_emergencia,
                user=self.demo_user,
                amount=Decimal('5000.00'),
                contribution_type='manual',
                date=today - timedelta(days=150),
                from_account=self.cuentas['bcp_corriente'],
                notes='Aporte inicial para fondo de emergencia'
            )
            
            GoalContribution.objects.create(
                goal=goal_emergencia,
                user=self.demo_user,
                amount=Decimal('3500.00'),
                contribution_type='transfer',
                date=today - timedelta(days=45),
                from_account=self.cuentas['bcp_corriente'],
                notes='Transferencia de bonificación anual'
            )
            
            # Meta 3: Auto Nuevo (largo plazo)
            goal_auto = FinancialGoal.objects.create(
                user=self.demo_user,
                title="Auto Toyota Corolla 2024",
                description="Cuota inicial para auto nuevo. Modelo: Toyota Corolla Cross Híbrido 2024",
                goal_type="purchase",
                target_amount=Decimal('35000.00'),
                current_amount=Decimal('12500.00'),
                start_date=today - timedelta(days=60),
                target_date=today + timedelta(days=540),  # 18 meses
                monthly_target=Decimal('1250.00'),
                priority="medium",
                icon="car",
                color="#3b82f6",
                enable_reminders=True,
                reminder_frequency="monthly"
            )
            
            # Meta 4: Educación/Certificación (completada)
            goal_educacion = FinancialGoal.objects.create(
                user=self.demo_user,
                title="Certificación AWS Cloud Practitioner",
                description="Curso y examen de certificación AWS para desarrollo profesional",
                goal_type="education",
                target_amount=Decimal('1200.00'),
                current_amount=Decimal('1200.00'),
                start_date=today - timedelta(days=90),
                target_date=today - timedelta(days=15),
                monthly_target=Decimal('400.00'),
                priority="medium",
                icon="graduation-cap",
                color="#8b5cf6",
                status="completed",
                completed_at=timezone.now() - timedelta(days=15)
            )
            
            GoalContribution.objects.create(
                goal=goal_educacion,
                user=self.demo_user,
                amount=Decimal('1200.00'),
                contribution_type='manual',
                date=today - timedelta(days=30),
                from_account=self.cuentas['bcp_corriente'],
                notes='Pago completo curso AWS + examen'
            )
            
            self.log_success("4 metas financieras demo creadas con contribuciones")
            
        except Exception as e:
            self.log_error(f"Error al crear metas demo: {e}")
    
    def update_account_balances(self):
        """Actualizar balances de todas las cuentas basado en transacciones"""
        self.stdout.write("\n💰 Actualizando balances de cuentas...")
        try:
            updated_count = 0
            for cuenta in self.cuentas.values():
                old_balance = cuenta.current_balance
                new_balance = cuenta.update_balance()
                if old_balance != new_balance:
                    updated_count += 1
            
            self.log_success(f"Balances actualizados: {updated_count} cuentas")
            
        except Exception as e:
            self.log_error(f"Error actualizando balances: {e}")
    
    def print_summary(self):
        """Mostrar resumen de datos demo creados"""
        self.stdout.write("\n" + "="*50)
        self.stdout.write(self.style.SUCCESS("🎭 USUARIO DEMO - RESUMEN"))
        self.stdout.write("="*50)
        
        if self.demo_user:
            # Contar datos creados
            account_count = Account.objects.filter(user=self.demo_user).count()
            transaction_count = Transaction.objects.filter(user=self.demo_user).count()
            goal_count = FinancialGoal.objects.filter(user=self.demo_user).count()
            contribution_count = GoalContribution.objects.filter(user=self.demo_user).count()
            
            # Calcular totales
            total_balance = sum(
                account.current_balance for account in Account.objects.filter(user=self.demo_user)
            )
            
            self.stdout.write(f"👤 Usuario: {self.demo_user.username}")
            self.stdout.write(f"💰 Cuentas creadas: {account_count}")
            self.stdout.write(f"💸 Transacciones: {transaction_count}")
            self.stdout.write(f"🎯 Metas financieras: {goal_count}")
            self.stdout.write(f"📈 Contribuciones: {contribution_count}")
            self.stdout.write(f"💵 Balance total: S/.{total_balance:,.2f}")
            
            self.stdout.write("\n📋 CREDENCIALES:")
            self.stdout.write("   Username: demo")
            self.stdout.write("   Password: demo123")
            
            # Mostrar balance por cuenta
            self.stdout.write("\n💰 BALANCES POR CUENTA:")
            for account in Account.objects.filter(user=self.demo_user).order_by('bank_name', 'name'):
                symbol = account.currency if account.currency == 'USD' else 'S/.'
                self.stdout.write(f"   {account.bank_name} {account.name}: {symbol}{account.current_balance:,.2f}")
        
        self.stdout.write(f"\n✅ Operaciones exitosas: {self.success_count}")
        self.stdout.write(f"❌ Errores encontrados: {self.error_count}")
        self.stdout.write("="*50)