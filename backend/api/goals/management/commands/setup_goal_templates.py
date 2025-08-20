from api.core.management.base import FinTrackBaseCommand
from decimal import Decimal

from api.goals.models import GoalTemplate

class Command(FinTrackBaseCommand):
    help = 'Configura plantillas predeterminadas para metas financieras'
    
    def handle(self, *args, **options):
        self.stdout.write("🎯 GOALS - Configurando plantillas de metas financieras...")
        
        self.create_goal_templates()
        self.print_summary("GOALS - PLANTILLAS CONFIGURADAS", "goals")
    
    def create_goal_templates(self):
        """Crear plantillas de metas financieras"""
        self.stdout.write("\n🎯 Creando plantillas de metas financieras...")
        try:
            initial_count = GoalTemplate.objects.count()
            
            templates = [
                {
                    'name': 'Fondo de Emergencia',
                    'description': 'Ahorra para cubrir 6 meses de gastos en caso de emergencia. Es la base de cualquier plan financiero sólido.',
                    'goal_type': 'emergency_fund',
                    'suggested_timeframe_months': 12,
                    'icon': 'shield-check',
                    'color': '#ef4444',
                    'sort_order': 1,
                    'tips': [
                        'Ahorra automáticamente cada mes',
                        'Mantén el dinero en cuenta separada de alta liquidez',
                        'No uses este fondo para gastos no esenciales',
                        'Revisa y ajusta el monto anualmente según tus gastos',
                        'Objetivo: 3-6 meses de gastos básicos'
                    ]
                },
                {
                    'name': 'Vacaciones Soñadas',
                    'description': 'Ahorra para ese viaje que siempre has querido hacer. Planifica con anticipación para mejores precios.',
                    'goal_type': 'vacation',
                    'suggested_amount': Decimal('3000.00'),
                    'suggested_timeframe_months': 8,
                    'icon': 'plane',
                    'color': '#22c55e',
                    'sort_order': 2,
                    'tips': [
                        'Investiga y calcula todos los costos del viaje',
                        'Busca ofertas y promociones con anticipación',
                        'Considera viajar en temporada baja',
                        'Ahorra dinero extra para imprevistos (10-20%)',
                        'Usa apps de comparación de precios'
                    ]
                },
                {
                    'name': 'Auto Nuevo',
                    'description': 'Ahorra para la cuota inicial de tu próximo vehículo. Una buena cuota inicial reduce el financiamiento.',
                    'goal_type': 'purchase',
                    'suggested_amount': Decimal('15000.00'),
                    'suggested_timeframe_months': 18,
                    'icon': 'car',
                    'color': '#3b82f6',
                    'sort_order': 3,
                    'tips': [
                        'Investiga modelos, precios y consumo de combustible',
                        'Considera autos usados certificados en buen estado',
                        'Negocia el mejor precio y condiciones',
                        'Incluye gastos de seguro, mantenimiento y SOAT',
                        'Compara opciones de financiamiento'
                    ]
                },
                {
                    'name': 'Casa Propia',
                    'description': 'Ahorra para la cuota inicial de tu primera vivienda. La inversión más importante para tu patrimonio.',
                    'goal_type': 'purchase',
                    'suggested_amount': Decimal('50000.00'),
                    'suggested_timeframe_months': 36,
                    'icon': 'home',
                    'color': '#f59e0b',
                    'sort_order': 4,
                    'tips': [
                        'Investiga programas de gobierno (Mi Vivienda, Techo Propio)',
                        'Mantén buen historial crediticio en centrales de riesgo',
                        'Considera ubicación vs precio y proyección de valorización',
                        'Incluye gastos adicionales (notaría, registro, tasación)',
                        'Evalúa el barrio y servicios cercanos'
                    ]
                },
                {
                    'name': 'Eliminar Deudas',
                    'description': 'Libérate de deudas de tarjetas de crédito y préstamos. Prioriza las de mayor interés.',
                    'goal_type': 'debt_payment',
                    'suggested_amount': Decimal('5000.00'),
                    'suggested_timeframe_months': 12,
                    'icon': 'credit-card',
                    'color': '#dc2626',
                    'sort_order': 5,
                    'tips': [
                        'Lista todas tus deudas con montos y tasas',
                        'Prioriza deudas con mayor tasa de interés',
                        'Evita contraer nuevas deudas mientras pagas',
                        'Negocia planes de pago o reestructuración',
                        'Considera consolidar deudas si es beneficioso'
                    ]
                },
                {
                    'name': 'Educación y Cursos',
                    'description': 'Invierte en tu desarrollo profesional con cursos, certificaciones o estudios superiores.',
                    'goal_type': 'education',
                    'suggested_amount': Decimal('8000.00'),
                    'suggested_timeframe_months': 10,
                    'icon': 'graduation-cap',
                    'color': '#8b5cf6',
                    'sort_order': 6,
                    'tips': [
                        'Investiga instituciones y programas reconocidos',
                        'Verifica retorno de inversión esperado',
                        'Busca becas, descuentos y financiamiento',
                        'Planifica los horarios con tu trabajo actual',
                        'Considera cursos online de calidad'
                    ]
                },
                {
                    'name': 'Emprendimiento',
                    'description': 'Capital inicial para tu negocio o startup. Incluye equipos, inventario y capital de trabajo.',
                    'goal_type': 'investment',
                    'suggested_amount': Decimal('20000.00'),
                    'suggested_timeframe_months': 15,
                    'icon': 'briefcase',
                    'color': '#06b6d4',
                    'sort_order': 7,
                    'tips': [
                        'Elabora un plan de negocios detallado',
                        'Investiga el mercado y competencia',
                        'Calcula costos iniciales y operativos',
                        'Considera financiamiento adicional si necesario',
                        'Mantén reserva para imprevistos (20-30%)'
                    ]
                },
                {
                    'name': 'Jubilación',
                    'description': 'Ahorro complementario para tu jubilación. Mientras antes empieces, mejor por el interés compuesto.',
                    'goal_type': 'retirement',
                    'suggested_amount': Decimal('100000.00'),
                    'suggested_timeframe_months': 240,  # 20 años
                    'icon': 'piggy-bank',
                    'color': '#059669',
                    'sort_order': 8,
                    'tips': [
                        'Aprovecha aportes voluntarios al SPP',
                        'Diversifica entre diferentes instrumentos',
                        'Revisa y ajusta periódicamente tus aportes',
                        'Considera inflación en tus cálculos',
                        'Consulta con asesores financieros'
                    ]
                }
            ]
            
            created_templates = []
            for template_data in templates:
                template, created = GoalTemplate.objects.get_or_create(
                    name=template_data['name'],
                    defaults=template_data
                )
                if created:
                    created_templates.append(template.name)
            
            final_count = GoalTemplate.objects.count()
            if len(created_templates) > 0:
                self.log_success(f"Plantillas de metas creadas: {len(created_templates)}")
                self.stdout.write(f"   Nuevas: {', '.join(created_templates[:3])}{'...' if len(created_templates) > 3 else ''}")
            else:
                self.log_info("Las plantillas de metas ya existían")
            
            self.log_info(f"Total de plantillas: {final_count}")
                
        except Exception as e:
            self.log_error(f"Error al crear plantillas de metas: {e}")
    

    def get_summary_stats(self):
        """Obtener estadísticas para el resumen"""
        from django.db.models import Count

        template_stats = GoalTemplate.objects.values('goal_type').annotate(
            count=Count('id')
        ).order_by('goal_type')

        summary_lines = []
        for stat in template_stats:
            goal_type_display = stat['goal_type'].replace('_', ' ').title()
            summary_lines.append(f"📋 {goal_type_display}: {stat['count']}")

        # Total al final
        summary_lines.append(f"📊 Total plantillas: {GoalTemplate.objects.count()}")

        return summary_lines	