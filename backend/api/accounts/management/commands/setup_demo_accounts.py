from django.core.management.base import BaseCommand
from django.contrib.auth.models import User
from decimal import Decimal

from api.accounts.models import Account

class Command(BaseCommand):
    help = 'Crear cuentas demo para el usuario de demostración'
    
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
        self.stdout.write("💰 ACCOUNTS - Creando cuentas demo...")
        
        self.create_demo_accounts()
        self.print_summary()
    
    def create_demo_accounts(self):
        """Crear cuentas para el usuario demo"""
        try:
            demo_user = User.objects.filter(username="demo").first()
            if not demo_user:
                self.log_error("Usuario demo no encontrado. Ejecuta primero setup_demo")
                return
            
            # Limpiar cuentas existentes del demo
            Account.objects.filter(user=demo_user).delete()
            self.log_info("Cuentas demo anteriores eliminadas")
            
            # Definir cuentas demo
            demo_accounts = [
                {
                    'name': "Cuenta Corriente",
                    'bank_name': "BCP",
                    'account_number': "****1234",
                    'account_type': "checking",
                    'initial_balance': Decimal('8000.00'),
                    'currency': "PEN"
                },
                {
                    'name': "Cuenta Ahorros",
                    'bank_name': "BBVA",
                    'account_number': "****5678", 
                    'account_type': "savings",
                    'initial_balance': Decimal('15000.00'),
                    'currency': "PEN"
                },
                {
                    'name': "Tarjeta Crédito",
                    'bank_name': "Interbank",
                    'account_number': "****9012",
                    'account_type': "credit",
                    'initial_balance': Decimal('0.00'),
                    'currency': "PEN"
                },
                {
                    'name': "Efectivo",
                    'bank_name': "",
                    'account_number': "",
                    'account_type': "cash",
                    'initial_balance': Decimal('800.00'),
                    'currency': "PEN"
                },
                {
                    'name': "Yape",
                    'bank_name': "",
                    'account_number': "",
                    'account_type': "digital_wallet",
                    'initial_balance': Decimal('200.00'),
                    'currency': "PEN"
                }
            ]
            
            # Crear las cuentas
            created_accounts = {}
            for account_data in demo_accounts:
                account = Account.objects.create(
                    user=demo_user,
                    **account_data
                )
                # Establecer balance actual igual al inicial
                account.current_balance = account.initial_balance
                account.save(update_fields=['current_balance'])
                
                created_accounts[account.account_type] = account
                self.log_success(f"Cuenta creada: {account}")
            
            self.log_success(f"Total de cuentas demo creadas: {len(created_accounts)}")
            
            # Mostrar resumen de balances
            total_balance = sum(acc.current_balance for acc in created_accounts.values())
            self.log_info(f"Balance total inicial: S/.{total_balance}")
            
            return created_accounts
            
        except Exception as e:
            self.log_error(f"Error al crear cuentas demo: {e}")
            return {}
    
    def print_summary(self):
        """Mostrar resumen de configuración de cuentas"""
        self.stdout.write("\n" + "="*50)
        self.stdout.write("💰 ACCOUNTS - CONFIGURACIÓN COMPLETADA")
        self.stdout.write("="*50)
        self.stdout.write(f"✅ Operaciones exitosas: {self.success_count}")
        self.stdout.write(f"❌ Errores encontrados: {self.error_count}")
        
        if self.success_count > 0:
            self.stdout.write("\n💳 Cuentas demo creadas:")
            demo_user = User.objects.filter(username="demo").first()
            if demo_user:
                accounts = Account.objects.filter(user=demo_user)
                for account in accounts:
                    self.stdout.write(f"   • {account} - S/.{account.current_balance}")
                
                total = sum(acc.current_balance for acc in accounts)
                self.stdout.write(f"\n💰 Patrimonio total: S/.{total}")
        
        self.stdout.write("="*50)