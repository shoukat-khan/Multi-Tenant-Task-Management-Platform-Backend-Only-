from django.contrib import admin
from .models import Project


@admin.register(Project)
class ProjectAdmin(admin.ModelAdmin):
    """Admin configuration for Project model."""
    list_display = ['name', 'team', 'manager', 'status', 'priority', 'get_task_count', 'is_active', 'created_at']
    list_filter = ['status', 'priority', 'is_active', 'created_at', 'team', 'manager__role']
    search_fields = ['name', 'description', 'team__name', 'manager__email', 'manager__first_name', 'manager__last_name']
    list_select_related = ['team', 'manager', 'created_by']
    date_hierarchy = 'created_at'
    
    fieldsets = (
        ('Basic Information', {
            'fields': ('name', 'description', 'team', 'manager', 'created_by')
        }),
        ('Status & Priority', {
            'fields': ('status', 'priority')
        }),
        ('Dates', {
            'fields': ('start_date', 'end_date', 'completed_date')
        }),
        ('Settings', {
            'fields': ('is_active', 'budget')
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )
    
    readonly_fields = ['created_at', 'updated_at', 'created_by']
    
    def get_task_count(self, obj):
        """Display task count in admin list."""
        return obj.get_task_count()
    get_task_count.short_description = 'Tasks'
    
    def get_queryset(self, request):
        return super().get_queryset(request).select_related('team', 'manager', 'created_by')
    
    def save_model(self, request, obj, form, change):
        """Set created_by when creating a new project."""
        if not change:  # Only for new objects
            obj.created_by = request.user
        super().save_model(request, obj, form, change)
