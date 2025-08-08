from django.contrib import admin
from django.utils.html import format_html

from .models import Transaction, Category

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

@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ['name', 'category_type', 'parent', 'is_active', 'transaction_count', 'color_preview']
    list_filter = ['category_type', 'is_active', 'parent']
    search_fields = ['name', 'slug']
    prepopulated_fields = {'slug': ('name',)}
    ordering = ['sort_order', 'name']
    
    fieldsets = (
        ('Información Básica', {
            'fields': ('name', 'slug', 'category_type', 'parent')
        }),
        ('Apariencia', {
            'fields': ('icon', 'color', 'sort_order')
        }),
        ('Configuración', {
            'fields': ('is_active',)
        }),
    )
    
    def color_preview(self, obj):
        """Preview del color"""
        return format_html(
            '<div style="width: 20px; height: 20px; background-color: {}; border: 1px solid #ccc;"></div>',
            obj.color
        )
    color_preview.short_description = 'Color'
    
    def transaction_count(self, obj):
        """Número de transacciones"""
        return obj.transaction_set.count()
    transaction_count.short_description = 'Transacciones'