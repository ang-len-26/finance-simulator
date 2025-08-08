from django.core.management.base import BaseCommand
from django.contrib.auth.models import User
from django.core.management import call_command
from api.core.models import UserProfile

class Command(BaseCommand):
    help = 'Configura usuarios del sistema: superusuario y perfiles base'
    
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
        self.stdout.write("👤 CORE - Configurando usuarios del sistema...")
        
        self.run_migrations()
        self.create_superuser()
        self.setup_user_profiles()
        self.print_summary()
    
    def run_migrations(self):
        """Ejecutar migraciones de Django"""
        self.stdout.write("\n🔄 Ejecutando migraciones...")
        try:
            call_command('makemigrations', verbosity=0)
            call_command('migrate', verbosity=0)
            self.log_success("Migraciones ejecutadas correctamente")
        except Exception as e:
            self.log_error(f"Error en migraciones: {e}")
    
    def create_superuser(self):
        """Crear superusuario si no existe"""
        self.stdout.write("\n👤 Creando superusuario...")
        try:
            if User.objects.filter(username="AngelAdminFindTrack").exists():
                self.log_info("Superusuario 'AngelAdminFindTrack' ya existe")
                return
            
            superuser = User.objects.create_superuser(
                username="AngelAdminFindTrack",
                email="adminfindTrack@findtrack.com",
                password="@FindTrack2025"
            )
            
            # Crear perfil para el superusuario
            UserProfile.objects.get_or_create(
                user=superuser,
                defaults={'is_demo': False}
            )
            
            self.log_success("Superusuario creado - Username: AngelAdminFindTrack, Password: @FindTrack2025")
        except Exception as e:
            self.log_error(f"Error al crear superusuario: {e}")
    
    def setup_user_profiles(self):
        """Configurar perfiles base para usuarios existentes"""
        self.stdout.write("\n🔧 Configurando perfiles de usuario...")
        try:
            users_without_profile = User.objects.filter(userprofile__isnull=True)
            created_count = 0
            
            for user in users_without_profile:
                UserProfile.objects.create(
                    user=user,
                    is_demo=False
                )
                created_count += 1
            
            if created_count > 0:
                self.log_success(f"Perfiles creados para {created_count} usuarios")
            else:
                self.log_info("Todos los usuarios ya tienen perfiles")
                
        except Exception as e:
            self.log_error(f"Error al configurar perfiles: {e}")
    
    def print_summary(self):
        """Mostrar resumen del comando"""
        self.stdout.write("\n" + "="*50)
        self.stdout.write(self.style.SUCCESS("🎉 CORE - CONFIGURACIÓN COMPLETADA"))
        self.stdout.write("="*50)
        self.stdout.write(f"✅ Operaciones exitosas: {self.success_count}")
        self.stdout.write(f"❌ Errores encontrados: {self.error_count}")
        self.stdout.write("\n📋 USUARIOS CONFIGURADOS:")
        self.stdout.write("👤 Superusuario: AngelAdminFindTrack")
        self.stdout.write(f"📊 Total usuarios: {User.objects.count()}")
        self.stdout.write(f"📈 Total perfiles: {UserProfile.objects.count()}")
        self.stdout.write("="*50)