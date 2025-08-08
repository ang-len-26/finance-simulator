from django.core.management.base import BaseCommand
from django.core.management import call_command
from django.contrib.auth.models import User
import time

class Command(BaseCommand):
    help = 'Ejecuta toda la configuración de FinTrack: migra, crea datos iniciales y usuario demo'
    
    def __init__(self):
        super().__init__()
        self.success_count = 0
        self.error_count = 0
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
    
    def log_success(self, message):
        self.stdout.write(self.style.SUCCESS(f"✅ {message}"))
        self.success_count += 1
    
    def log_error(self, message):
        self.stdout.write(self.style.ERROR(f"❌ {message}"))
        self.error_count += 1
    
    def log_info(self, message):
        self.stdout.write(self.style.WARNING(f"ℹ️  {message}"))
    
    def log_step(self, step, description):
        self.stdout.write(f"\n{'='*60}")
        self.stdout.write(self.style.HTTP_INFO(f"PASO {step}: {description}"))
        self.stdout.write("="*60)
    
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
            self.setup_analytics()
            
            if not options.get('skip_demo', False):
                self.setup_demo_data(options.get('quick', False))
            
            self.verify_setup()
            self.print_final_summary()
            
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
                self.log_info("Limpiando usuarios existentes...")
                User.objects.filter(
                    username__in=['AngelAdminFindTrack', 'demo']
                ).delete()
            
            self.log_info("Creando superusuario y configuración core...")
            call_command('setup_users', verbosity=1)
            self.log_success("Configuración core completada")
            
        except Exception as e:
            self.log_error(f"Error en configuración core: {e}")
            # No es crítico, continuar
    
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
    
    def setup_analytics(self):
        """Paso 5: Configurar analytics"""
        self.log_step(5, "CONFIGURACIÓN DE ANALYTICS")
        try:
            self.log_info("Inicializando sistema de analytics...")
            call_command('setup_analytics', verbosity=1)
            self.log_success("Analytics configurado")
            
        except Exception as e:
            self.log_error(f"Error en analytics: {e}")
            # Continuar sin analytics
    
    def setup_demo_data(self, quick=False):
        """Paso 6: Crear datos demo"""
        self.log_step(6, "DATOS DE DEMOSTRACIÓN")
        try:
            self.log_info("Creando usuario demo...")
            call_command('setup_demo', verbosity=1)
            
            if not quick:
                self.log_info("Creando cuentas demo...")
                call_command('setup_demo_accounts', verbosity=1)
                
                self.log_info("Creando transacciones demo...")
                call_command('setup_demo_transactions', verbosity=1)
                
                self.log_info("Creando metas demo...")
                call_command('setup_demo_goals', verbosity=1)
                
                self.log_success("Datos demo completos creados")
            else:
                self.log_success("Datos demo básicos creados")
            
        except Exception as e:
            self.log_error(f"Error en datos demo: {e}")
            # No es crítico
    
    def verify_setup(self):
        """Paso 7: Verificar configuración"""
        self.log_step(7, "VERIFICACIÓN DEL SISTEMA")
        try:
            from api.core.models import UserProfile
            from api.transactions.models import Category
            from api.goals.models import GoalTemplate
            from api.accounts.models import Account
            
            # Verificar usuarios
            superuser_exists = User.objects.filter(username="AngelAdminFindTrack").exists()
            demo_exists = User.objects.filter(username="demo").exists()
            
            if superuser_exists:
                self.log_success("Superusuario configurado")
            else:
                self.log_error("Falta superusuario")
            
            if demo_exists:
                demo_user = User.objects.get(username="demo")
                account_count = Account.objects.filter(user=demo_user).count()
                self.log_success(f"Usuario demo con {account_count} cuentas")
            else:
                self.log_info("Sin usuario demo")
            
            # Verificar datos base
            category_count = Category.objects.count()
            template_count = GoalTemplate.objects.count()
            
            self.log_success(f"Sistema verificado: {category_count} categorías, {template_count} plantillas")
            
        except Exception as e:
            self.log_error(f"Error en verificación: {e}")
    
    def print_final_summary(self):
        """Resumen final de la configuración"""
        elapsed_time = time.time() - self.start_time
        
        self.stdout.write("\n" + "="*70)
        self.stdout.write(self.style.SUCCESS("🎉 FINTRACK - CONFIGURACIÓN COMPLETADA"))
        self.stdout.write("="*70)
        self.stdout.write(f"⏱️  Tiempo total: {elapsed_time:.1f} segundos")
        self.stdout.write(f"✅ Operaciones exitosas: {self.success_count}")
        self.stdout.write(f"❌ Errores encontrados: {self.error_count}")
        
        self.stdout.write("\n📋 CREDENCIALES DE ACCESO:")
        self.stdout.write("👤 Panel Admin: http://localhost:8000/admin/")
        self.stdout.write("   Username: AngelAdminFindTrack")
        self.stdout.write("   Password: @FindTrack2025")
        
        if User.objects.filter(username="demo").exists():
            self.stdout.write("\n🎭 Usuario Demo:")
            self.stdout.write("   Username: demo")
            self.stdout.write("   Password: demo123")
        
        self.stdout.write("\n🚀 API Base URL: http://localhost:8000/api/")
        self.stdout.write("\n🔧 PRÓXIMOS PASOS:")
        self.stdout.write("   1. python manage.py runserver")
        self.stdout.write("   2. Probar endpoints con test_all_endpoints.py")
        self.stdout.write("   3. Configurar frontend React")
        
        if self.error_count > 0:
            self.stdout.write("\n⚠️  Se encontraron algunos errores, pero el sistema base está funcional.")
        
        self.stdout.write("="*70)