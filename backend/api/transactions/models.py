from decimal import Decimal
from django.db import models
from django.contrib.auth.models import User
from django.utils.text import slugify
from django.core.exceptions import ValidationError

from ..accounts.models import Account

# =====================================================
# Categorías para clasificación avanzada de transacciones
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
        
    def get_full_name(self):
        """Nombre completo con jerarquía"""
        if self.parent:
            return f"{self.parent.name} > {self.name}"
        return self.name
    
    def get_transaction_total(self, user=None):
        """Total de transacciones en esta categoría"""
        qs = self.transaction_set.all()
        if user:
            qs = qs.filter(user=user)
        return qs.aggregate(total=models.Sum('amount'))['total'] or Decimal('0.00')
    
    def get_subcategory_count(self):
        """Número de subcategorías activas"""
        return self.subcategories.filter(is_active=True).count()
    
    def save(self, *args, **kwargs):
        """Auto-generar slug"""
        if not self.slug:
            self.slug = slugify(self.name)
        super().save(*args, **kwargs)

# =====================================================
# Transacciones con soporte para cuentas y categorías
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
    
    # CAMPOS CORREGIDOS: Sistema de cuentas con validación lógica
    from_account = models.ForeignKey(
        Account, 
        on_delete=models.CASCADE, 
        related_name='outgoing_transactions',
        null=True,
        blank=True,
        help_text="Cuenta de origen (para gastos/transferencias)"
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
    
    def clean(self):
        """Validación personalizada según el tipo de transacción"""
        super().clean()
        
        if self.type == 'income' and not self.to_account:
            raise ValidationError({
                'to_account': 'Las transacciones de ingreso requieren una cuenta destino (to_account)'
            })
        elif self.type == 'expense' and not self.from_account:
            raise ValidationError({
                'from_account': 'Las transacciones de gasto requieren una cuenta origen (from_account)'
            })
        elif self.type == 'transfer':
            if not self.from_account:
                raise ValidationError({
                    'from_account': 'Las transferencias requieren una cuenta origen'
                })
            if not self.to_account:
                raise ValidationError({
                    'to_account': 'Las transferencias requieren una cuenta destino'
                })
            if self.from_account == self.to_account:
                raise ValidationError({
                    '__all__': 'No se puede transferir a la misma cuenta'
                })
    
    def save(self, *args, **kwargs):
        """Override save con validación y actualización de balances"""
        # Ejecutar validación antes de guardar
        self.full_clean()
        
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
    
    # Propiedades agregadas
    @property
    def is_income(self):
        """¿Es una transacción de ingreso?"""
        return self.type == 'income'
    
    @property
    def is_expense(self):
        """¿Es una transacción de gasto?"""
        return self.type == 'expense'
    
    @property
    def is_transfer(self):
        """¿Es una transferencia entre cuentas?"""
        return self.type == 'transfer'
    
    @property
    def affects_balance(self):
        """¿Esta transacción afecta el balance de las cuentas?"""
        return self.type in ['income', 'expense', 'transfer', 'investment', 'savings']
    
    @property
    def main_account(self):
        """Cuenta principal de la transacción"""
        return self.from_account or self.to_account
    
    def get_cash_flow_impact(self):
        """Impacto en el flujo de efectivo"""
        if self.type == 'income':
            return float(self.amount)
        elif self.type in ['expense', 'investment', 'debt', 'savings']:
            return -float(self.amount)
        else:  # transfer, loan, other
            return 0.0
    
    def get_display_amount(self):
        """Monto para mostrar (con signo)"""
        if self.is_income:
            return f"+${self.amount}"
        elif self.is_expense:
            return f"-${self.amount}"
        else:
            return f"${self.amount}"
    
    def get_account_for_type(self):
        """Retorna la cuenta principal según el tipo de transacción"""
        if self.type == 'income':
            return self.to_account
        elif self.type in ['expense', 'investment', 'debt', 'savings']:
            return self.from_account
        elif self.type == 'transfer':
            return {'from': self.from_account, 'to': self.to_account}
        else:
            return self.from_account or self.to_account