from django.db import models
from django.contrib.auth.models import User
from django.core.validators import MinValueValidator
from django.db.models import Sum
from decimal import Decimal
from django.utils import timezone

from backend.api.accounts.models import Account
from backend.api.transactions.models import Category, Transaction

# =====================================================
# Métricas financieras precalculadas para reportes rápidos
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
# Resumen de gastos por categoría para análisis rápido
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
# Sistema de alertas para presupuestos y gastos inusuales
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
