from django.core.management.base import BaseCommand
from api.transactions.models import Category

class Command(BaseCommand):
    help = 'Configura categorías predeterminadas para transacciones'
    
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
        self.stdout.write("📂 TRANSACTIONS - Configurando categorías predeterminadas...")
        
        self.create_categories()
        self.print_summary()
    
    def create_categories(self):
        """Crear categorías predeterminadas"""
        self.stdout.write("\n📂 Creando categorías predeterminadas...")
        try:
            initial_count = Category.objects.count()
            
            default_categories = [
                # Gastos principales
                {'name': 'Alimentación', 'icon': 'utensils', 'color': '#ef4444', 'type': 'expense', 'order': 1},
                {'name': 'Transporte', 'icon': 'car', 'color': '#f97316', 'type': 'expense', 'order': 2},
                {'name': 'Vivienda', 'icon': 'home', 'color': '#eab308', 'type': 'expense', 'order': 3},
                {'name': 'Entretenimiento', 'icon': 'gamepad2', 'color': '#22c55e', 'type': 'expense', 'order': 4},
                {'name': 'Servicios', 'icon': 'zap', 'color': '#3b82f6', 'type': 'expense', 'order': 5},
                {'name': 'Salud', 'icon': 'heart-pulse', 'color': '#8b5cf6', 'type': 'expense', 'order': 6},
                {'name': 'Educación', 'icon': 'graduation-cap', 'color': '#06b6d4', 'type': 'expense', 'order': 7},
                {'name': 'Compras', 'icon': 'shopping-cart', 'color': '#ec4899', 'type': 'expense', 'order': 8},
                {'name': 'Ropa', 'icon': 'shirt', 'color': '#f59e0b', 'type': 'expense', 'order': 9},
                {'name': 'Tecnología', 'icon': 'smartphone', 'color': '#6366f1', 'type': 'expense', 'order': 10},
                
                # Ingresos
                {'name': 'Salario', 'icon': 'banknote', 'color': '#10b981', 'type': 'income', 'order': 21},
                {'name': 'Freelance', 'icon': 'laptop', 'color': '#059669', 'type': 'income', 'order': 22},
                {'name': 'Inversiones', 'icon': 'trending-up', 'color': '#0d9488', 'type': 'income', 'order': 23},
                {'name': 'Otros Ingresos', 'icon': 'plus-circle', 'color': '#14b8a6', 'type': 'income', 'order': 24},
                {'name': 'Bonos', 'icon': 'award', 'color': '#16a34a', 'type': 'income', 'order': 25},
                {'name': 'Ventas', 'icon': 'shopping-bag', 'color': '#15803d', 'type': 'income', 'order': 26},
            ]
            
            created_categories = []
            for cat_data in default_categories:
                category, created = Category.objects.get_or_create(
                    slug=cat_data['name'].lower().replace(' ', '-').replace('ñ', 'n'),
                    defaults={
                        'name': cat_data['name'],
                        'icon': cat_data['icon'],
                        'color': cat_data['color'],
                        'category_type': cat_data['type'],
                        'sort_order': cat_data['order'],
                        'is_active': True
                    }
                )
                if created:
                    created_categories.append(category.name)
            
            final_count = Category.objects.count()
            if len(created_categories) > 0:
                self.log_success(f"Categorías creadas: {len(created_categories)}")
                self.stdout.write(f"   Nuevas: {', '.join(created_categories[:5])}{'...' if len(created_categories) > 5 else ''}")
            else:
                self.log_info("Las categorías predeterminadas ya existían")
            
            self.log_info(f"Total de categorías: {final_count}")
                
        except Exception as e:
            self.log_error(f"Error al crear categorías: {e}")
    
    def print_summary(self):
        """Mostrar resumen del comando"""
        self.stdout.write("\n" + "="*50)
        self.stdout.write(self.style.SUCCESS("🎉 TRANSACTIONS - CATEGORÍAS CONFIGURADAS"))
        self.stdout.write("="*50)
        self.stdout.write(f"✅ Operaciones exitosas: {self.success_count}")
        self.stdout.write(f"❌ Errores encontrados: {self.error_count}")
        self.stdout.write(f"\n📊 RESUMEN DE CATEGORÍAS:")
        
        # Estadísticas por tipo
        expense_count = Category.objects.filter(category_type='expense').count()
        income_count = Category.objects.filter(category_type='income').count()
        both_count = Category.objects.filter(category_type='both').count()
        
        self.stdout.write(f"💸 Gastos: {expense_count}")
        self.stdout.write(f"💰 Ingresos: {income_count}")
        self.stdout.write(f"🔄 Ambos: {both_count}")
        self.stdout.write(f"📈 Total: {Category.objects.count()}")
        self.stdout.write("="*50)