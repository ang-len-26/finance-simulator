from django.contrib import admin
from django.utils.html import format_html

from .models import FinancialGoal, GoalContribution, GoalTemplate, GoalMilestone

@admin.register(FinancialGoal)
class FinancialGoalAdmin(admin.ModelAdmin):
    list_display = ['title', 'user', 'goal_type', 'status', 'progress_display', 'target_amount', 'days_remaining', 'created_at']
    list_filter = ['goal_type', 'status', 'priority', 'created_at']
    search_fields = ['title', 'user__username']
    readonly_fields = ['progress_percentage', 'remaining_amount', 'days_remaining', 'is_overdue']
    
    def progress_display(self, obj):
        return format_html(
            '<div style="width: 100px; background: #f0f0f0; border-radius: 5px;">'
            '<div style="width: {}%; background: #10b981; height: 20px; border-radius: 5px;"></div>'
            '</div> {}%',
            min(obj.progress_percentage, 100),
            round(obj.progress_percentage, 1)
        )
    progress_display.short_description = 'Progreso'

@admin.register(GoalContribution)
class GoalContributionAdmin(admin.ModelAdmin):
    list_display = ['goal', 'amount', 'date', 'contribution_type', 'from_account']
    list_filter = ['contribution_type', 'date', 'is_recurring']
    search_fields = ['goal__title', 'notes']

@admin.register(GoalTemplate)
class GoalTemplateAdmin(admin.ModelAdmin):
    list_display = ['name', 'goal_type', 'suggested_amount', 'suggested_timeframe_months', 'is_active']
    list_filter = ['goal_type', 'is_active']
    ordering = ['sort_order']

@admin.register(GoalMilestone)
class GoalMilestoneAdmin(admin.ModelAdmin):
    list_display = ['goal', 'title', 'target_amount', 'target_date', 'is_completed']
    list_filter = ['is_completed', 'target_date']