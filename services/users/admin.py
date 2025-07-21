from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from django.utils.html import format_html
from .models import User, UserProfile


class UserProfileInline(admin.StackedInline):
    model = UserProfile
    fk_name = 'user'  # Specify which foreign key to use
    extra = 0
    fields = [
        'bio', 'department', 'employee_id', 'hire_date', 
        'manager', 'timezone', 'preferences'
    ]


@admin.register(User)
class UserAdmin(BaseUserAdmin):
    inlines = [UserProfileInline]
    
    list_display = [
        'email', 'full_name', 'role', 'is_active', 
        'date_joined'
    ]
    list_filter = [
        'is_active', 'is_staff', 'is_superuser', 'role', 'date_joined'
    ]
    search_fields = ['email', 'first_name', 'last_name', 'username']
    ordering = ['-date_joined']
    
    fieldsets = (
        (None, {
            'fields': ('username', 'email', 'password', 'role')
        }),
        ('Personal info', {
            'fields': ('first_name', 'last_name')
        }),
        ('Permissions', {
            'fields': (
                'is_active', 'is_staff', 'is_superuser', 
                'groups', 'user_permissions'
            ),
        }),
        ('Important dates', {
            'fields': ('last_login', 'date_joined')
        }),
    )
    
    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': (
                'username', 'email', 'first_name', 'last_name',
                'role', 'password1', 'password2'
            ),
        }),
    )
    
    readonly_fields = ['last_login', 'date_joined']
    
    def full_name(self, obj):
        """Display full name in list view."""
        return obj.get_full_name()
    full_name.short_description = 'Full Name'


@admin.register(UserProfile)
class UserProfileAdmin(admin.ModelAdmin):
    list_display = [
        'user', 'department', 'employee_id', 'manager', 'hire_date'
    ]
    list_filter = ['department', 'hire_date', 'timezone']
    search_fields = [
        'user__email', 'user__first_name', 'user__last_name',
        'department', 'employee_id'
    ]
    ordering = ['-created_at']
    
    fieldsets = (
        ('User', {
            'fields': ('user',)
        }),
        ('Work Information', {
            'fields': ('department', 'employee_id', 'hire_date', 'manager')
        }),
        ('Personal Information', {
            'fields': ('bio', 'timezone')
        }),
        ('Preferences', {
            'fields': ('preferences',),
            'classes': ('collapse',)
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )
    
    readonly_fields = ['created_at', 'updated_at']
