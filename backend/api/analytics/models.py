from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone
from decimal import Decimal

from ..accounts.models import Account
from ..transactions.models import Category, Transaction

class FinancialMetric(models.Model):
    """Métricas financieras precalculadas para reportes rápidos"""
    
    PERIOD_TYPES = (
        ('daily', 'Diario'),
        ('weekly', 'Semanal'),
        ('monthly', 'Mensual'),
        ('quarterly', 'Trimestral'),
        ('yearly', 'Anual'),
    )
    
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='financial_metrics')
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
    top_expense_category = models.ForeignKey(
        Category, on_delete=models.SET_NULL, 
        null=True, blank=True,
        related_name='top_expense_periods'
    )
    top_expense_amount = models.DecimalField(max_digits=15, decimal_places=2, default=Decimal('0.00'))
    
    # Metadatos
    calculated_at = models.DateTimeField(auto_now=True)
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        unique_together = ['user', 'period_type', 'period_start', 'period_end']
        ordering = ['-period_start']
        verbose_name = "Métrica Financiera"
        verbose_name_plural = "Métricas Financieras"
    
    def __str__(self):
        return f"{self.user.username} - {self.get_period_type_display()} - {self.period_start}"
    
    @property
    def savings_rate(self):
        """Tasa de ahorro como porcentaje"""
        if self.total_income > 0:
            savings = self.total_income - self.total_expenses
            return float((savings / self.total_income) * 100)
        return 0
    
    @property
    def expense_ratio(self):
        """Ratio de gastos vs ingresos"""
        if self.total_income > 0:
            return float((self.total_expenses / self.total_income) * 100)
        return 0
    
    def recalculate(self):
        """Recalcular métricas desde transacciones"""
        from django.db.models import Sum, Count, Q
        
        transactions = Transaction.objects.filter(
            user=self.user,
            date__range=[self.period_start, self.period_end]
        )
        
        # Calcular totales
        totals = transactions.aggregate(
            income=Sum('amount', filter=Q(type='income')),
            expenses=Sum('amount', filter=Q(type='expense')),
            count=Count('id')
        )
        
        self.total_income = totals['income'] or Decimal('0.00')
        self.total_expenses = totals['expenses'] or Decimal('0.00')
        self.net_balance = self.total_income - self.total_expenses
        self.transaction_count = totals['count']
        
        # Encontrar categoría con mayor gasto
        top_category = transactions.filter(type='expense').values('category').annotate(
            total=Sum('amount')
        ).order_by('-total').first()
        
        if top_category:
            self.top_expense_category_id = top_category['category']
            self.top_expense_amount = top_category['total']
        
        self.save()

class CategorySummary(models.Model):
    """Resumen de gastos por categoría para análisis rápido"""
    
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='category_summaries')
    category = models.ForeignKey(Category, on_delete=models.CASCADE, related_name='summaries')
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
    most_used_account = models.ForeignKey(
        Account, on_delete=models.SET_NULL, 
        null=True, blank=True,
        related_name='most_used_for_categories'
    )
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        unique_together = ['user', 'category', 'period_start', 'period_end', 'period_type']
        ordering = ['-total_amount']
        verbose_name = "Resumen de Categoría"
        verbose_name_plural = "Resúmenes de Categorías"
    
    def __str__(self):
        return f"{self.user.username} - {self.category.name} - {self.period_start}"
    
    @property
    def trend_direction(self):
        """Dirección de la tendencia"""
        if self.percentage_change > 5:
            return 'up'
        elif self.percentage_change < -5:
            return 'down'
        else:
            return 'stable'

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
    
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='budget_alerts')
    alert_type = models.CharField(max_length=20, choices=ALERT_TYPES)
    severity = models.CharField(max_length=10, choices=SEVERITY_LEVELS, default='medium')
    
    title = models.CharField(max_length=200)
    message = models.TextField()
    
    # Relaciones opcionales
    related_transaction = models.ForeignKey(
        Transaction, on_delete=models.CASCADE, 
        null=True, blank=True,
        related_name='alerts'
    )
    related_category = models.ForeignKey(
        Category, on_delete=models.CASCADE, 
        null=True, blank=True,
        related_name='alerts'
    )
    related_account = models.ForeignKey(
        Account, on_delete=models.CASCADE, 
        null=True, blank=True,
        related_name='alerts'
    )
    
    # Datos del trigger
    threshold_amount = models.DecimalField(max_digits=15, decimal_places=2, null=True, blank=True)
    actual_amount = models.DecimalField(max_digits=15, decimal_places=2, null=True, blank=True)
    
    # Estado
    is_read = models.BooleanField(default=False)
    is_dismissed = models.BooleanField(default=False)
    
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        ordering = ['-created_at']
        verbose_name = "Alerta de Presupuesto"
        verbose_name_plural = "Alertas de Presupuesto"
    
    def __str__(self):
        return f"{self.user.username} - {self.get_alert_type_display()} - {self.get_severity_display()}"
    
    @property
    def is_active(self):
        """Verifica si la alerta está activa"""
        return not self.is_dismissed and not self.is_read
    
    @property
    def days_since_created(self):
        """Días desde que se creó la alerta"""
        return (timezone.now().date() - self.created_at.date()).days