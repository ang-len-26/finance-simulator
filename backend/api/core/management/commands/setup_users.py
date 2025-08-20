from django.contrib.auth.models import User
from api.core.models import UserProfile
from api.core.management.base import FinTrackBaseCommand
from api.core.utils.config import FinTrackConfig

class Command(FinTrackBaseCommand):
    help = 'Configura usuarios del sistema: superusuario y perfiles base'
    
    def handle(self, *args, **options):
        self.stdout.write("👤 CORE - Configurando usuarios del sistema...")
        
        self.create_superuser()
        self.setup_user_profiles()
        self.print_summary("CORE - CONFIGURACIÓN COMPLETADA", "core")

    def create_superuser(self):
        """Crear superusuario si no existe"""
        self.stdout.write("👤 Creando superusuario...")
        try:
            credentials = FinTrackConfig.get_admin_credentials()

            if User.objects.filter(username=credentials['username']).exists():
                self.log_info(f"Superusuario '{credentials['username']}' ya existe")
                return

            superuser = User.objects.create_superuser(
                username=credentials['username'],
                email=credentials['email'],
                password=credentials['password']
            )

            self.log_success(f"Superusuario creado - Username: {credentials['username']}")
        except Exception as e:
            self.log_error(f"Error al crear superusuario: {e}")
    
    def setup_user_profiles(self):
        """Configurar perfiles base para usuarios existentes"""
        self.log_info("Configurando perfiles de usuario...")
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
    
    def get_summary_stats(self):
        """Obtener estadísticas para el resumen"""
        credentials = FinTrackConfig.get_admin_credentials()
        return  [
            f"👤 Superusuario: {credentials['username']}",
            f"📊 Total usuarios: {User.objects.count()}",
            f"📈 Total perfiles: {UserProfile.objects.count()}"
        ]
