from django.core.management.base import BaseCommand

class FinTrackBaseCommand(BaseCommand):
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
        
    def log_step(self, step, description):
        self.stdout.write(f"\n{'='*60}")
        self.stdout.write(self.style.HTTP_INFO(f"PASO {step}: {description}"))
        self.stdout.write("="*60)
    
    def print_summary(self, title, module_name):
        """Mostrar resumen del comando con formato consistente"""
        self.stdout.write("\n" + "="*50)
        self.stdout.write(self.style.SUCCESS(f"🎉 {title}"))
        self.stdout.write("="*50)
        self.stdout.write(f"✅ Operaciones exitosas: {self.success_count}")
        self.stdout.write(f"❌ Errores encontrados: {self.error_count}")
        
        # Mostrar estadísticas específicas del módulo si están disponibles
        if hasattr(self, 'get_summary_stats'):
            stats = self.get_summary_stats()
            if stats:
                self.stdout.write(f"\n📊 RESUMEN DE {module_name.upper()}:")
                for stat in stats:
                    self.stdout.write(stat)
        
        self.stdout.write("="*50)