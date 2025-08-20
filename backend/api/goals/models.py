from datetime import timedelta
from django.db import models
from django.contrib.auth.models import User
from django.db.models import Sum, Avg
from decimal import Decimal
from django.utils import timezone

from ..accounts.models import Account
from ..transactions.models import Category, Transaction

# =====================================================
# MODELOS PARA METAS FINANCIERAS
# =====================================================
class FinancialGoal(models.Model):
    """Modelo principal para metas financieras"""
    
    GOAL_TYPES = (
        ('savings', 'Ahorro'),
        ('expense_reduction', 'Reducir Gastos'),
        ('income_increase', 'Aumentar Ingresos'),
        ('debt_payment', 'Pagar Deuda'),
        ('emergency_fund', 'Fondo de Emergencia'),
        ('investment', 'Inversión'),
        ('purchase', 'Compra Específica'),
        ('vacation', 'Vacaciones'),
        ('education', 'Educación'),
        ('retirement', 'Jubilación'),
        ('other', 'Otro'),
    )
    
    GOAL_STATUS = (
        ('active', 'Activa'),
        ('paused', 'Pausada'),
        ('completed', 'Completada'),
        ('cancelled', 'Cancelada'),
        ('overdue', 'Vencida'),
    )
    
    PRIORITY_LEVELS = (
        ('low', 'Baja'),
        ('medium', 'Media'),
        ('high', 'Alta'),
        ('critical', 'Crítica'),
    )
    
    # Información básica
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    title = models.CharField(max_length=200, help_text="Ej: Ahorrar para auto nuevo")
    description = models.TextField(blank=True, help_text="Descripción detallada de la meta")
    goal_type = models.CharField(max_length=20, choices=GOAL_TYPES, default='savings')
    
    # Configuración de la meta
    target_amount = models.DecimalField(
        max_digits=15, 
        decimal_places=2,
        help_text="Monto objetivo a alcanzar"
    )
    current_amount = models.DecimalField(
        max_digits=15, 
        decimal_places=2, 
        default=Decimal('0.00'),
        help_text="Monto actual ahorrado/progreso"
    )
    
    # Configuración temporal
    start_date = models.DateField(default=timezone.now)
    target_date = models.DateField(help_text="Fecha límite para completar la meta")
    
    # Configuración de contribuciones
    monthly_target = models.DecimalField(
        max_digits=12, 
        decimal_places=2,
        null=True, 
        blank=True,
        help_text="Meta mensual recomendada para llegar al objetivo"
    )
    auto_contribution = models.DecimalField(
        max_digits=12, 
        decimal_places=2,
        null=True, 
        blank=True,
        help_text="Contribución automática mensual"
    )
    
    # Cuenta asociada (opcional)
    associated_account = models.ForeignKey(
        Account, 
        on_delete=models.SET_NULL, 
        null=True, 
        blank=True,
        help_text="Cuenta donde se guarda el dinero para esta meta"
    )
    
    # Categorías relacionadas (para metas de reducción de gastos)
    related_categories = models.ManyToManyField(
        Category, 
        blank=True,
        help_text="Categorías relacionadas con esta meta"
    )
    
    # Estado y configuración
    status = models.CharField(max_length=20, choices=GOAL_STATUS, default='active')
    priority = models.CharField(max_length=10, choices=PRIORITY_LEVELS, default='medium')
    is_public = models.BooleanField(default=False, help_text="Visible para otros usuarios")
    
    # Configuración visual
    icon = models.CharField(max_length=50, default='target', help_text="Ícono lucide-react")
    color = models.CharField(max_length=7, default='#3b82f6', help_text="Color hexadecimal")
    
    # Recordatorios y notificaciones
    enable_reminders = models.BooleanField(default=True)
    reminder_frequency = models.CharField(
        max_length=20,
        choices=[
            ('daily', 'Diario'),
            ('weekly', 'Semanal'),
            ('monthly', 'Mensual'),
        ],
        default='weekly'
    )
    
    # Metadatos
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    completed_at = models.DateTimeField(null=True, blank=True)
    
    class Meta:
        ordering = ['-priority', '-created_at']
        verbose_name = "Meta Financiera"
        verbose_name_plural = "Metas Financieras"
    
    def __str__(self):
        return f"{self.title} - {self.get_goal_type_display()}"
    
    @property
    def progress_percentage(self):
        """Calcular porcentaje de progreso"""
        if self.target_amount <= 0:
            return 0
        percentage = (self.current_amount / self.target_amount) * 100
        return min(percentage, 100)  # No exceder 100%
    
    @property
    def remaining_amount(self):
        """Cantidad restante para completar la meta"""
        return max(self.target_amount - self.current_amount, Decimal('0.00'))
    
    @property
    def days_remaining(self):
        """Días restantes hasta la fecha objetivo"""
        today = timezone.now().date()
        if self.target_date <= today:
            return 0
        return (self.target_date - today).days
    
    @property
    def is_overdue(self):
        """Verificar si la meta está vencida"""
        return timezone.now().date() > self.target_date and self.status == 'active'
    
    @property
    def suggested_monthly_amount(self):
        """Calcular contribución mensual sugerida"""
        if self.days_remaining <= 0:
            return self.remaining_amount
        
        months_remaining = max(self.days_remaining / 30, 1)
        return self.remaining_amount / Decimal(str(months_remaining))
    
    def update_progress(self):
        """Actualizar progreso automáticamente basado en transacciones"""
        if self.associated_account:
            # Para metas de ahorro, usar balance de cuenta asociada
            if self.goal_type in ['savings', 'emergency_fund']:
                self.current_amount = self.associated_account.current_balance
        
        # Para otras metas, calcular basado en contribuciones registradas
        contributions = GoalContribution.objects.filter(goal=self).aggregate(
            total=Sum('amount')
        )['total'] or Decimal('0.00')
        
        if contributions > 0:
            self.current_amount = contributions
        
        # Actualizar estado automáticamente
        if self.current_amount >= self.target_amount:
            self.status = 'completed'
            if not self.completed_at:
                self.completed_at = timezone.now()
        elif self.is_overdue and self.status == 'active':
            self.status = 'overdue'
        
        self.save(update_fields=['current_amount', 'status', 'completed_at'])
        return self.current_amount
    
    def calculate_required_daily_amount(self):
        """Calcular cantidad diaria requerida para completar a tiempo"""
        if self.days_remaining <= 0:
            return self.remaining_amount
        return self.remaining_amount / Decimal(str(self.days_remaining))

# =====================================================
# MODELOS PARA CONTRIBUCIONES Y HITOS DE METAS
# =====================================================
class GoalContribution(models.Model):
    """Contribuciones/aportes hacia una meta financiera"""
    
    CONTRIBUTION_TYPES = (
        ('manual', 'Aporte Manual'),
        ('automatic', 'Aporte Automático'),
        ('transaction_based', 'Basado en Transacción'),
        ('transfer', 'Transferencia'),
    )
    
    goal = models.ForeignKey(FinancialGoal, on_delete=models.CASCADE, related_name='contributions')
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    
    # Información del aporte
    amount = models.DecimalField(max_digits=12, decimal_places=2)
    contribution_type = models.CharField(max_length=20, choices=CONTRIBUTION_TYPES, default='manual')
    date = models.DateField(default=timezone.now)
    
    # Relación con transacción (opcional)
    related_transaction = models.ForeignKey(
        Transaction, 
        on_delete=models.SET_NULL, 
        null=True, 
        blank=True,
        help_text="Transacción que generó este aporte"
    )
    
    # Cuenta de origen
    from_account = models.ForeignKey(
        Account, 
        on_delete=models.CASCADE,
        help_text="Cuenta de donde sale el dinero"
    )
    
    # Información adicional
    notes = models.TextField(blank=True, help_text="Notas sobre este aporte")
    is_recurring = models.BooleanField(default=False)
    
    # Metadatos
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['-date', '-created_at']
        verbose_name = "Contribución a Meta"
        verbose_name_plural = "Contribuciones a Metas"
    
    def __str__(self):
        return f"{self.goal.title} - S/.{self.amount} - {self.date}"
    
    def save(self, *args, **kwargs):
        """Actualizar progreso de la meta al guardar contribución"""
        super().save(*args, **kwargs)
        self.goal.update_progress()

# =====================================================
# MODELOS PARA HITOS DE METAS FINANCIERAS
# =====================================================
class GoalMilestone(models.Model):
    """Hitos/etapas dentro de una meta financiera"""
    
    goal = models.ForeignKey(FinancialGoal, on_delete=models.CASCADE, related_name='milestones')
    title = models.CharField(max_length=200, help_text="Ej: 25% completado")
    description = models.TextField(blank=True)
    
    # Configuración del hito
    target_amount = models.DecimalField(max_digits=12, decimal_places=2)
    target_date = models.DateField()
    
    # Estado
    is_completed = models.BooleanField(default=False)
    completed_at = models.DateTimeField(null=True, blank=True)
    
    # Configuración visual
    icon = models.CharField(max_length=50, default='flag', help_text="Ícono del hito")
    
    # Orden de los hitos
    order = models.PositiveIntegerField(default=0)
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['goal', 'order', 'target_date']
        unique_together = ['goal', 'order']
    
    def __str__(self):
        return f"{self.goal.title} - {self.title}"
    
    @property
    def progress_percentage(self):
        """Porcentaje de progreso del hito"""
        if self.target_amount <= 0:
            return 0
        return min((self.goal.current_amount / self.target_amount) * 100, 100)
    
    def check_completion(self):
        """Verificar si el hito debe marcarse como completado"""
        if not self.is_completed and self.goal.current_amount >= self.target_amount:
            self.is_completed = True
            self.completed_at = timezone.now()
            self.save(update_fields=['is_completed', 'completed_at'])
            return True
        return False

# =====================================================
# MODELOS PARA PLANTILLAS DE METAS FINANCIERAS
# =====================================================
class GoalTemplate(models.Model):
    """Plantillas predefinidas para metas financieras comunes"""
    
    name = models.CharField(max_length=200, help_text="Ej: Fondo de Emergencia")
    description = models.TextField()
    goal_type = models.CharField(max_length=20, choices=FinancialGoal.GOAL_TYPES)
    
    # Configuración sugerida
    suggested_amount = models.DecimalField(
        max_digits=15, 
        decimal_places=2,
        null=True, 
        blank=True,
        help_text="Monto sugerido (puede ser calculado dinámicamente)"
    )
    suggested_timeframe_months = models.PositiveIntegerField(
        help_text="Plazo sugerido en meses"
    )
    
    # Configuración visual
    icon = models.CharField(max_length=50, default='target')
    color = models.CharField(max_length=7, default='#3b82f6')
    
    # Configuración de plantilla
    is_active = models.BooleanField(default=True)
    sort_order = models.PositiveIntegerField(default=0)
    
    # Información educativa
    tips = models.JSONField(
        default=list, 
        blank=True,
        help_text="Lista de consejos: ['Ahorra automáticamente', 'Revisa mensualmente']"
    )
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['sort_order', 'name']
    
    def __str__(self):
        return self.name
    
    def calculate_suggested_amount(self, user):
        """Calcular monto sugerido basado en datos del usuario"""
        if self.goal_type == 'emergency_fund':
            # Fondo de emergencia: 6 meses de gastos promedio
            user_expenses = Transaction.objects.filter(
                user=user,
                type='expense',
                date__gte=timezone.now().date() - timedelta(days=90)
            ).aggregate(avg_monthly=Avg('amount'))['avg_monthly'] or Decimal('0.00')
            
            return user_expenses * 6
        
        return self.suggested_amount or Decimal('1000.00')




