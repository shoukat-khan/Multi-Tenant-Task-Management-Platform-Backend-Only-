from django.contrib import admin
from .models import Task, TaskComment, TaskAttachment


@admin.register(TaskComment)
class TaskCommentAdmin(admin.ModelAdmin):
    """Admin configuration for TaskComment model."""
    list_display = ['task', 'author', 'created_at']
    list_filter = ['created_at', 'author__role']
    search_fields = ['content', 'task__title', 'author__email', 'author__first_name', 'author__last_name']
    list_select_related = ['task', 'author']
    date_hierarchy = 'created_at'
    readonly_fields = ['created_at', 'updated_at']
    
    def get_queryset(self, request):
        return super().get_queryset(request).select_related('task', 'author')


@admin.register(TaskAttachment)
class TaskAttachmentAdmin(admin.ModelAdmin):
    """Admin configuration for TaskAttachment model."""
    list_display = ['filename', 'task', 'uploaded_by', 'file_size', 'uploaded_at']
    list_filter = ['uploaded_at', 'uploaded_by__role']
    search_fields = ['filename', 'task__title', 'uploaded_by__email', 'uploaded_by__first_name', 'uploaded_by__last_name']
    list_select_related = ['task', 'uploaded_by']
    date_hierarchy = 'uploaded_at'
    readonly_fields = ['uploaded_at', 'file_size']
    
    def get_queryset(self, request):
        return super().get_queryset(request).select_related('task', 'uploaded_by')


@admin.register(Task)
class TaskAdmin(admin.ModelAdmin):
    """Admin configuration for Task model."""
    list_display = ['title', 'project', 'team', 'assigned_to', 'status', 'priority', 'is_overdue', 'created_at']
    list_filter = ['status', 'priority', 'is_active', 'is_public', 'created_at', 'team', 'project']
    search_fields = ['title', 'description', 'project__name', 'team__name', 'assigned_to__email', 'assigned_to__first_name', 'assigned_to__last_name']
    list_select_related = ['project', 'team', 'assigned_to', 'created_by']
    date_hierarchy = 'created_at'
    
    fieldsets = (
        ('Basic Information', {
            'fields': ('title', 'description', 'project', 'team', 'assigned_to', 'created_by')
        }),
        ('Status & Priority', {
            'fields': ('status', 'priority')
        }),
        ('Dates', {
            'fields': ('due_date', 'started_at', 'completed_at')
        }),
        ('Time Tracking', {
            'fields': ('estimated_hours', 'actual_hours')
        }),
        ('Settings', {
            'fields': ('is_active', 'is_public')
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )
    
    readonly_fields = ['created_at', 'updated_at', 'started_at', 'completed_at', 'created_by']
    
    def is_overdue(self, obj):
        """Display overdue status in admin list."""
        return obj.is_overdue()
    is_overdue.boolean = True
    is_overdue.short_description = 'Overdue'
    
    def get_queryset(self, request):
        return super().get_queryset(request).select_related('project', 'team', 'assigned_to', 'created_by')
    
    def save_model(self, request, obj, form, change):
        """Set created_by when creating a new task."""
        if not change:  # Only for new objects
            obj.created_by = request.user
        super().save_model(request, obj, form, change)
