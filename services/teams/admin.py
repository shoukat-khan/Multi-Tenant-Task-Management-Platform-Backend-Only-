from django.contrib import admin
from .models import Team, TeamMembership


@admin.register(TeamMembership)
class TeamMembershipAdmin(admin.ModelAdmin):
    """Admin configuration for TeamMembership model."""
    list_display = ['member', 'team', 'role', 'joined_at', 'is_active']
    list_filter = ['role', 'is_active', 'joined_at', 'team']
    search_fields = ['member__email', 'member__first_name', 'member__last_name', 'team__name']
    list_select_related = ['member', 'team']
    date_hierarchy = 'joined_at'
    
    def get_queryset(self, request):
        return super().get_queryset(request).select_related('member', 'team')


@admin.register(Team)
class TeamAdmin(admin.ModelAdmin):
    """Admin configuration for Team model."""
    list_display = ['name', 'manager', 'get_member_count', 'is_active', 'created_at']
    list_filter = ['is_active', 'created_at', 'manager__role']
    search_fields = ['name', 'description', 'manager__email', 'manager__first_name', 'manager__last_name']
    list_select_related = ['manager']
    date_hierarchy = 'created_at'

    
    fieldsets = (
        ('Basic Information', {
            'fields': ('name', 'description', 'manager')
        }),
        ('Settings', {
            'fields': ('is_active', 'max_members')
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )
    
    readonly_fields = ['created_at', 'updated_at']
    
    def get_member_count(self, obj):
        """Display member count in admin list."""
        return obj.get_member_count()
    get_member_count.short_description = 'Members'
    
    def get_queryset(self, request):
        return super().get_queryset(request).select_related('manager')
