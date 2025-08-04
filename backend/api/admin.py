from django.contrib import admin
from django.db.models import Sum
from django.utils.html import format_html
from .models import Transaction, Account, UserProfile

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

@admin.register(Transaction)
class TransactionAdmin(admin.ModelAdmin):
    list_display = [
        'title', 'formatted_amount', 'type', 'date', 
        'from_account_info', 'to_account_info', 'user', 'is_recurring'
    ]
    list_filter = [
        'type', 'date', 'is_recurring', 'recurring_frequency',
        'from_account__bank_name', 'to_account__bank_name',
        'from_account__account_type', 'to_account__account_type'
    ]
    search_fields = [
        'title', 'description', 'reference_number', 'location',
        'user__username', 'from_account__name', 'to_account__name'
    ]
    readonly_fields = ['created_at', 'updated_at']
    date_hierarchy = 'date'
    ordering = ['-date', '-created_at']
    
    fieldsets = (
        ('Información Básica', {
            'fields': ('user', 'title', 'amount', 'type', 'date', 'description')
        }),
        ('Cuentas', {
            'fields': ('from_account', 'to_account')
        }),
        ('Detalles Adicionales', {
            'fields': ('reference_number', 'location', 'tags'),
            'classes': ('collapse',)
        }),
        ('Recurrencia', {
            'fields': ('is_recurring', 'recurring_frequency', 'parent_transaction'),
            'classes': ('collapse',)
        }),
        ('Metadatos', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )
    
    def formatted_amount(self, obj):
        """Monto formateado con color según tipo"""
        colors = {
            'income': 'green',
            'expense': 'red',
            'investment': 'blue',
            'transfer': 'orange',
            'loan': 'purple',
            'debt': 'brown',
            'savings': 'teal',
            'other': 'gray'
        }
        color = colors.get(obj.type, 'black')
        return format_html(
            '<span style="color: {}; font-weight: bold;">${:.2f}</span>',
            color, obj.amount
        )
    formatted_amount.short_description = 'Monto'
    formatted_amount.admin_order_field = 'amount'
    
    def from_account_info(self, obj):
        """Información de cuenta origen"""
        if obj.from_account:
            return f"{obj.from_account.bank_name} - {obj.from_account.name}"
        return "-"
    from_account_info.short_description = 'Cuenta Origen'
    
    def to_account_info(self, obj):
        """Información de cuenta destino"""
        if obj.to_account:
            return f"{obj.to_account.bank_name} - {obj.to_account.name}"
        return "-"
    to_account_info.short_description = 'Cuenta Destino'
    
    actions = ['duplicate_transactions', 'mark_as_recurring']
    
    def duplicate_transactions(self, request, queryset):
        """Duplicar transacciones seleccionadas"""
        duplicated = 0
        for transaction in queryset:
            Transaction.objects.create(
                user=transaction.user,
                title=f"Copia de {transaction.title}",
                amount=transaction.amount,
                type=transaction.type,
                date=transaction.date,
                description=transaction.description,
                from_account=transaction.from_account,
                to_account=transaction.to_account,
                reference_number=f"COPY_{transaction.reference_number}",
                location=transaction.location,
                tags=transaction.tags
            )
            duplicated += 1
        
        self.message_user(
            request,
            f'Se duplicaron {duplicated} transacción(es).'
        )
    duplicate_transactions.short_description = 'Duplicar transacciones'
    
    def mark_as_recurring(self, request, queryset):
        """Marcar como recurrentes"""
        updated = queryset.update(is_recurring=True)
        self.message_user(
            request,
            f'Se marcaron {updated} transacción(es) como recurrentes.'
        )
    mark_as_recurring.short_description = 'Marcar como recurrentes'

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

# Personalización del admin site
admin.site.site_header = "FinTrack Admin"
admin.site.site_title = "FinTrack Admin"
admin.site.index_title = "Panel de Administración"