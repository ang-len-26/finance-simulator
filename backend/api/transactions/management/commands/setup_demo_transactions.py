from django.core.management.base import BaseCommand
from django.contrib.auth.models import User
from decimal import Decimal
from datetime import datetime, timedelta

from api.transactions.models import Transaction, Category
from api.accounts.models import Account

class Command(BaseCommand):
    help = 'Crear transacciones demo realistas para el usuario de demostración'
    
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
        self.stdout.write("📊 TRANSACTIONS - Creando transacciones demo...")
        
        self.create_demo_transactions()
        self.update_account_balances()
        self.print_summary()
    
    def create_demo_transactions(self):
        """Crear transacciones demo realistas"""
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
            
            # Obtener categorías
            categories = self.get_categories()
            if not categories:
                self.log_error("Categorías no encontradas. Ejecuta primero setup_categories")
                return
            
            # Limpiar transacciones existentes del demo
            Transaction.objects.filter(user=demo_user).delete()
            self.log_info("Transacciones demo anteriores eliminadas")
            
            # Crear transacciones del último mes
            today = datetime.now().date()
            transactions_data = [
                # INGRESOS
                {
                    'title': 'Sueldo Enero 2025',
                    'amount': Decimal('4500.00'),
                    'type': 'income',
                    'date': today - timedelta(days=30),
                    'to_account': accounts['bcp'],
                    'category': categories.get('salario'),
                    'description': 'Salario mensual empresa ABC',
                    'reference_number': 'SAL-2025-001'
                },
                {
                    'title': 'Freelance Diseño Web',
                    'amount': Decimal('1200.00'),
                    'type': 'income',
                    'date': today - timedelta(days=25),
                    'to_account': accounts['bcp'],
                    'category': categories.get('freelance'),
                    'description': 'Proyecto web para cliente',
                    'reference_number': 'FREE-2025-001'
                },
                
                # GASTOS - ALIMENTACIÓN
                {
                    'title': 'Supermercado Plaza Vea',
                    'amount': Decimal('280.50'),
                    'type': 'expense',
                    'date': today - timedelta(days=28),
                    'from_account': accounts['bcp'],
                    'category': categories.get('alimentacion'),
                    'location': 'Lima Centro',
                    'tags': ['compras', 'familia']
                },
                {
                    'title': 'Almuerzo Chifa Wong',
                    'amount': Decimal('35.00'),
                    'type': 'expense',
                    'date': today - timedelta(days=26),
                    'from_account': accounts['efectivo'],
                    'category': categories.get('alimentacion'),
                    'location': 'San Isidro'
                },
                {
                    'title': 'Delivery McDonald\'s',
                    'amount': Decimal('42.50'),
                    'type': 'expense',
                    'date': today - timedelta(days=20),
                    'from_account': accounts['yape'],
                    'category': categories.get('alimentacion'),
                    'location': 'Lima'
                },
                
                # TRANSPORTE
                {
                    'title': 'Recarga Tarjeta Metro',
                    'amount': Decimal('50.00'),
                    'type': 'expense',
                    'date': today - timedelta(days=27),
                    'from_account': accounts['bcp'],
                    'category': categories.get('transporte'),
                    'description': 'Recarga mensual transporte público'
                },
                {
                    'title': 'Uber al aeropuerto',
                    'amount': Decimal('45.00'),
                    'type': 'expense',
                    'date': today - timedelta(days=22),
                    'from_account': accounts['bcp'],
                    'category': categories.get('transporte'),
                    'location': 'Lima - Callao',
                    'tags': ['viaje']
                },
                {
                    'title': 'Combustible auto',
                    'amount': Decimal('120.00'),
                    'type': 'expense',
                    'date': today - timedelta(days=15),
                    'from_account': accounts['bcp'],
                    'category': categories.get('transporte'),
                    'location': 'Grifo Repsol'
                },
                
                # SERVICIOS
                {
                    'title': 'Netflix Suscripción',
                    'amount': Decimal('24.90'),
                    'type': 'expense',
                    'date': today - timedelta(days=23),
                    'from_account': accounts['bcp'],
                    'category': categories.get('servicios'),
                    'is_recurring': True,
                    'recurring_frequency': 'monthly',
                    'description': 'Suscripción mensual streaming'
                },
                {
                    'title': 'Internet Movistar',
                    'amount': Decimal('89.90'),
                    'type': 'expense',
                    'date': today - timedelta(days=18),
                    'from_account': accounts['bcp'],
                    'category': categories.get('servicios'),
                    'is_recurring': True,
                    'recurring_frequency': 'monthly'
                },
                
                # ENTRETENIMIENTO
                {
                    'title': 'Cine Cinemark',
                    'amount': Decimal('65.00'),
                    'type': 'expense',
                    'date': today - timedelta(days=14),
                    'from_account': accounts['bcp'],
                    'category': categories.get('entretenimiento'),
                    'location': 'Mall del Sur',
                    'tags': ['pareja', 'cine']
                },
                
                # TRANSFERENCIAS
                {
                    'title': 'Transferencia a Ahorros',
                    'amount': Decimal('1000.00'),
                    'type': 'transfer',
                    'date': today - timedelta(days=17),
                    'from_account': accounts['bcp'],
                    'to_account': accounts['bbva'],
                    'description': 'Ahorro mensual programado'
                },
                
                # INVERSIONES
                {
                    'title': 'Inversión Fondo Mutuo BCP',
                    'amount': Decimal('800.00'),
                    'type': 'investment',
                    'date': today - timedelta(days=10),
                    'from_account': accounts['bbva'],
                    'description': 'Fondo de inversión conservador BCP',
                    'reference_number': 'INV-BCP-2025-001'
                },
                
                # COMPRAS
                {
                    'title': 'Compras Saga Falabella',
                    'amount': Decimal('185.00'),
                    'type': 'expense',
                    'date': today - timedelta(days=12),
                    'from_account': accounts['interbank'],
                    'category': categories.get('compras'),
                    'location': 'Mall Aventura',
                    'tags': ['ropa', 'personal']
                },
                
                # SALUD
                {
                    'title': 'Consulta médica',
                    'amount': Decimal('150.00'),
                    'type': 'expense',
                    'date': today - timedelta(days=8),
                    'from_account': accounts['bcp'],
                    'category': categories.get('salud'),
                    'location': 'Clínica Ricardo Palma'
                }
            ]
            
            # Crear las transacciones
            created_count = 0
            for trans_data in transactions_data:
                transaction = Transaction.objects.create(
                    user=demo_user,
                    **trans_data
                )
                created_count += 1
            
            self.log_success(f"Transacciones demo creadas: {created_count}")
            
        except Exception as e:
            self.log_error(f"Error al crear transacciones demo: {e}")
    
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
    
    def get_categories(self):
        """Obtener categorías necesarias"""
        categories = {}
        category_slugs = [
            'salario', 'freelance', 'alimentacion', 'transporte', 
            'servicios', 'entretenimiento', 'compras', 'salud'
        ]
        
        for slug in category_slugs:
            try:
                categories[slug] = Category.objects.get(slug=slug)
            except Category.DoesNotExist:
                categories[slug] = None
                
        return categories
    
    def update_account_balances(self):
        """Actualizar balances de las cuentas después de crear transacciones"""
        self.stdout.write("\n💰 Actualizando balances de cuentas...")
        try:
            demo_user = User.objects.get(username="demo")
            accounts = Account.objects.filter(user=demo_user)
            
            for account in accounts:
                old_balance = account.current_balance
                new_balance = account.update_balance()
                self.log_success(f"{account.name}: {old_balance} → {new_balance}")
                
        except Exception as e:
            self.log_error(f"Error actualizando balances: {e}")
    
    def print_summary(self):
        """Mostrar resumen final"""
        self.stdout.write("\n" + "="*50)
        self.stdout.write(self.style.SUCCESS("📊 TRANSACCIONES DEMO - COMPLETADO"))
        self.stdout.write("="*50)
        self.stdout.write(f"✅ Operaciones exitosas: {self.success_count}")
        self.stdout.write(f"❌ Errores encontrados: {self.error_count}")
        
        try:
            demo_user = User.objects.get(username="demo")
            transaction_count = Transaction.objects.filter(user=demo_user).count()
            self.stdout.write(f"\n📈 Total transacciones demo: {transaction_count}")
            
            # Mostrar balances finales
            self.stdout.write("\n💰 BALANCES FINALES:")
            for account in Account.objects.filter(user=demo_user):
                self.stdout.write(f"   {account.name}: S/.{account.current_balance}")
                
        except Exception as e:
            self.stdout.write(f"Error en resumen: {e}")
        
        self.stdout.write("\n🔧 Próximo paso:")
        self.stdout.write("   python manage.py setup_demo_goals")
        self.stdout.write("="*50)