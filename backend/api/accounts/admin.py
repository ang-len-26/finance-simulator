from django.contrib import admin
from django.utils.html import format_html

from ..transactions.models import Transaction
from .models import Account

@admin.register(Account)
class AccountAdmin(admin.ModelAdmin):
    list_display = [
        'user', 'name', 'bank_name', 'account_type', 
        'formatted_current_balance', 'currency', 'is_active', 
        'transaction_count', 'created_at'
    ]
    list_filter = [
        'account_type', 'bank_name', 'currency', 'is_active', 
        'include_in_reports', 'created_at'
    ]
    search_fields = ['name', 'bank_name', 'user__username', 'account_number']
    readonly_fields = ['current_balance', 'created_at', 'updated_at', 'transaction_count']
    ordering = ['user', 'bank_name', 'name']
    
    fieldsets = (
        ('Información Básica', {
            'fields': ('user', 'name', 'bank_name', 'account_number', 'account_type')
        }),
        ('Balance', {
            'fields': ('initial_balance', 'current_balance', 'currency')
        }),
        ('Configuración', {
            'fields': ('is_active', 'include_in_reports')
        }),
        ('Metadatos', {
            'fields': ('transaction_count', 'created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )
    
    def formatted_current_balance(self, obj):
        """Balance formateado con color"""
        balance = obj.current_balance
        color = 'green' if balance >= 0 else 'red'
        return format_html(
            '<span style="color: {};">{} {:.2f}</span>',
            color, obj.currency, balance
        )
    formatted_current_balance.short_description = 'Balance Actual'
    formatted_current_balance.admin_order_field = 'current_balance'
    
    def transaction_count(self, obj):
        """Número de transacciones asociadas"""
        from django.db.models import Q
        return Transaction.objects.filter(
            Q(from_account=obj) | Q(to_account=obj)
        ).count()
    transaction_count.short_description = 'Transacciones'
    
    actions = ['recalculate_balances', 'activate_accounts', 'deactivate_accounts']
    
    def recalculate_balances(self, request, queryset):
        """Recalcular balances de cuentas seleccionadas"""
        updated = 0
        for account in queryset:
            account.update_balance()
            updated += 1
        
        self.message_user(
            request,
            f'Se recalcularon los balances de {updated} cuenta(s).'
        )
    recalculate_balances.short_description = 'Recalcular balances'
    
    def activate_accounts(self, request, queryset):
        """Activar cuentas seleccionadas"""
        updated = queryset.update(is_active=True)
        self.message_user(
            request,
            f'Se activaron {updated} cuenta(s).'
        )
    activate_accounts.short_description = 'Activar cuentas'
    
    def deactivate_accounts(self, request, queryset):
        """Desactivar cuentas seleccionadas"""
        updated = queryset.update(is_active=False)
        self.message_user(
            request,
            f'Se desactivaron {updated} cuenta(s).'
        )
    deactivate_accounts.short_description = 'Desactivar cuentas'
