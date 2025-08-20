from django.core.management import call_command
from django.contrib.auth.models import User
from django.db import transaction
import time

from api.core.management.base import FinTrackBaseCommand
from api.core.utils.config import FinTrackConfig

class Command(FinTrackBaseCommand):
    help = 'Ejecuta toda la configuración de FinTrack: migra, crea datos iniciales y usuario demo'
    
    def __init__(self):
        super().__init__()
        self.start_time = None
    
    def add_arguments(self, parser):
        parser.add_argument(
            '--skip-demo',
            action='store_true',
            help='Omitir creación de usuario demo y datos de ejemplo'
        )
        parser.add_argument(
            '--reset',
            action='store_true',
            help='Eliminar datos existentes antes de crear nuevos'
        )
        parser.add_argument(
            '--quick',
            action='store_true',
            help='Configuración rápida sin datos demo extensos'
        )
    
    def handle(self, *args, **options):
        self.start_time = time.time()
        
        self.stdout.write(self.style.SUCCESS(
            "\n🚀 FINTRACK - CONFIGURACIÓN AUTOMÁTICA MODULAR"
        ))
        self.stdout.write("Configurando sistema completo de finanzas personales...")
        
        try:
            # Ejecutar configuración paso a paso
            self.run_migrations()
            self.setup_core_data(options.get('reset', False))
            self.setup_categories()
            self.setup_goal_templates()
            
            if not options.get('skip_demo', False):
                self.setup_demo_data(options.get('quick', False))
                self.setup_analytics()
            
            self.verify_setup()
            self.print_summary("FINTRACK - CONFIGURACIÓN COMPLETADA", "core")
            
        except Exception as e:
            self.log_error(f"Error crítico en configuración: {e}")
            self.stdout.write(
                self.style.ERROR("❌ Configuración interrumpida. Revisa los errores anteriores.")
            )
            return
    
    def run_migrations(self):
        """Paso 1: Ejecutar migraciones"""
        self.log_step(1, "MIGRACIONES DE BASE DE DATOS")
        try:
            self.log_info("Creando migraciones...")
            call_command('makemigrations', verbosity=0, interactive=False)
            
            self.log_info("Aplicando migraciones...")
            call_command('migrate', verbosity=0, interactive=False)
            
            self.log_success("Base de datos actualizada correctamente")
            
        except Exception as e:
            self.log_error(f"Error en migraciones: {e}")
            raise
    
    def setup_core_data(self, reset=False):
        """Paso 2: Configurar datos core (usuarios, perfiles)"""
        self.log_step(2, "CONFIGURACIÓN DE USUARIOS Y CORE")
        try:
            if reset:
                self.perform_clean_reset()
            
            self.log_info("Creando superusuario y configuración core...")
            call_command('setup_users', verbosity=1)
            self.log_success("Configuración core completada")
            
        except Exception as e:
            self.log_error(f"Error en configuración core: {e}")
            # No es crítico, continuar
    
    def perform_clean_reset(self):
        """Limpieza completa y segura de datos demo y relacionados"""
        self.log_info("Realizando limpieza completa del sistema...")
        
        try:
            with transaction.atomic():
                # Obtener credenciales desde configuración centralizada
                admin_creds = FinTrackConfig.get_admin_credentials()
                demo_creds = FinTrackConfig.get_demo_credentials()
                
                # Obtener usuarios a limpiar
                users_to_clean = User.objects.filter(
                    username__in=[admin_creds['username'], demo_creds['username']]
                )
                
                if users_to_clean.exists():
                    # Limpiar datos relacionados en orden correcto para evitar constraint errors
                    for user in users_to_clean:
                        # Importar solo cuando sea necesario para evitar circular imports
                        from api.goals.models import FinancialGoal, GoalContribution
                        from api.transactions.models import Transaction
                        from api.accounts.models import Account
                        from api.analytics.models import FinancialMetric, CategorySummary, BudgetAlert
                        
                        # Eliminar en orden de dependencias
                        GoalContribution.objects.filter(user=user).delete()
                        FinancialGoal.objects.filter(user=user).delete()
                        Transaction.objects.filter(user=user).delete()
                        Account.objects.filter(user=user).delete()
                        
                        # Analytics
                        FinancialMetric.objects.filter(user=user).delete()
                        CategorySummary.objects.filter(user=user).delete()
                        BudgetAlert.objects.filter(user=user).delete()
                    
                    # Finalmente eliminar usuarios (excepto si es superuser activo)
                    User.objects.filter(
                        username__in=[admin_creds['username'], demo_creds['username']],
                        is_superuser=False
                    ).delete()
                    
                    # Para superuser, solo limpiar datos pero mantener usuario
                    superuser = User.objects.filter(
                        username=admin_creds['username'], 
                        is_superuser=True
                    ).first()
                    
                    if superuser:
                        self.log_info(f"Superusuario '{admin_creds['username']}' mantenido, solo datos limpiados")
                
            self.log_success("Limpieza completa realizada correctamente")
            
        except Exception as e:
            self.log_error(f"Error en limpieza: {e}")
            raise
    
    def setup_categories(self):
        """Paso 3: Crear categorías predeterminadas"""
        self.log_step(3, "CATEGORÍAS DE TRANSACCIONES")
        try:
            self.log_info("Creando categorías predeterminadas...")
            call_command('setup_categories', verbosity=1)
            self.log_success("Categorías configuradas")
            
        except Exception as e:
            self.log_error(f"Error en categorías: {e}")
            # Continuar sin categorías
    
    def setup_goal_templates(self):
        """Paso 4: Crear plantillas de metas"""
        self.log_step(4, "PLANTILLAS DE METAS FINANCIERAS")
        try:
            self.log_info("Creando plantillas de metas...")
            call_command('setup_goal_templates', verbosity=1)
            self.log_success("Plantillas de metas configuradas")
            
        except Exception as e:
            self.log_error(f"Error en plantillas de metas: {e}")
            # Continuar sin plantillas

    def setup_demo_data(self, quick=False):
        """Paso 5: Crear datos demo"""
        self.log_step(5, "DATOS DE DEMOSTRACIÓN")
        try:
            self.log_info("Creando usuario demo...")
            if quick:
                call_command('setup_demo', '--quick', verbosity=1)
            else:
                call_command('setup_demo', verbosity=1)
            
        except Exception as e:
            self.log_error(f"Error en datos demo: {e}")
            # No es crítico
   
    def setup_analytics(self):
        """Paso 6: Configurar analytics"""
        self.log_step(6, "CONFIGURACIÓN DE ANALYTICS")
        try:
            self.log_info("Inicializando sistema de analytics...")
            call_command('setup_analytics', verbosity=1)
            self.log_success("Analytics configurado")
            
        except Exception as e:
            self.log_error(f"Error en analytics: {e}")
            # Continuar sin analytics
        
    def verify_setup(self):
        """Paso 7: Verificar configuración"""
        self.log_step(7, "VERIFICACIÓN DEL SISTEMA")
        try:
            from api.core.models import UserProfile
            from api.transactions.models import Category
            from api.goals.models import GoalTemplate
            from api.accounts.models import Account
            
            # Usar configuración centralizada
            admin_creds = FinTrackConfig.get_admin_credentials()
            demo_creds = FinTrackConfig.get_demo_credentials()
            
            # Verificar usuarios
            superuser_exists = User.objects.filter(
                username=admin_creds['username'],
                is_superuser=True
            ).exists()
            
            demo_exists = User.objects.filter(
                username=demo_creds['username']
            ).exists()
            
            if superuser_exists:
                self.log_success("Superusuario configurado correctamente")
            else:
                self.log_error("Falta superusuario o no tiene permisos correctos")
            
            if demo_exists:
                demo_user = User.objects.get(username=demo_creds['username'])
                account_count = Account.objects.filter(user=demo_user).count()
                profile = UserProfile.objects.filter(user=demo_user).first()
                
                if profile and profile.is_demo:
                    self.log_success(f"Usuario demo con {account_count} cuentas y perfil demo válido")
                else:
                    self.log_error("Usuario demo existe pero perfil demo inválido")
            else:
                self.log_info("Sin usuario demo (omitido con --skip-demo)")
            
            # Verificar datos base
            category_count = Category.objects.count()
            template_count = GoalTemplate.objects.count()
            
            if category_count >= 10:  # Verificar cantidad mínima esperada
                self.log_success(f"Categorías verificadas: {category_count} disponibles")
            else:
                self.log_error(f"Pocas categorías: solo {category_count}")
                
            if template_count >= 5:  # Verificar cantidad mínima esperada
                self.log_success(f"Plantillas verificadas: {template_count} disponibles")
            else:
                self.log_error(f"Pocas plantillas: solo {template_count}")
            
        except Exception as e:
            self.log_error(f"Error en verificación: {e}")
    
    def get_summary_stats(self):
        """Resumen final de la configuración"""
        admin_creds = FinTrackConfig.get_admin_credentials()
        demo_creds = FinTrackConfig.get_demo_credentials()

        summary = [
            f"⏱️  Tiempo total: {time.time() - self.start_time:.1f} segundos",
            "\n📋 CREDENCIALES DE ACCESO:",
            "👤 Panel Admin: http://localhost:8000/admin/",
            f"   Username: {admin_creds['username']}",
            "   Password: [Configurado en variables de entorno]",
        ]

        # Solo añadir si existe usuario demo
        if User.objects.filter(username=demo_creds['username']).exists():
            summary.extend([
                "\n🎭 Usuario Demo:",
                f"   Username: {demo_creds['username']}",
                f"   Password: {demo_creds['password']}",
            ])

        summary.extend([
            "\n🚀 API Base URL: http://localhost:8000/api/",
            "\n🔧 PRÓXIMOS PASOS:",
            "   1. python manage.py runserver",
            "   2. Probar endpoints con test_all_endpoints.py",
            "   3. Configurar frontend React",
        ])

        if self.error_count > 0:
            summary.append("⚠️  Se encontraron algunos errores, pero el sistema base está funcional.")

        return summary