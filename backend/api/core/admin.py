from django.contrib import admin
from django.db.models import Sum
from django.utils.html import format_html

from ..accounts.models import Account
from ..transactions.models import Transaction
from .models import UserProfile

@admin.register(UserProfile)
class UserProfileAdmin(admin.ModelAdmin):
    list_display = ['user', 'is_demo', 'demo_expires', 'account_count', 'transaction_count', 'created_at']
    list_filter = ['is_demo', 'created_at', 'demo_expires']
    search_fields = ['user__username', 'user__email']
    readonly_fields = ['created_at', 'account_count', 'transaction_count', 'total_balance']
    
    fieldsets = (
        ('Usuario', {
            'fields': ('user',)
        }),
        ('Configuración Demo', {
            'fields': ('is_demo', 'demo_expires')
        }),
        ('Estadísticas', {
            'fields': ('account_count', 'transaction_count', 'total_balance', 'created_at'),
            'classes': ('collapse',)
        }),
    )
    
    def account_count(self, obj):
        """Número de cuentas del usuario"""
        return Account.objects.filter(user=obj.user).count()
    account_count.short_description = 'Cuentas'
    
    def transaction_count(self, obj):
        """Número de transacciones del usuario"""
        return Transaction.objects.filter(user=obj.user).count()
    transaction_count.short_description = 'Transacciones'
    
    def total_balance(self, obj):
        """Balance total de todas las cuentas"""
        total = Account.objects.filter(
            user=obj.user, 
            is_active=True
        ).aggregate(total=Sum('current_balance'))['total']
        
        if total:
            return format_html(
                '<span style="font-weight: bold; color: green;">${:.2f}</span>',
                total
            )
        return "$0.00"
    total_balance.short_description = 'Balance Total'
