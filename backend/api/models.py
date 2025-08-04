from django.db import models
from django.contrib.auth.models import User
from django.core.validators import MinValueValidator
from django.db.models import Avg, Sum
from decimal import Decimal
from django.utils import timezone
from datetime import timedelta

# =====================================================
# NUEVO MODELO: Sistema de Cuentas/Bancos
# =====================================================
class Account(models.Model):
    ACCOUNT_TYPES = (
        ('checking', 'Cuenta Corriente'),
        ('savings', 'Cuenta Ahorros'),
        ('investment', 'Cuenta Inversión'),
        ('credit', 'Tarjeta Crédito'),
        ('cash', 'Efectivo'),
        ('digital_wallet', 'Billetera Digital'),
        ('business', 'Cuenta Empresarial'),
        ('other', 'Otros'),
    )
    
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    name = models.CharField(max_length=100, help_text="Ej: Cuenta Corriente BCP")
    bank_name = models.CharField(max_length=100, blank=True, help_text="Ej: BCP, BBVA, Interbank")
    account_number = models.CharField(max_length=50, blank=True, help_text="Últimos 4 dígitos (opcional)")
    account_type = models.CharField(max_length=20, choices=ACCOUNT_TYPES, default='checking')
    
    # Balance y configuración
    initial_balance = models.DecimalField(
        max_digits=12, 
        decimal_places=2, 
        default=Decimal('0.00'),
        validators=[MinValueValidator(Decimal('0.00'))]
    )
    current_balance = models.DecimalField(
        max_digits=12, 
        decimal_places=2, 
        default=Decimal('0.00')
    )
    
    # Configuración de cuenta
    currency = models.CharField(max_length=3, default='PEN', help_text="PEN, USD, EUR")
    is_active = models.BooleanField(default=True)
    include_in_reports = models.BooleanField(default=True)
    
    # Metadatos
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['bank_name', 'name']
        unique_together = ['user', 'name']  # No duplicar nombres de cuenta por usuario
    
    def __str__(self):
        if self.bank_name:
            return f"{self.bank_name} - {self.name}"
        return self.name
    
    def update_balance(self):
        """Recalcular balance basado en transacciones"""
        from django.db.models import Sum, Q
        
        # Ingresos a esta cuenta
        income = Transaction.objects.filter(
            to_account=self,
            type__in=['income', 'transfer']
        ).aggregate(total=Sum('amount'))['total'] or Decimal('0.00')
        
        # Gastos desde esta cuenta  
        expenses = Transaction.objects.filter(
            from_account=self,
            type__in=['expense', 'transfer', 'investment', 'loan', 'debt', 'savings']
        ).aggregate(total=Sum('amount'))['total'] or Decimal('0.00')
        
        self.current_balance = self.initial_balance + income - expenses
        self.save(update_fields=['current_balance'])
        return self.current_balance

# =====================================================
# MODELO DE USUARIO PARA DEMO Y REGISTRO
# =====================================================
class UserProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    is_demo = models.BooleanField(default=False)
    demo_expires = models.DateTimeField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return f"{self.user.username} - Demo: {self.is_demo}"

# =====================================================
# MODELOS PARA SISTEMA DE REPORTES AVANZADOS
# =====================================================
class Category(models.Model):
    """Categorías para clasificación avanzada de transacciones"""
    
    CATEGORY_TYPES = (
        ('expense', 'Gasto'),
        ('income', 'Ingreso'),
        ('both', 'Ambos'),
    )
    
    name = models.CharField(max_length=100, unique=True)
    slug = models.SlugField(max_length=100, unique=True)
    icon = models.CharField(max_length=50, default='receipt', 
                           help_text="Nombre del ícono (lucide-react)")
    color = models.CharField(max_length=7, default='#6366f1', 
                            help_text="Color hexadecimal para gráficos")
    category_type = models.CharField(max_length=10, choices=CATEGORY_TYPES, default='expense')
    
    # Jerarquía de categorías
    parent = models.ForeignKey('self', null=True, blank=True, on_delete=models.CASCADE,
                              related_name='subcategories')
    
    # Configuración
    is_active = models.BooleanField(default=True)
    sort_order = models.PositiveIntegerField(default=0)
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        verbose_name_plural = "Categories"
        ordering = ['sort_order', 'name']
    
    def __str__(self):
        if self.parent:
            return f"{self.parent.name} > {self.name}"
        return self.name

# =====================================================
# MODELO ACTUALIZADO: Transaction con cuentas
# =====================================================
class Transaction(models.Model):
    TRANSACTION_TYPES = (
        ('income', 'Income'),
        ('expense', 'Expense'),
        ('transfer', 'Transfer'),
        ('investment', 'Investment'),
        ('loan', 'Loan'),
        ('debt', 'Debt'),
        ('savings', 'Savings'),
        ('other', 'Other'),
    )
    
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    title = models.CharField(max_length=100)
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    type = models.CharField(max_length=20, choices=TRANSACTION_TYPES)
    date = models.DateField()
    description = models.TextField(blank=True, null=True)
    category = models.ForeignKey(Category, on_delete=models.SET_NULL, null=True, blank=True)
    
    # NUEVOS CAMPOS: Sistema de cuentas
    from_account = models.ForeignKey(
        Account, 
        on_delete=models.CASCADE, 
        related_name='outgoing_transactions',
        help_text="Cuenta de origen (obligatorio para gastos/transferencias)"
    )
    to_account = models.ForeignKey(
        Account, 
        on_delete=models.CASCADE, 
        null=True, 
        blank=True,
        related_name='incoming_transactions',
        help_text="Cuenta destino (para ingresos/transferencias)"
    )
    
    # Campos adicionales para funcionalidad avanzada
    reference_number = models.CharField(max_length=100, blank=True, help_text="Número de referencia/voucher")
    location = models.CharField(max_length=200, blank=True, help_text="Lugar de la transacción")
    tags = models.JSONField(default=list, blank=True, help_text="Etiquetas: ['comida', 'trabajo']")
    
    # Transacciones recurrentes
    is_recurring = models.BooleanField(default=False)
    recurring_frequency = models.CharField(
        max_length=20, 
        null=True, 
        blank=True,
        choices=[
            ('daily', 'Diario'),
            ('weekly', 'Semanal'), 
            ('monthly', 'Mensual'),
            ('quarterly', 'Trimestral'),
            ('yearly', 'Anual')
        ]
    )
    parent_transaction = models.ForeignKey(
        'self', 
        null=True, 
        blank=True, 
        on_delete=models.CASCADE,
        help_text="Transacción padre si es recurrente"
    )
    
    # Metadatos
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['-date', '-created_at']
    
    def __str__(self):
        return f"{self.title} - {self.type} - {self.amount} - {self.date}"
    
    def save(self, *args, **kwargs):
        """Override save para actualizar balances de cuentas"""
        is_new = self.pk is None
        old_transaction = None
        
        if not is_new:
            old_transaction = Transaction.objects.get(pk=self.pk)
        
        super().save(*args, **kwargs)
        
        # Actualizar balances de cuentas afectadas
        if self.from_account:
            self.from_account.update_balance()
        if self.to_account:
            self.to_account.update_balance()
            
        # Si es actualización, actualizar cuentas anteriores también
        if old_transaction:
            if old_transaction.from_account and old_transaction.from_account != self.from_account:
                old_transaction.from_account.update_balance()
            if old_transaction.to_account and old_transaction.to_account != self.to_account:
                old_transaction.to_account.update_balance()

# =====================================================
# MODELOS PARA REPORTES Y ANÁLISIS FINANCIERO
# =====================================================
class FinancialMetric(models.Model):
    """Métricas financieras precalculadas para reportes rápidos"""
    
    PERIOD_TYPES = (
        ('daily', 'Diario'),
        ('weekly', 'Semanal'),
        ('monthly', 'Mensual'),
        ('quarterly', 'Trimestral'),
        ('yearly', 'Anual'),
    )
    
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    period_type = models.CharField(max_length=10, choices=PERIOD_TYPES)
    period_start = models.DateField()
    period_end = models.DateField()
    
    # Métricas principales
    total_income = models.DecimalField(max_digits=15, decimal_places=2, default=Decimal('0.00'))
    total_expenses = models.DecimalField(max_digits=15, decimal_places=2, default=Decimal('0.00'))
    net_balance = models.DecimalField(max_digits=15, decimal_places=2, default=Decimal('0.00'))
    
    # Métricas por cuenta
    checking_balance = models.DecimalField(max_digits=15, decimal_places=2, default=Decimal('0.00'))
    savings_balance = models.DecimalField(max_digits=15, decimal_places=2, default=Decimal('0.00'))
    investment_balance = models.DecimalField(max_digits=15, decimal_places=2, default=Decimal('0.00'))
    credit_balance = models.DecimalField(max_digits=15, decimal_places=2, default=Decimal('0.00'))
    
    # Contador de transacciones
    transaction_count = models.PositiveIntegerField(default=0)
    
    # Categoría con mayor gasto
    top_expense_category = models.ForeignKey(Category, on_delete=models.SET_NULL, 
                                           null=True, blank=True,
                                           related_name='top_expense_periods')
    top_expense_amount = models.DecimalField(max_digits=15, decimal_places=2, default=Decimal('0.00'))
    
    # Metadatos
    calculated_at = models.DateTimeField(auto_now=True)
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        unique_together = ['user', 'period_type', 'period_start', 'period_end']
        ordering = ['-period_start']
    
    def __str__(self):
        return f"{self.user.username} - {self.period_type} - {self.period_start}"

# =====================================================
# MODELOS PARA ANÁLISIS Y ALERTAS FINANCIERAS
# =====================================================
class CategorySummary(models.Model):
    """Resumen de gastos por categoría para análisis rápido"""
    
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    category = models.ForeignKey(Category, on_delete=models.CASCADE)
    period_start = models.DateField()
    period_end = models.DateField()
    period_type = models.CharField(max_length=10, choices=FinancialMetric.PERIOD_TYPES)
    
    # Totales
    total_amount = models.DecimalField(max_digits=15, decimal_places=2, default=Decimal('0.00'))
    transaction_count = models.PositiveIntegerField(default=0)
    average_amount = models.DecimalField(max_digits=15, decimal_places=2, default=Decimal('0.00'))
    
    # Comparativas
    previous_period_amount = models.DecimalField(max_digits=15, decimal_places=2, default=Decimal('0.00'))
    percentage_change = models.DecimalField(max_digits=5, decimal_places=2, default=Decimal('0.00'))
    
    # Cuentas más utilizadas para esta categoría
    most_used_account = models.ForeignKey(Account, on_delete=models.SET_NULL, null=True, blank=True)
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        unique_together = ['user', 'category', 'period_start', 'period_end', 'period_type']
        ordering = ['-total_amount']
    
    def __str__(self):
        return f"{self.user.username} - {self.category.name} - {self.period_start}"

# =====================================================
# MODELO PARA ALERTAS Y NOTIFICACIONES FINANCIERAS
# =====================================================
class BudgetAlert(models.Model):
    """Sistema de alertas para presupuestos y gastos inusuales"""
    
    ALERT_TYPES = (
        ('budget_exceeded', 'Presupuesto Excedido'),
        ('unusual_expense', 'Gasto Inusual'),
        ('income_drop', 'Caída de Ingresos'),
        ('account_low', 'Saldo Bajo'),
        ('category_spike', 'Pico en Categoría'),
    )
    
    SEVERITY_LEVELS = (
        ('low', 'Baja'),
        ('medium', 'Media'),
        ('high', 'Alta'),
        ('critical', 'Crítica'),
    )
    
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    alert_type = models.CharField(max_length=20, choices=ALERT_TYPES)
    severity = models.CharField(max_length=10, choices=SEVERITY_LEVELS, default='medium')
    
    title = models.CharField(max_length=200)
    message = models.TextField()
    
    # Relaciones opcionales
    related_transaction = models.ForeignKey(Transaction, on_delete=models.CASCADE, null=True, blank=True)
    related_category = models.ForeignKey(Category, on_delete=models.CASCADE, null=True, blank=True)
    related_account = models.ForeignKey(Account, on_delete=models.CASCADE, null=True, blank=True)
    
    # Datos del trigger
    threshold_amount = models.DecimalField(max_digits=15, decimal_places=2, null=True, blank=True)
    actual_amount = models.DecimalField(max_digits=15, decimal_places=2, null=True, blank=True)
    
    # Estado
    is_read = models.BooleanField(default=False)
    is_dismissed = models.BooleanField(default=False)
    
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        ordering = ['-created_at']
    
    def __str__(self):
        return f"{self.user.username} - {self.alert_type} - {self.severity}"

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

# =====================================================
# FUNCIÓN PARA CREAR PLANTILLAS PREDETERMINADAS
# =====================================================

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

# =====================================================
# CATEGORÍAS PREDETERMINADAS 
# =====================================================
def create_default_categories():
    """Función para crear categorías predeterminadas"""
    
    default_categories = [
        # Gastos principales
        {'name': 'Alimentación', 'icon': 'utensils', 'color': '#ef4444', 'type': 'expense'},
        {'name': 'Transporte', 'icon': 'car', 'color': '#f97316', 'type': 'expense'},
        {'name': 'Vivienda', 'icon': 'home', 'color': '#eab308', 'type': 'expense'},
        {'name': 'Entretenimiento', 'icon': 'gamepad2', 'color': '#22c55e', 'type': 'expense'},
        {'name': 'Servicios', 'icon': 'zap', 'color': '#3b82f6', 'type': 'expense'},
        {'name': 'Salud', 'icon': 'heart-pulse', 'color': '#8b5cf6', 'type': 'expense'},
        {'name': 'Educación', 'icon': 'graduation-cap', 'color': '#06b6d4', 'type': 'expense'},
        {'name': 'Compras', 'icon': 'shopping-cart', 'color': '#ec4899', 'type': 'expense'},
        
        # Ingresos
        {'name': 'Salario', 'icon': 'banknote', 'color': '#10b981', 'type': 'income'},
        {'name': 'Freelance', 'icon': 'laptop', 'color': '#059669', 'type': 'income'},
        {'name': 'Inversiones', 'icon': 'trending-up', 'color': '#0d9488', 'type': 'income'},
        {'name': 'Otros Ingresos', 'icon': 'plus-circle', 'color': '#14b8a6', 'type': 'income'},
    ]
    
    for cat_data in default_categories:
        Category.objects.get_or_create(
            slug=cat_data['name'].lower().replace(' ', '-'),
            defaults={
                'name': cat_data['name'],
                'icon': cat_data['icon'],
                'color': cat_data['color'],
                'category_type': cat_data['type']
            }
        )