#!/usr/bin/env python
"""
FinTrack - Script de configuración final
Ejecuta migraciones, crea superusuario, categorías predeterminadas, datos demo y verifica configuración.
"""

import os
import sys
import django
from django.core.management import execute_from_command_line
from django.contrib.auth.models import User
from decimal import Decimal
from datetime import datetime, timedelta

# Configurar Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'backend.settings')
django.setup()

# Importar modelos después de configurar Django
from api.models import Account, Transaction, Category, create_default_categories, GoalTemplate, FinancialGoal, GoalContribution

def create_default_goal_templates():
    """Crear plantillas predeterminadas de metas financieras"""
    
    templates = [
        {
            'name': 'Fondo de Emergencia',
            'description': 'Ahorra para cubrir 6 meses de gastos en caso de emergencia',
            'goal_type': 'emergency_fund',
            'suggested_timeframe_months': 12,
            'icon': 'shield-check',
            'color': '#ef4444',
            'tips': [
                'Ahorra automáticamente cada mes',
                'Mantén el dinero en cuenta separada',
                'No uses este fondo para gastos no esenciales',
                'Revisa y ajusta el monto anualmente'
            ]
        },
        {
            'name': 'Vacaciones Soñadas',
            'description': 'Ahorra para ese viaje que siempre has querido hacer',
            'goal_type': 'vacation',
            'suggested_amount': Decimal('3000.00'),
            'suggested_timeframe_months': 8,
            'icon': 'plane',
            'color': '#22c55e',
            'tips': [
                'Investiga y calcula todos los costos',
                'Busca ofertas y promociones',
                'Considera viajar en temporada baja',
                'Ahorra dinero extra para imprevistos'
            ]
        },
        {
            'name': 'Auto Nuevo',
            'description': 'Ahorra para la cuota inicial de tu próximo vehículo',
            'goal_type': 'purchase',
            'suggested_amount': Decimal('15000.00'),
            'suggested_timeframe_months': 18,
            'icon': 'car',
            'color': '#3b82f6',
            'tips': [
                'Investiga modelos y precios',
                'Considera autos usados en buen estado',
                'Negocia el mejor precio',
                'Incluye gastos de seguro y mantenimiento'
            ]
        },
        {
            'name': 'Casa Propia',
            'description': 'Ahorra para la cuota inicial de tu primera vivienda',
            'goal_type': 'purchase',
            'suggested_amount': Decimal('50000.00'),
            'suggested_timeframe_months': 36,
            'icon': 'home',
            'color': '#f59e0b',
            'tips': [
                'Investiga programas de gobierno (Mi Vivienda)',
                'Mantén buen historial crediticio',
                'Considera ubicación vs precio',
                'Incluye gastos adicionales (notaría, etc.)'
            ]
        },
        {
            'name': 'Jubilación Temprana',
            'description': 'Construye un fondo para jubilarte cómodamente',
            'goal_type': 'retirement',
            'suggested_amount': Decimal('100000.00'),
            'suggested_timeframe_months': 120,  # 10 años
            'icon': 'sunset',
            'color': '#8b5cf6',
            'tips': [
                'Invierte en instrumentos de largo plazo',
                'Diversifica tus inversiones',
                'Aumenta aportes con incrementos salariales',
                'Revisa estrategia anualmente'
            ]
        },
        {
            'name': 'Educación/Curso',
            'description': 'Invierte en tu desarrollo profesional',
            'goal_type': 'education',
            'suggested_amount': Decimal('2500.00'),
            'suggested_timeframe_months': 6,
            'icon': 'graduation-cap',
            'color': '#06b6d4',
            'tips': [
                'Investiga la calidad del programa',
                'Considera el retorno de inversión',
                'Busca becas o descuentos',
                'Planifica tiempo de estudio'
            ]
        },
        {
            'name': 'Eliminar Deudas',
            'description': 'Libérate de deudas de tarjetas de crédito',
            'goal_type': 'debt_payment',
            'suggested_amount': Decimal('5000.00'),
            'suggested_timeframe_months': 12,
            'icon': 'credit-card',
            'color': '#dc2626',
            'tips': [
                'Lista todas tus deudas',
                'Prioriza deudas con mayor interés',
                'Evita contraer nuevas deudas',
                'Negocia planes de pago si es necesario'
            ]
        },
        {
            'name': 'Emprendimiento',
            'description': 'Capital inicial para tu propio negocio',
            'goal_type': 'investment',
            'suggested_amount': Decimal('10000.00'),
            'suggested_timeframe_months': 15,
            'icon': 'lightbulb',
            'color': '#f97316',
            'tips': [
                'Desarrolla un plan de negocio sólido',
                'Investiga tu mercado objetivo',
                'Considera todos los costos iniciales',
                'Mantén un fondo adicional para imprevistos'
            ]
        }
    ]
    
    for template_data in templates:
        GoalTemplate.objects.get_or_create(
            name=template_data['name'],
            defaults=template_data
        )

class FinTrackSetup:
    def __init__(self):
        self.success_count = 0
        self.error_count = 0
    
    def log_success(self, message):
        print(f"✅ {message}")
        self.success_count += 1
    
    def log_error(self, message):
        print(f"❌ {message}")
        self.error_count += 1
    
    def log_info(self, message):
        print(f"ℹ️  {message}")
    
    def run_migrations(self):
        """Ejecutar migraciones de Django"""
        print("\n🔄 Ejecutando migraciones...")
        try:
            execute_from_command_line(['manage.py', 'makemigrations'])
            execute_from_command_line(['manage.py', 'migrate'])
            self.log_success("Migraciones ejecutadas correctamente")
        except Exception as e:
            self.log_error(f"Error en migraciones: {e}")
    
    def create_superuser(self):
        """Crear superusuario si no existe"""
        print("\n👤 Creando superusuario...")
        try:
            if User.objects.filter(username="admin").exists():
                self.log_info("Superusuario 'admin' ya existe")
                return
            
            User.objects.create_superuser(
                username="AngelAdminFindTrack",
                email="adminfindTrack@findtrack.com",
                password="@FindTrack2025"
            )
            self.log_success("Superusuario creado - Username: AngelAdminFindTrack, Password: @FindTrack2025")
        except Exception as e:
            self.log_error(f"Error al crear superusuario: {e}")
    
    def create_categories(self):
        """Crear categorías predeterminadas"""
        print("\n📂 Creando categorías predeterminadas...")
        try:
            initial_count = Category.objects.count()
            create_default_categories()
            final_count = Category.objects.count()
            
            if final_count > initial_count:
                self.log_success(f"Categorías creadas: {final_count - initial_count}")
            else:
                self.log_info("Las categorías predeterminadas ya existían")
                
        except Exception as e:
            self.log_error(f"Error al crear categorías: {e}")
    
    def create_goal_templates(self):
        """Crear plantillas de metas financieras"""
        print("\n🎯 Creando plantillas de metas financieras...")
        try:
            initial_count = GoalTemplate.objects.count()
            create_default_goal_templates()
            final_count = GoalTemplate.objects.count()
            
            if final_count > initial_count:
                self.log_success(f"Plantillas de metas creadas: {final_count - initial_count}")
            else:
                self.log_info("Las plantillas de metas ya existían")
                
        except Exception as e:
            self.log_error(f"Error al crear plantillas de metas: {e}")

    def create_demo_user(self):
        """Crear usuario demo con datos completos"""
        print("\n🎭 Creando usuario demo...")
        try:
            # Verificar si ya existe
            if User.objects.filter(username="demo").exists():
                self.log_info("Usuario demo ya existe, actualizando datos...")
                demo_user = User.objects.get(username="demo")
                # Limpiar datos anteriores
                Account.objects.filter(user=demo_user).delete()
                Transaction.objects.filter(user=demo_user).delete()
            else:
                demo_user = User.objects.create_user(
                    username="demo",
                    email="demo@findtrack.com",
                    password="demo123"
                )
            
            # Crear cuentas demo
            cuentas = self.create_demo_accounts(demo_user)
            self.create_demo_transactions(demo_user, cuentas)
            
            # Actualizar balances
            for cuenta in cuentas.values():
                cuenta.update_balance()
            
            self.log_success("Usuario demo creado con datos completos")
            self.log_info("Acceso demo - Username: demo, Password: demo123")
            
        except Exception as e:
            self.log_error(f"Error al crear usuario demo: {e}")
    
    def create_demo_accounts(self, user):
        """Crear cuentas para el usuario demo"""
        cuentas = {}
        
        cuentas['bcp'] = Account.objects.create(
            user=user,
            name="Cuenta Corriente",
            bank_name="BCP",
            account_number="****1234",
            account_type="checking",
            initial_balance=Decimal('8000.00'),
            currency="PEN"
        )
        
        cuentas['bbva'] = Account.objects.create(
            user=user,
            name="Cuenta Ahorros",
            bank_name="BBVA",
            account_number="****5678",
            account_type="savings",
            initial_balance=Decimal('15000.00'),
            currency="PEN"
        )
        
        cuentas['interbank'] = Account.objects.create(
            user=user,
            name="Tarjeta Crédito",
            bank_name="Interbank",
            account_number="****9012",
            account_type="credit",
            initial_balance=Decimal('0.00'),
            currency="PEN"
        )
        
        cuentas['efectivo'] = Account.objects.create(
            user=user,
            name="Efectivo",
            account_type="cash",
            initial_balance=Decimal('800.00'),
            currency="PEN"
        )
        
        cuentas['yape'] = Account.objects.create(
            user=user,
            name="Yape",
            account_type="digital_wallet",
            initial_balance=Decimal('200.00'),
            currency="PEN"
        )
        
        return cuentas
    
    def create_demo_transactions(self, user, cuentas):
        """Crear transacciones demo realistas"""
        
        # Obtener categorías (asumiendo que ya fueron creadas)
        try:
            cat_salario = Category.objects.get(slug='salario')
            cat_alimentacion = Category.objects.get(slug='alimentacion')
            cat_transporte = Category.objects.get(slug='transporte')
            cat_servicios = Category.objects.get(slug='servicios')
            cat_entretenimiento = Category.objects.get(slug='entretenimiento')
            cat_freelance = Category.objects.get(slug='freelance')
        except Category.DoesNotExist:
            # Si no existen las categorías, usar None
            cat_salario = cat_alimentacion = cat_transporte = None
            cat_servicios = cat_entretenimiento = cat_freelance = None
        
        # Transacciones del último mes
        today = datetime.now().date()
        
        transacciones = [
            # Ingresos
            {
                'title': 'Sueldo Enero 2025', 
                'amount': Decimal('4500.00'), 
                'type': 'income', 
                'date': today - timedelta(days=30),
                'to_account': cuentas['bcp'],
                'category': cat_salario,
                'description': 'Salario mensual empresa ABC'
            },
            {
                'title': 'Freelance Diseño Web', 
                'amount': Decimal('1200.00'), 
                'type': 'income', 
                'date': today - timedelta(days=25),
                'to_account': cuentas['bcp'],
                'category': cat_freelance,
                'description': 'Proyecto web para cliente'
            },
            
            # Gastos alimentación
            {
                'title': 'Supermercado Plaza Vea', 
                'amount': Decimal('280.50'), 
                'type': 'expense', 
                'date': today - timedelta(days=28),
                'from_account': cuentas['bcp'],
                'category': cat_alimentacion,
                'location': 'Lima Centro'
            },
            {
                'title': 'Almuerzo Chifa', 
                'amount': Decimal('35.00'), 
                'type': 'expense', 
                'date': today - timedelta(days=26),
                'from_account': cuentas['efectivo'],
                'category': cat_alimentacion,
                'location': 'San Isidro'
            },
            {
                'title': 'Café y desayuno', 
                'amount': Decimal('18.50'), 
                'type': 'expense', 
                'date': today - timedelta(days=24),
                'from_account': cuentas['yape'],
                'category': cat_alimentacion
            },
            
            # Transporte
            {
                'title': 'Recarga Tarjeta Metro', 
                'amount': Decimal('50.00'), 
                'type': 'expense', 
                'date': today - timedelta(days=27),
                'from_account': cuentas['bcp'],
                'category': cat_transporte
            },
            {
                'title': 'Uber a aeropuerto', 
                'amount': Decimal('45.00'), 
                'type': 'expense', 
                'date': today - timedelta(days=22),
                'from_account': cuentas['bcp'],
                'category': cat_transporte,
                'location': 'Lima - Callao'
            },
            {
                'title': 'Gasolina Shell', 
                'amount': Decimal('120.00'), 
                'type': 'expense', 
                'date': today - timedelta(days=20),
                'from_account': cuentas['interbank'],
                'category': cat_transporte,
                'reference_number': 'SHELL001234'
            },
            
            # Servicios
            {
                'title': 'Netflix Suscripción', 
                'amount': Decimal('24.90'), 
                'type': 'expense', 
                'date': today - timedelta(days=23),
                'from_account': cuentas['bcp'],
                'category': cat_servicios,
                'is_recurring': True,
                'recurring_frequency': 'monthly'
            },
            {
                'title': 'Spotify Premium', 
                'amount': Decimal('19.90'), 
                'type': 'expense', 
                'date': today - timedelta(days=21),
                'from_account': cuentas['bcp'],
                'category': cat_servicios,
                'is_recurring': True,
                'recurring_frequency': 'monthly'
            },
            {
                'title': 'Recibo de Luz', 
                'amount': Decimal('85.20'), 
                'type': 'expense', 
                'date': today - timedelta(days=19),
                'from_account': cuentas['bcp'],
                'category': cat_servicios,
                'reference_number': 'LUZ202501001'
            },
            
            # Entretenimiento
            {
                'title': 'Cine Cinemark', 
                'amount': Decimal('32.00'), 
                'type': 'expense', 
                'date': today - timedelta(days=18),
                'from_account': cuentas['bcp'],
                'category': cat_entretenimiento,
                'location': 'Jockey Plaza'
            },
            {
                'title': 'Cena en restaurante', 
                'amount': Decimal('95.00'), 
                'type': 'expense', 
                'date': today - timedelta(days=15),
                'from_account': cuentas['interbank'],
                'category': cat_entretenimiento,
                'location': 'Barranco'
            },
            
            # Transferencias
            {
                'title': 'Transferencia a Ahorros', 
                'amount': Decimal('1000.00'), 
                'type': 'transfer', 
                'date': today - timedelta(days=17),
                'from_account': cuentas['bcp'],
                'to_account': cuentas['bbva'],
                'description': 'Ahorro mensual programado'
            },
            {
                'title': 'Retiro ATM', 
                'amount': Decimal('300.00'), 
                'type': 'transfer', 
                'date': today - timedelta(days=14),
                'from_account': cuentas['bcp'],
                'to_account': cuentas['efectivo']
            },
            {
                'title': 'Recarga Yape', 
                'amount': Decimal('100.00'), 
                'type': 'transfer', 
                'date': today - timedelta(days=12),
                'from_account': cuentas['bcp'],
                'to_account': cuentas['yape']
            },
            
            # Inversiones y ahorros
            {
                'title': 'Inversión Fondo Mutuo', 
                'amount': Decimal('800.00'), 
                'type': 'investment', 
                'date': today - timedelta(days=10),
                'from_account': cuentas['bbva'],
                'description': 'Fondo de inversión conservador BCP'
            },
            {
                'title': 'Ahorro objetivo vacaciones', 
                'amount': Decimal('500.00'), 
                'type': 'savings', 
                'date': today - timedelta(days=8),
                'from_account': cuentas['bcp'],
                'description': 'Meta: viaje a Cusco'
            },
            
            # Transacciones recientes
            {
                'title': 'Compra farmacia', 
                'amount': Decimal('28.50'), 
                'type': 'expense', 
                'date': today - timedelta(days=3),
                'from_account': cuentas['efectivo'],
                'category': None,  # Sin categoría para mostrar necesidad de categorización
                'location': 'InkaFarma'
            },
            {
                'title': 'Pago app delivery', 
                'amount': Decimal('42.00'), 
                'type': 'expense', 
                'date': today - timedelta(days=1),
                'from_account': cuentas['yape'],
                'category': cat_alimentacion,
                'description': 'Pedidos Ya - Pizza'
            }
        ]
        
        # Crear las transacciones
        for trans_data in transacciones:
            Transaction.objects.create(user=user, **trans_data)
    
    def create_demo_goals(self, user, cuentas):
        """Crear metas financieras demo"""	
        print("🎯 Creando metas financieras demo...")
        
        today = datetime.now().date()
        
        # Meta 1: Vacaciones a Cusco (en progreso)
        goal_vacaciones = FinancialGoal.objects.create(
            user=user,
            title="Vacaciones a Cusco",
            description="Viaje familiar a Machu Picchu para el próximo verano",
            goal_type="vacation",
            target_amount=Decimal('3500.00'),
            current_amount=Decimal('1200.00'),
            start_date=today - timedelta(days=60),
            target_date=today + timedelta(days=180),  # 6 meses
            monthly_target=Decimal('400.00'),
            associated_account=cuentas['metas'],
            priority="medium",
            icon="plane",
            color="#22c55e"
        )
        
        # Contribuciones para vacaciones
        GoalContribution.objects.create(
            goal=goal_vacaciones,
            user=user,
            amount=Decimal('500.00'),
            contribution_type="manual",
            date=today - timedelta(days=45),
            from_account=cuentas['bcp'],
            notes="Primer aporte para vacaciones"
        )
        
        GoalContribution.objects.create(
            goal=goal_vacaciones,
            user=user,
            amount=Decimal('400.00'),
            contribution_type="automatic",
            date=today - timedelta(days=15),
            from_account=cuentas['bcp'],
            notes="Aporte automático mensual"
        )
        
        GoalContribution.objects.create(
            goal=goal_vacaciones,
            user=user,
            amount=Decimal('300.00'),
            contribution_type="manual",
            date=today - timedelta(days=5),
            from_account=cuentas['bbva'],
            notes="Aporte extra del bono"
        )
        
        # Meta 2: Fondo de Emergencia (activa)
        goal_emergencia = FinancialGoal.objects.create(
            user=user,
            title="Fondo de Emergencia",
            description="6 meses de gastos para emergencias",
            goal_type="emergency_fund",
            target_amount=Decimal('18000.00'),
            current_amount=Decimal('4500.00'),
            start_date=today - timedelta(days=90),
            target_date=today + timedelta(days=300),  # 10 meses
            monthly_target=Decimal('1500.00'),
            associated_account=cuentas['bbva'],
            priority="high",
            icon="shield-check",
            color="#ef4444"
        )
        
        # Contribuciones para emergencia
        GoalContribution.objects.create(
            goal=goal_emergencia,
            user=user,
            amount=Decimal('2000.00'),
            contribution_type="manual",
            date=today - timedelta(days=80),
            from_account=cuentas['bcp'],
            notes="Aporte inicial"
        )
        
        GoalContribution.objects.create(
            goal=goal_emergencia,
            user=user,
            amount=Decimal('1500.00'),
            contribution_type="automatic",
            date=today - timedelta(days=30),
            from_account=cuentas['bcp'],
            notes="Aporte mensual automático"
        )
        
        GoalContribution.objects.create(
            goal=goal_emergencia,
            user=user,
            amount=Decimal('1000.00'),
            contribution_type="manual",
            date=today - timedelta(days=7),
            from_account=cuentas['bbva'],
            notes="Aporte extra de freelance"
        )
        
        # Meta 3: Auto nuevo (a largo plazo)
        goal_auto = FinancialGoal.objects.create(
            user=user,
            title="Auto Nuevo",
            description="Cuota inicial para auto Toyota Yaris",
            goal_type="purchase",
            target_amount=Decimal('25000.00'),
            current_amount=Decimal('3200.00'),
            start_date=today - timedelta(days=30),
            target_date=today + timedelta(days=720),  # 2 años
            monthly_target=Decimal('900.00'),
            priority="medium",
            icon="car",
            color="#3b82f6"
        )
        
        # Meta 4: Curso de Especialización (completada)
        goal_curso = FinancialGoal.objects.create(
            user=user,
            title="Curso Python Avanzado",
            description="Especialización en desarrollo backend",
            goal_type="education",
            target_amount=Decimal('1500.00'),
            current_amount=Decimal('1500.00'),
            start_date=today - timedelta(days=120),
            target_date=today - timedelta(days=30),
            status="completed",
            completed_at=datetime.now() - timedelta(days=30),
            priority="high",
            icon="graduation-cap",
            color="#06b6d4"
        )
        
        # Meta 5: Eliminar deuda tarjeta (urgente)
        goal_deuda = FinancialGoal.objects.create(
            user=user,
            title="Eliminar Deuda Tarjeta",
            description="Pagar deuda completa de tarjeta de crédito",
            goal_type="debt_payment",
            target_amount=Decimal('5500.00'),
            current_amount=Decimal('2100.00'),
            start_date=today - timedelta(days=45),
            target_date=today + timedelta(days=90),  # 3 meses
            monthly_target=Decimal('1200.00'),
            priority="high",
            icon="credit-card",
            color="#dc2626"
        )
        
        self.log_success("5 metas financieras demo creadas con contribuciones")
	
    def verify_setup(self):
        """Verificar que todo esté configurado correctamente"""
        print("\n🔍 Verificando configuración...")
        
        try:
            # Verificar superusuario
            if User.objects.filter(username="admin").exists():
                self.log_success("Superusuario configurado")
            else:
                self.log_error("Falta superusuario")
            
            # Verificar categorías
            category_count = Category.objects.count()
            if category_count >= 10:
                self.log_success(f"Categorías configuradas: {category_count}")
            else:
                self.log_error(f"Pocas categorías: {category_count}")
                
			# Verificar plantillas de metas
            template_count = GoalTemplate.objects.count()
            if template_count >= 5:
                self.log_success(f"Plantillas de metas configuradas: {template_count}")
            else:
                self.log_error(f"Pocas plantillas de metas: {template_count}")
            
            # Verificar usuario demo
            if User.objects.filter(username="demo").exists():
                demo_user = User.objects.get(username="demo")
                account_count = Account.objects.filter(user=demo_user).count()
                transaction_count = Transaction.objects.filter(user=demo_user).count()
                goal_count = FinancialGoal.objects.filter(user=demo_user).count()
                contribution_count = GoalContribution.objects.filter(user=demo_user).count()
                
                self.log_success(f"Usuario demo: {account_count} cuentas, {transaction_count} transacciones")
                self.log_success(f"Metas demo: {goal_count} metas, {contribution_count} contribuciones")
            else:
                self.log_error("Falta usuario demo")
                
        except Exception as e:
            self.log_error(f"Error en verificación: {e}")
    
    def print_summary(self):
        """Mostrar resumen final"""
        print("\n" + "="*60)
        print("🎉 FINTRACK - CONFIGURACIÓN COMPLETADA")
        print("="*60)
        print(f"✅ Operaciones exitosas: {self.success_count}")
        print(f"❌ Errores encontrados: {self.error_count}")
        print("\n📋 CREDENCIALES DE ACCESO:")
        print("👤 Admin Panel: http://localhost:8000/admin/")
        print("   Username: admin")
        print("   Password: admin123")
        print("\n🎭 Usuario Demo:")
        print("   Username: demo")
        print("   Password: demo123")
        print("\n🚀 API Endpoints:")
        print("   Base URL: http://localhost:8000/api/")
        print("   Documentación: Ver urls.py para endpoints completos")
        print("\n🔧 Próximos pasos:")
        print("   1. python manage.py runserver")
        print("   2. Probar endpoints con el script test_all_endpoints.py")
        print("   3. Configurar frontend React")
        print("="*60)

def main():
    """Función principal de configuración"""
    setup = FinTrackSetup()
    
    print("🚀 FINTRACK - CONFIGURACIÓN AUTOMÁTICA")
    print("Configurando sistema de finanzas personales...")
    
    # Ejecutar todos los pasos
    setup.run_migrations()
    setup.create_superuser()
    setup.create_categories()
    setup.create_goal_templates()
    setup.create_demo_user()
    setup.create_demo_accounts()
    setup.create_demo_transactions()
    setup.create_demo_goals()
    setup.verify_setup()
    setup.print_summary()

if __name__ == "__main__":
    main()