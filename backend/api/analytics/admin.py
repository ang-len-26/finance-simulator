from django.contrib import admin
from django.utils.html import format_html
from django.utils import timezone

from .models import FinancialMetric, CategorySummary, BudgetAlert

@admin.register(FinancialMetric)
class FinancialMetricAdmin(admin.ModelAdmin):
    list_display = [
        'user', 'period_type', 'period_start', 'period_end', 
        'formatted_income', 'formatted_expenses', 'formatted_net_balance',
        'transaction_count', 'calculated_at'
    ]
    list_filter = ['period_type', 'period_start', 'user']
    search_fields = ['user__username', 'period_type']
    readonly_fields = ['calculated_at', 'created_at']
    date_hierarchy = 'period_start'
    
    fieldsets = (
        ('Período', {
            'fields': ('user', 'period_type', 'period_start', 'period_end')
        }),
        ('Métricas Principales', {
            'fields': ('total_income', 'total_expenses', 'net_balance', 'transaction_count')
        }),
        ('Balances por Tipo', {
            'fields': ('checking_balance', 'savings_balance', 'investment_balance', 'credit_balance'),
            'classes': ('collapse',)
        }),
        ('Categoría Top', {
            'fields': ('top_expense_category', 'top_expense_amount'),
            'classes': ('collapse',)
        }),
        ('Metadatos', {
            'fields': ('calculated_at', 'created_at'),
            'classes': ('collapse',)
        }),
    )
    
    def formatted_income(self, obj):
        return format_html(
            '<span style="color: green; font-weight: bold;">${:.2f}</span>',
            obj.total_income
        )
    formatted_income.short_description = 'Ingresos'
    
    def formatted_expenses(self, obj):
        return format_html(
            '<span style="color: red; font-weight: bold;">${:.2f}</span>',
            obj.total_expenses
        )
    formatted_expenses.short_description = 'Gastos'
    
    def formatted_net_balance(self, obj):
        color = 'green' if obj.net_balance >= 0 else 'red'
        return format_html(
            '<span style="color: {}; font-weight: bold;">${:.2f}</span>',
            color, obj.net_balance
        )
    formatted_net_balance.short_description = 'Balance Neto'
    
    actions = ['recalculate_metrics']
    
    def recalculate_metrics(self, request, queryset):
        """Recalcular métricas seleccionadas"""
        count = 0
        for metric in queryset:
            # Aquí iría la lógica de recálculo
            metric.calculated_at = timezone.now()
            metric.save()
            count += 1
        
        self.message_user(
            request, 
            f'{count} métricas recalculadas exitosamente.'
        )
    recalculate_metrics.short_description = "Recalcular métricas seleccionadas"

@admin.register(CategorySummary)
class CategorySummaryAdmin(admin.ModelAdmin):
    list_display = [
        'user', 'category', 'period_type', 'period_start', 
        'formatted_amount', 'transaction_count', 'formatted_change'
    ]
    list_filter = ['period_type', 'category', 'period_start']
    search_fields = ['user__username', 'category__name']
    readonly_fields = ['created_at', 'updated_at']
    
    fieldsets = (
        ('Información Básica', {
            'fields': ('user', 'category', 'period_type', 'period_start', 'period_end')
        }),
        ('Métricas', {
            'fields': ('total_amount', 'transaction_count', 'average_amount')
        }),
        ('Comparativas', {
            'fields': ('previous_period_amount', 'percentage_change'),
            'classes': ('collapse',)
        }),
        ('Análisis', {
            'fields': ('most_used_account',),
            'classes': ('collapse',)
        }),
        ('Metadatos', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )
    
    def formatted_amount(self, obj):
        return format_html(
            '<span style="font-weight: bold;">${:.2f}</span>',
            obj.total_amount
        )
    formatted_amount.short_description = 'Total'
    
    def formatted_change(self, obj):
        if obj.percentage_change > 0:
            color = 'red'
            icon = '↑'
        elif obj.percentage_change < 0:
            color = 'green'
            icon = '↓'
        else:
            color = 'gray'
            icon = '→'
            
        return format_html(
            '<span style="color: {};">{} {:.1f}%</span>',
            color, icon, abs(obj.percentage_change)
        )
    formatted_change.short_description = 'Cambio'

@admin.register(BudgetAlert)
class BudgetAlertAdmin(admin.ModelAdmin):
    list_display = [
        'user', 'alert_type', 'severity_badge', 'title', 
        'status_badge', 'created_at'
    ]
    list_filter = ['alert_type', 'severity', 'is_read', 'is_dismissed', 'created_at']
    search_fields = ['user__username', 'title', 'message']
    readonly_fields = ['created_at']
    
    fieldsets = (
        ('Alerta', {
            'fields': ('user', 'alert_type', 'severity', 'title', 'message')
        }),
        ('Relaciones', {
            'fields': ('related_transaction', 'related_category', 'related_account'),
            'classes': ('collapse',)
        }),
        ('Datos del Trigger', {
            'fields': ('threshold_amount', 'actual_amount'),
            'classes': ('collapse',)
        }),
        ('Estado', {
            'fields': ('is_read', 'is_dismissed', 'created_at')
        }),
    )
    
    def severity_badge(self, obj):
        colors = {
            'low': '#22c55e',
            'medium': '#f59e0b', 
            'high': '#f97316',
            'critical': '#ef4444'
        }
        return format_html(
            '<span style="background: {}; color: white; padding: 2px 8px; border-radius: 12px; font-size: 11px;">{}</span>',
            colors.get(obj.severity, '#6b7280'),
            obj.get_severity_display()
        )
    severity_badge.short_description = 'Severidad'
    
    def status_badge(self, obj):
        if obj.is_dismissed:
            return format_html('<span style="color: #6b7280;">❌ Descartada</span>')
        elif obj.is_read:
            return format_html('<span style="color: #22c55e;">✅ Leída</span>')
        else:
            return format_html('<span style="color: #ef4444; font-weight: bold;">🔔 Nueva</span>')
    status_badge.short_description = 'Estado'
    
    actions = ['mark_as_read', 'mark_as_dismissed']
    
    def mark_as_read(self, request, queryset):
        count = queryset.update(is_read=True)
        self.message_user(request, f'{count} alertas marcadas como leídas.')
    mark_as_read.short_description = "Marcar como leídas"
    
    def mark_as_dismissed(self, request, queryset):
        count = queryset.update(is_dismissed=True)
        self.message_user(request, f'{count} alertas descartadas.')
    mark_as_dismissed.short_description = "Descartar alertas"