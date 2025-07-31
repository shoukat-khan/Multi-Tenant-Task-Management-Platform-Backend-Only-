"""
Filters for Task management.
"""
import django_filters
from django.db import models
from django_filters import rest_framework as filters
from .models import Task


class TaskFilter(django_filters.FilterSet):
    """
    Filter class for Task model with advanced filtering options.
    """
    # Status filtering
    status = django_filters.ChoiceFilter(
        choices=Task.STATUS_CHOICES,
        help_text="Filter tasks by status"
    )
    
    # Priority filtering
    priority = django_filters.ChoiceFilter(
        choices=Task.PRIORITY_CHOICES,
        help_text="Filter tasks by priority"
    )
    
    # Date range filtering
    due_date = django_filters.DateFilter(
        help_text="Filter tasks by exact due date"
    )
    due_date_after = django_filters.DateFilter(
        field_name='due_date',
        lookup_expr='gte',
        help_text="Filter tasks due after this date"
    )
    due_date_before = django_filters.DateFilter(
        field_name='due_date',
        lookup_expr='lte',
        help_text="Filter tasks due before this date"
    )
    
    # User filtering
    assigned_to = django_filters.NumberFilter(
        field_name='assigned_to__id',
        help_text="Filter tasks by assigned user ID"
    )
    assigned_to_email = django_filters.CharFilter(
        field_name='assigned_to__email',
        lookup_expr='icontains',
        help_text="Filter tasks by assigned user email"
    )
    created_by = django_filters.NumberFilter(
        field_name='created_by__id',
        help_text="Filter tasks by creator user ID"
    )
    
    # Project and Team filtering
    project = django_filters.NumberFilter(
        field_name='project__id',
        help_text="Filter tasks by project ID"
    )
    project_name = django_filters.CharFilter(
        field_name='project__name',
        lookup_expr='icontains',
        help_text="Filter tasks by project name"
    )
    team = django_filters.NumberFilter(
        field_name='team__id',
        help_text="Filter tasks by team ID"
    )
    team_name = django_filters.CharFilter(
        field_name='team__name',
        lookup_expr='icontains',
        help_text="Filter tasks by team name"
    )
    
    # Date range filtering with date range widget
    created_at_range = django_filters.DateRangeFilter(
        field_name='created_at',
        help_text="Filter tasks by creation date range"
    )
    
    # Boolean filters
    is_overdue = django_filters.BooleanFilter(
        method='filter_overdue',
        help_text="Filter overdue tasks"
    )
    
    # Search-like filters
    title = django_filters.CharFilter(
        lookup_expr='icontains',
        help_text="Search tasks by title"
    )
    description = django_filters.CharFilter(
        lookup_expr='icontains',
        help_text="Search tasks by description"
    )
    
    class Meta:
        model = Task
        fields = {
            'status': ['exact'],
            'priority': ['exact'],
            'due_date': ['exact', 'gte', 'lte'],
            'created_at': ['exact', 'gte', 'lte'],
            'updated_at': ['exact', 'gte', 'lte'],
            'is_active': ['exact'],
            'is_public': ['exact'],
        }
    
    def filter_overdue(self, queryset, name, value):
        """
        Custom filter method to filter overdue tasks.
        """
        if value is True:
            from django.utils import timezone
            now = timezone.now()
            return queryset.filter(
                due_date__lt=now,
                status__in=['todo', 'in_progress', 'review']
            )
        elif value is False:
            from django.utils import timezone
            now = timezone.now()
            return queryset.exclude(
                due_date__lt=now,
                status__in=['todo', 'in_progress', 'review']
            )
        return queryset
