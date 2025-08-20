from django.contrib.auth.models import User
from decimal import Decimal
from datetime import timedelta
from django.utils import timezone

from api.core.management.base import FinTrackBaseCommand
from api.core.utils.config import FinTrackConfig
from api.core.models import UserProfile
from api.accounts.models import Account
from api.transactions.models import Transaction, Category
from api.goals.models import FinancialGoal, GoalContribution

class Command(FinTrackBaseCommand):
    help = 'Crear usuario demo con datos completos de muestra'
    
    def __init__(self):
        super().__init__()
        self.demo_user = None
        self.cuentas = {}
        self.categorias = {}
    
    def add_arguments(self, parser):
        parser.add_argument(
            '--quick',
            action='store_true',
            help='Crear datos demo básicos sin transacciones extensas'
        )
    
    def handle(self, *args, **options):
        self.stdout.write("🎭 DEMO - Creando usuario demo completo...")
        
        # Verificar que existan categorías, si no, crearlas
        self.ensure_categories_exist()
        
        self.create_demo_user()
        if self.demo_user:
            self.create_demo_accounts()
            if options.get('quick', False):
                self.create_basic_demo_transactions()
            else:
                self.create_demo_transactions()
            self.create_demo_goals()
            self.update_account_balances()
        
        self.print_summary("USUARIO DEMO", "DEMO")
    
    def ensure_categories_exist(self):
        """Verificar que existan categorías, si no las hay, crearlas"""
        self.stdout.write("\n📂 Verificando categorías...")
        try:
            category_count = Category.objects.count()
            if category_count < 5:  # Número mínimo esperado
                self.log_info("Pocas categorías encontradas, creando categorías predeterminadas...")
                from django.core.management import call_command
                call_command('setup_categories', verbosity=0)
                self.log_success("Categorías predeterminadas creadas")
            else:
                self.log_info(f"Categorías disponibles: {category_count}")
            
            # Cargar categorías en memoria para uso eficiente
            self.load_categories_cache()
            
        except Exception as e:
            self.log_error(f"Error verificando categorías: {e}")
            raise
    
    def load_categories_cache(self):
        """Cargar categorías en cache para evitar consultas repetidas"""
        try:
            # Mapeo correcto: nombre_esperado -> slug_real
            category_mapping = {
                # Ingresos
                'Salario': 'salario',
                'Freelance': 'freelance', 
                'Inversiones': 'inversiones',
                'Otros Ingresos': 'otros-ingresos',
                'Bonos': 'bonos',
                'Ventas': 'ventas',
                
                # Gastos
                'Alimentación': 'alimentacion',  # Sin tilde en slug
                'Transporte': 'transporte',
                'Servicios': 'servicios',
                'Entretenimiento': 'entretenimiento',
                'Salud': 'salud',
                'Compras': 'compras',
                'Vivienda': 'vivienda',
                'Educación': 'educacion',  # Sin tilde en slug
                'Ropa': 'ropa',
                'Tecnología': 'tecnologia',  # Sin tilde en slug
                
                # Alias para transacciones
                'alimentacion': 'alimentacion',  # Para compatibilidad
                'ahorros': 'otros-ingresos',  # Las transferencias pueden usar esta
            }
        
            # Cargar categorías usando el mapeo correcto
            for name_key, slug in category_mapping.items():
                category = Category.objects.filter(slug=slug).first()
                if category:
                    self.categorias[name_key] = category
                else:
                    # Buscar por nombre como fallback
                    category = Category.objects.filter(name__icontains=name_key).first()
                    if category:
                        self.categorias[name_key] = category
                        self.log_info(f"Categoría encontrada por nombre para {name_key}: {category.name}")
                    else:
                        # Último recurso: fallback por tipo
                        if name_key in ['Salario', 'Freelance', 'Inversiones', 'Otros Ingresos', 'Bonos', 'Ventas']:
                            fallback = Category.objects.filter(category_type='income').first()
                        else:
                            fallback = Category.objects.filter(category_type='expense').first()
                        
                        if fallback:
                            self.categorias[name_key] = fallback
                            self.log_info(f"Usando categoría fallback para {name_key}: {fallback.name}")

            self.log_success(f"Cache de categorías cargado: {len(self.categorias)} categorías")
            
            # Debug: mostrar todas las categorías encontradas
            if len(self.categorias) < 10:  # Si hay pocas, mostrar debug
                self.log_info("Categorías cargadas en cache:")
                for key, cat in self.categorias.items():
                    self.stdout.write(f"    {key} -> {cat.name} (slug: {cat.slug})")
                
        except Exception as e:
             self.log_error(f"Error cargando cache de categorías: {e}")

    def create_demo_user(self):
        """Crear usuario demo con perfil"""
        self.stdout.write("\n👤 Creando usuario demo...")
        try:
            # Usar configuración centralizada
            demo_creds = FinTrackConfig.get_demo_credentials()
            
            # Verificar si ya existe y limpiar datos anteriores
            if User.objects.filter(username=demo_creds['username']).exists():
                self.log_info("Usuario demo ya existe, limpiando datos anteriores...")
                self.demo_user = User.objects.get(username=demo_creds['username'])
                
                # Limpiar datos anteriores - orden correcto para evitar constraint errors
                FinancialGoal.objects.filter(user=self.demo_user).delete()
                Transaction.objects.filter(user=self.demo_user).delete()
                Account.objects.filter(user=self.demo_user).delete()
                
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
                    username=demo_creds['username'],
                    email=demo_creds.get('email', 'demo@fintrack.com'),
                    password=demo_creds['password'],
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
            self.log_info(f"Credenciales - Username: {demo_creds['username']}, Password: {demo_creds['password']}")
            
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
    
    def create_basic_demo_transactions(self):
        """Crear transacciones demo básicas para --quick"""
        self.stdout.write("\n💸 Creando transacciones demo básicas...")
        try:
            today = timezone.now().date()
            
            # Solo 8 transacciones básicas usando las categorías cargadas
            basic_transactions = [
                {
                    'title': 'Salario Actual',
                    'amount': Decimal('4800.00'),
                    'type': 'income',
                    'date': today - timedelta(days=5),
                    'to_account': self.cuentas.get('bcp_corriente'),
                    'category': self.categorias.get('Salario'),
                    'description': 'Salario mensual'
                },
                {
                    'title': 'Supermercado',
                    'amount': Decimal('280.50'),
                    'type': 'expense',
                    'date': today - timedelta(days=3),
                    'from_account': self.cuentas.get('bcp_corriente'),
                    'category': self.categorias.get('alimentacion'),
                    'location': 'Supermercado Metro'
                },
                {
                    'title': 'Transporte Mensual',
                    'amount': Decimal('120.00'),
                    'type': 'expense',
                    'date': today - timedelta(days=7),
                    'from_account': self.cuentas.get('bcp_corriente'),
                    'category': self.categorias.get('Transporte'),
                    'description': 'Tarjeta Metro + Uber'
                },
                {
                    'title': 'Netflix + Spotify',
                    'amount': Decimal('44.90'),
                    'type': 'expense',
                    'date': today - timedelta(days=10),
                    'from_account': self.cuentas.get('bcp_corriente'),
                    'category': self.categorias.get('Servicios'),
                    'is_recurring': True,
                    'recurring_frequency': 'monthly'
                },
                {
                    'title': 'Freelance Project',
                    'amount': Decimal('1200.00'),
                    'type': 'income',
                    'date': today - timedelta(days=15),
                    'to_account': self.cuentas.get('bcp_corriente'),
                    'category': self.categorias.get('Freelance'),
                    'description': 'Desarrollo web'
                },
                {
                    'title': 'Cena Restaurante',
                    'amount': Decimal('85.00'),
                    'type': 'expense',
                    'date': today - timedelta(days=12),
                    'from_account': self.cuentas.get('bcp_corriente'),
                    'category': self.categorias.get('Entretenimiento'),
                    'location': 'Miraflores'
                },
                {
                    'title': 'Compras Online',
                    'amount': Decimal('150.00'),
                    'type': 'expense',
                    'date': today - timedelta(days=8),
                    'from_account': self.cuentas.get('bcp_corriente'),
                    'category': self.categorias.get('Compras'),
                    'description': 'Amazon - Libros técnicos'
                },
                {
                    'title': 'Transferencia a Ahorros',
                    'amount': Decimal('1000.00'),
                    'type': 'transfer',
                    'date': today - timedelta(days=20),
                    'from_account': self.cuentas.get('bcp_corriente'),
                    'to_account': self.cuentas.get('bbva_ahorros'),
                    'category': self.categorias.get('ahorros'),
                    'description': 'Ahorro mensual'
                }
            ]
            
            created_count = self.create_transactions_batch(basic_transactions)
            self.log_success(f"Transacciones demo básicas creadas: {created_count}")
            
        except Exception as e:
            self.log_error(f"Error en transacciones demo básicas: {e}")
    
    def create_demo_transactions(self):
        """Crear transacciones demo completas"""
        self.stdout.write("\n💸 Creando transacciones demo...")
        try:
            today = timezone.now().date()
            
            # Crear grupos de transacciones por mes para mejor organización
            enero_transactions = self.create_enero_transactions(today)
            febrero_transactions = self.create_febrero_transactions(today)
            marzo_transactions = self.create_marzo_transactions(today)
            
            all_transactions = enero_transactions + febrero_transactions + marzo_transactions
            created_count = self.create_transactions_batch(all_transactions)
            
            self.log_success(f"Transacciones demo creadas: {created_count}")
            
        except Exception as e:
            self.log_error(f"Error general en transacciones demo: {e}")
    
    def create_transactions_batch(self, transactions_data):
        """Crear transacciones en lote de forma eficiente - VERSIÓN CORREGIDA"""
        created_count = 0
        failed_transactions = []

        for trans_data in transactions_data:
            try:
                # Obtener categoría del cache
                category_key = trans_data.pop('category_key', None)  # Usar nueva clave
                category = None
                				
                if category_key and category_key in self.categorias:
                    category = self.categorias[category_key]
                    trans_data['category'] = category
                else:
                    # Fallback si no hay categoría específica
                    if trans_data['type'] == 'income':
                        category = Category.objects.filter(category_type='income').first()
                    else:
                        category = Category.objects.filter(category_type='expense').first()
                    
                    if category:
                        trans_data['category'] = category
                    else:
                        self.log_info(f"Saltando transacción '{trans_data['title']}' - categoría no encontrada")
                        continue
				
                # Validar que las cuentas existan
                from_account = trans_data.get('from_account')
                to_account = trans_data.get('to_account')
                
                if trans_data['type'] == 'expense' and not from_account:
                    self.log_info(f"Saltando transacción '{trans_data['title']}' - cuenta origen faltante")
                    continue
                if trans_data['type'] == 'income' and not to_account:
                    self.log_info(f"Saltando transacción '{trans_data['title']}' - cuenta destino faltante")
                    continue
				
                Transaction.objects.create(
                    user=self.demo_user,
                    **trans_data
                )
                created_count += 1
                
            except Exception as e:
                failed_transactions.append(f"{trans_data.get('title', 'Sin título')}: {str(e)}")
        
        if failed_transactions:
            self.log_info(f"Transacciones fallidas: {len(failed_transactions)}")
		    # Mostrar solo las primeras 3 para no saturar el log
            for fail in failed_transactions[:3]:
                self.log_info(f"  - {fail}")
            
        return created_count
    
    def create_enero_transactions(self, today):
        """Crear transacciones de enero usando category_key"""
        return [
            # === Ingresos ENERO ===
            {
                'title': 'Sueldo Enero',
                'amount': Decimal('4800.00'),
                'type': 'income',
                'date': today - timedelta(days=31),
                'to_account': self.cuentas.get('bcp_corriente'),
                'category_key': 'Salario',  # ✅ Usar category_key en lugar de category
                'description': 'Salario mensual - Empresa TechCorp SAC',
                'reference_number': 'SUE-202501-001'
            },
            {
                'title': 'Freelance App Móvil',
                'amount': Decimal('1500.00'),
                'type': 'income',
                'date': today - timedelta(days=28),
                'to_account': self.cuentas.get('bcp_corriente'),
                'category_key': 'Freelance',  # ✅
                'description': 'Desarrollo app móvil para startup',
                'reference_number': 'FREE-001'
            },
            # === Gastos Enero ===
            {
                'title': 'Supermercado Tottus',
                'amount': Decimal('320.80'),
                'type': 'expense',
                'date': today - timedelta(days=30),
                'from_account': self.cuentas.get('bcp_corriente'),
                'category_key': 'Alimentación',  # ✅
                'location': 'Lima Centro',
                'tags': ['supermercado', 'familia']
            },
            {
                'title': 'Recarga Tarjeta Metro',
                'amount': Decimal('50.00'),
                'type': 'expense',
                'date': today - timedelta(days=29),
                'from_account': self.cuentas.get('bcp_corriente'),
                'category_key': 'Transporte',  # ✅
                'is_recurring': True,
                'recurring_frequency': 'weekly'
            },
            {
                'title': 'Netflix + Spotify',
                'amount': Decimal('44.90'),
                'type': 'expense',
                'date': today - timedelta(days=28),
                'from_account': self.cuentas.get('bcp_corriente'),
                'category_key': 'Servicios',  # ✅
                'is_recurring': True,
                'recurring_frequency': 'monthly',
                'tags': ['suscripción']
            }
        ]

    def create_febrero_transactions(self, today):
        """Crear transacciones de febrero usando category_key"""
        return [
            # === Ingresos FEBRERO ===
            {
                'title': 'Sueldo Febrero',
				'amount': Decimal('4800.00'),
				'type': 'income',
				'date': today - timedelta(days=2),
				'to_account': self.cuentas.get('bcp_corriente'),
				'category_key': 'Salario',  # ✅
				'description': 'Salario mensual - Empresa TechCorp SAC',
				'reference_number': 'SUE-202502-001'
			},
			# === Gastos FEBRERO ===
			{
				'title': 'Cena Romántica - Valentín',
				'amount': Decimal('185.00'),
				'type': 'expense',
				'date': today - timedelta(days=7),
				'from_account': self.cuentas.get('interbank_credito'),
				'category_key': 'Entretenimiento',  # ✅
				'location': 'Miraflores - Restaurante Central',
				'tags': ['san_valentin', 'pareja']
			},
			{
				'title': 'Consulta Médica',
				'amount': Decimal('120.00'),
				'type': 'expense',
				'date': today - timedelta(days=5),
				'from_account': self.cuentas.get('bcp_corriente'),
				'category_key': 'Salud',  # ✅
				'location': 'Clínica Anglo Americana',
				'tags': ['salud', 'consulta']
			},
			{
				'title': 'Compras Mall',
				'amount': Decimal('280.50'),
				'type': 'expense',
				'date': today - timedelta(days=3),
				'from_account': self.cuentas.get('bcp_corriente'),
				'category_key': 'Compras',  # ✅
				'location': 'Jockey Plaza',
				'tags': ['ropa', 'personal']
			},
			# === Transferencias FEBRERO ===
			{
				'title': 'Ahorro Mensual',
				'amount': Decimal('1200.00'),
				'type': 'transfer',
				'date': today - timedelta(days=25),
				'from_account': self.cuentas.get('bcp_corriente'),
				'to_account': self.cuentas.get('bbva_ahorros'),
				'category_key': 'ahorros',  # ✅ Usa el alias definido
				'description': 'Transferencia automática mensual a ahorros',
				'tags': ['ahorro', 'automatico']
			},
			{
				'title': 'Inversión Fondo Mutuo',
				'amount': Decimal('800.00'),
				'type': 'investment',
				'date': today - timedelta(days=20),
				'from_account': self.cuentas.get('bbva_ahorros'),
				'category_key': 'Inversiones',  # ✅
				'description': 'Fondo mutuo BCP - Perfil conservador',
				'reference_number': 'INV-BCP-001'
			},
			# === Gastos menores ===
			{
				'title': 'Café Starbucks',
				'amount': Decimal('15.50'),
				'type': 'expense',
				'date': today - timedelta(days=1),
				'from_account': self.cuentas.get('yape'),
				'category_key': 'Alimentación',  # ✅ Cambiar de 'alimentacion' a 'Alimentación'
				'location': 'San Isidro',
				'tags': ['café', 'trabajo']
			},
			{
				'title': 'Taxi a casa',
				'amount': Decimal('35.00'),
				'type': 'expense',
				'date': today - timedelta(days=1),
				'from_account': self.cuentas.get('efectivo'),
				'category_key': 'Transporte',  # ✅
				'location': 'Lima Centro - San Borja'
			}
		]

    def create_marzo_transactions(self, today):
        """Crear transacciones de marzo usando category_key"""
        return [
			# === Ingresos MARZO ===
			{
				'title': 'Salario Marzo',
				'amount': Decimal('4800.00'),
				'type': 'income',
				'date': today - timedelta(days=5),
				'to_account': self.cuentas.get('bcp_corriente'),
				'category_key': 'Salario',  # ✅
				'description': 'Pago de Salario mensual',
				'tags': ['trabajo', 'salario']
			},
			{
				'title': 'Freelance Project Web',
				'amount': Decimal('1200.00'),
				'type': 'income',
				'date': today - timedelta(days=10),
				'to_account': self.cuentas.get('bcp_corriente'),
				'category_key': 'Freelance',  # ✅
				'description': 'Pago por proyecto freelance',
				'tags': ['freelance', 'proyecto']
			},
			# === Gastos MARZO ===
			{
				'title': 'Alquiler Marzo',
				'amount': Decimal('1200.00'),
				'type': 'expense',
				'date': today - timedelta(days=8),
				'from_account': self.cuentas.get('bcp_corriente'),
				'category_key': 'Vivienda',  # ✅
				'description': 'Pago de alquiler mensual',
				'tags': ['vivienda', 'alquiler']
			},
			{
				'title': 'Supermercado Marzo',
				'amount': Decimal('250.00'),
				'type': 'expense',
				'date': today - timedelta(days=12),
				'from_account': self.cuentas.get('bcp_corriente'),
				'category_key': 'Alimentación',  # ✅
				'description': 'Compra en supermercado',
				'tags': ['alimentacion', 'supermercado']
			},
			{
				'title': 'Uber al aeropuerto',
				'amount': Decimal('45.00'),
				'type': 'expense',
				'date': today - timedelta(days=22),
				'from_account': self.cuentas.get('bcp_corriente'),
				'category_key': 'Transporte',  # ✅
				'tags': ['viaje']
			},
			{
				'title': 'Combustible auto',
				'amount': Decimal('120.00'),
				'type': 'expense',
				'date': today - timedelta(days=15),
				'from_account': self.cuentas.get('bcp_corriente'),
				'category_key': 'Transporte'  # ✅
			},
			# === Compra USD ===
			{
				'title': 'Compra Amazon US',
				'amount': Decimal('89.99'),
				'type': 'expense',
				'date': today - timedelta(days=12),
				'from_account': self.cuentas.get('scotiabank_usd'),
				'category_key': 'Compras',  # ✅
				'description': 'Libros técnicos programación',
				'location': 'Online - Amazon.com',
				'tags': ['educacion', 'libros', 'usd']
			}
		]

    def create_basic_demo_transactions(self):
        """Crear transacciones demo básicas para --quick - VERSIÓN CORREGIDA"""
        self.stdout.write("\n💸 Creando transacciones demo básicas...")
        try:
            today = timezone.now().date()
            
            # Solo 8 transacciones básicas usando category_key
            basic_transactions = [
				{
					'title': 'Salario Actual',
					'amount': Decimal('4800.00'),
					'type': 'income',
					'date': today - timedelta(days=5),
					'to_account': self.cuentas.get('bcp_corriente'),
					'category_key': 'Salario',
					'description': 'Salario mensual'
				},
				{
					'title': 'Supermercado',
					'amount': Decimal('280.50'),
					'type': 'expense',
					'date': today - timedelta(days=3),
					'from_account': self.cuentas.get('bcp_corriente'),
					'category_key': 'Alimentación',
					'location': 'Supermercado Metro'
				},
				{
					'title': 'Transporte Mensual',
					'amount': Decimal('120.00'),
					'type': 'expense',
					'date': today - timedelta(days=7),
					'from_account': self.cuentas.get('bcp_corriente'),
					'category_key': 'Transporte',
					'description': 'Tarjeta Metro + Uber'
				},
				{
					'title': 'Netflix + Spotify',
					'amount': Decimal('44.90'),
					'type': 'expense',
					'date': today - timedelta(days=10),
					'from_account': self.cuentas.get('bcp_corriente'),
					'category_key': 'Servicios',
					'recurring_frequency': 'monthly'
				},
				{
					'title': 'Freelance Project',
					'amount': Decimal('1200.00'),
					'type': 'income',
					'date': today - timedelta(days=15),
					'to_account': self.cuentas.get('bcp_corriente'),
					'category_key': 'Freelance',
					'description': 'Desarrollo web'
				},
				{
                    'title': 'Cena Restaurante',
                    'amount': Decimal('85.00'),
                    'type': 'expense',
                    'date': today - timedelta(days=12),
                    'from_account': self.cuentas.get('bcp_corriente'),
                    'category_key': 'Entretenimiento',
                    'location': 'Miraflores'
				},
				{
                    'title': 'Compras Online',
                    'amount': Decimal('150.00'),
                    'type': 'expense',
                    'date': today - timedelta(days=8),
                    'from_account': self.cuentas.get('bcp_corriente'),
                    'category_key': 'Compras',
                    'description': 'Amazon - Libros técnicos'
                },
                {
                    'title': 'Transferencia a Ahorros',
                    'amount': Decimal('1000.00'),
                    'type': 'transfer',
                    'date': today - timedelta(days=20),
                    'from_account': self.cuentas.get('bcp_corriente'),
                    'to_account': self.cuentas.get('bbva_ahorros'),
                    'category_key': 'ahorros',
                    'description': 'Ahorro mensual'
                }
            ]
            
        except Exception as e:
            self.log_error(f"Error al crear transacciones demo: {e}")

    def create_demo_goals(self):
        """Crear metas financieras demo con progreso realista"""
        self.stdout.write("\nðŸŽ¯ Creando metas financieras demo...")
        try:
            today = timezone.now().date()
            
            # Meta 1: Vacaciones a Europa (en progreso activo)
            goal_europa = FinancialGoal.objects.create(
                user=self.demo_user,
                title="Vacaciones a Europa 2025",
                description="Viaje de 15 dÃ­as por EspaÃ±a, Francia e Italia. Incluye vuelos, hoteles y gastos.",
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
            GoalContribution.objects.create(
                goal=goal_europa,
                user=self.demo_user,
                amount=Decimal('1000.00'),
                contribution_type='manual',
                date=today - timedelta(days=90),
                from_account=self.cuentas['bcp_corriente'],
                notes='Aporte inicial para vacaciones'
            )

            GoalContribution.objects.create(
                goal=goal_europa,
                user=self.demo_user,
                amount=Decimal('800.00'),
                contribution_type='automatic',
                date=today - timedelta(days=60),
                from_account=self.cuentas['bcp_corriente'],
                notes='Aporte automÃ¡tico mensual'
            )

            GoalContribution.objects.create(
                goal=goal_europa,
                user=self.demo_user,
                amount=Decimal('700.00'),
                contribution_type='manual',
                date=today - timedelta(days=30),
                from_account=self.cuentas['bcp_corriente'],
                notes='Aporte extra de Freelance'
            )

            GoalContribution.objects.create(
                goal=goal_europa,
                user=self.demo_user,
                amount=Decimal('700.00'),
                contribution_type='automatic',
                date=today - timedelta(days=5),
                from_account=self.cuentas['bcp_corriente'],
                notes='Aporte mensual febrero'
            )

            # Meta 2: Fondo de Emergencia (en construcciÃ³n)
            goal_emergencia = FinancialGoal.objects.create(
                user=self.demo_user,
                title="Fondo de Emergencia",
                description="Reserva de 6 meses de gastos para situaciones imprevistas (pÃ©rdida de trabajo, Salud, etc.)",
                goal_type="emergency_fund",
                target_amount=Decimal('24000.00'),
                current_amount=Decimal('8500.00'),
                start_date=today - timedelta(days=180),
                target_date=today + timedelta(days=365),  # 1 aÃ±o
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
                notes='Transferencia de bonificaciÃ³n anual'
            )
            
            # Meta 3: Auto Nuevo (largo plazo)
            goal_auto = FinancialGoal.objects.create(
                user=self.demo_user,
                title="Auto Toyota Corolla 2024",
                description="Cuota inicial para auto nuevo. Modelo: Toyota Corolla Cross HÃ­brido 2024",
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
            
            # Contribuciones para auto
            GoalContribution.objects.create(
                goal=goal_auto,
                user=self.demo_user,
                amount=Decimal('2000.00'),
                contribution_type="manual",
                date=today - timedelta(days=25),
                from_account=self.cuentas['bbva_ahorros'],
                notes="Aporte inicial - venta de auto anterior"
            )
            
            GoalContribution.objects.create(
                goal=goal_auto,
                user=self.demo_user,
                amount=Decimal('600.00'),
                contribution_type="automatic",
                date=today - timedelta(days=10),
                from_account=self.cuentas['bcp_corriente'],
                notes="Primer aporte mensual automÃ¡tico"
            )
            
            GoalContribution.objects.create(
                goal=goal_auto,
                user=self.demo_user,
                amount=Decimal('600.00'),
                contribution_type="automatic", 
                date=today - timedelta(days=5),
                from_account=self.cuentas['bcp_corriente'],
                notes="Aporte mensual Freelance"
            )
            
            # Meta 4: EducaciÃ³n/CertificaciÃ³n (completada)
            goal_educacion = FinancialGoal.objects.create(
                user=self.demo_user,
                title="CertificaciÃ³n AWS Cloud Practitioner",
                description="Curso y examen de certificaciÃ³n AWS para desarrollo profesional",
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

    def print_demo_details(self):
        """Mostrar estadísticas detalladas específicas del demo"""
        if not self.demo_user:
            return
            
        # Contar datos creados
        account_count = Account.objects.filter(user=self.demo_user).count()
        transaction_count = Transaction.objects.filter(user=self.demo_user).count()
        goal_count = FinancialGoal.objects.filter(user=self.demo_user).count()
        contribution_count = GoalContribution.objects.filter(user=self.demo_user).count()
        
        # Calcular totales
        total_balance = sum(
            account.current_balance for account in Account.objects.filter(user=self.demo_user)
        )
        
        # Usar el formato estándar del BaseCommand pero con datos específicos del demo
        self.stdout.write(f"👤 Usuario: {self.demo_user.username}")
        self.stdout.write(f"💰 Cuentas creadas: {account_count}")
        self.stdout.write(f"💸 Transacciones: {transaction_count}")
        self.stdout.write(f"🎯 Metas financieras: {goal_count}")
        self.stdout.write(f"📈 Contribuciones: {contribution_count}")
        self.stdout.write(f"💵 Balance total: S/.{total_balance:,.2f}")
        
        # Credenciales usando configuración centralizada
        demo_creds = FinTrackConfig.get_demo_credentials()
        self.stdout.write("\n📋 CREDENCIALES:")
        self.stdout.write(f"   Username: {demo_creds['username']}")
        self.stdout.write(f"   Password: {demo_creds['password']}")
        
        # Mostrar balance por cuenta
        self.stdout.write("\n💰 BALANCES POR CUENTA:")
        for account in Account.objects.filter(user=self.demo_user).order_by('bank_name', 'name'):
            symbol = account.currency if account.currency == 'USD' else 'S/.'
            self.stdout.write(f"    {account.bank_name} {account.name}: {symbol}{account.current_balance:,.2f}")
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