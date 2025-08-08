from django.db import models
from django.contrib.auth.models import User
from django.core.validators import MinValueValidator
from django.db.models import Sum, Q
from decimal import Decimal

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
    
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='accounts')
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
        verbose_name = "Cuenta"
        verbose_name_plural = "Cuentas"
    
    def __str__(self):
        if self.bank_name:
            return f"{self.bank_name} - {self.name}"
        return self.name
    
    def update_balance(self):
        """Recalcular balance basado en transacciones"""
        from ..transactions.models import Transaction
        
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
    
    @property
    def transaction_count(self):
        """Número total de transacciones"""
        from ..transactions.models import Transaction
        return Transaction.objects.filter(
            Q(from_account=self) | Q(to_account=self)
        ).count()
    
    @property
    def last_transaction_date(self):
        """Fecha de la última transacción"""
        from ..transactions.models import Transaction
        last = Transaction.objects.filter(
            Q(from_account=self) | Q(to_account=self)
        ).order_by('-date').first()
        return last.date if last else None
    
    def get_monthly_income(self, month=None, year=None):
        """Ingresos del mes actual o específico"""
        from ..transactions.models import Transaction
        from django.utils import timezone
        
        if not month or not year:
            now = timezone.now()
            month, year = now.month, now.year
        
        return Transaction.objects.filter(
            to_account=self,
            type='income',
            date__month=month,
            date__year=year
        ).aggregate(total=Sum('amount'))['total'] or Decimal('0.00')
    
    def get_monthly_expenses(self, month=None, year=None):
        """Gastos del mes actual o específico"""
        from ..transactions.models import Transaction
        from django.utils import timezone
        
        if not month or not year:
            now = timezone.now()
            month, year = now.month, now.year
        
        return Transaction.objects.filter(
            from_account=self,
            type='expense',
            date__month=month,
            date__year=year
        ).aggregate(total=Sum('amount'))['total'] or Decimal('0.00')