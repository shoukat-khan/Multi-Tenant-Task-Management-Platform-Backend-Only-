"""
Filters for Project management.
"""
import django_filters
from django.db import models
from .models import Project


class ProjectFilter(django_filters.FilterSet):
    """
    Filter class for Project model with advanced filtering options.
    """
    # Status filtering
    status = django_filters.ChoiceFilter(
        choices=Project.STATUS_CHOICES,
        help_text="Filter projects by status"
    )
    
    # Priority filtering
    priority = django_filters.ChoiceFilter(
        choices=Project.PRIORITY_CHOICES,
        help_text="Filter projects by priority"
    )
    
    # Team filtering
    team = django_filters.NumberFilter(
        field_name='team__id',
        help_text="Filter projects by team ID"
    )
    team_name = django_filters.CharFilter(
        field_name='team__name',
        lookup_expr='icontains',
        help_text="Filter projects by team name"
    )
    
    # Owner filtering
    manager = django_filters.NumberFilter(
        field_name='manager__id',
        help_text="Filter projects by manager/owner ID"
    )
    manager_email = django_filters.CharFilter(
        field_name='manager__email',
        lookup_expr='icontains',
        help_text="Filter projects by manager email"
    )
    created_by = django_filters.NumberFilter(
        field_name='created_by__id',
        help_text="Filter projects by creator ID"
    )
    
    # Date range filtering
    start_date = django_filters.DateFilter(
        help_text="Filter projects by exact start date"
    )
    start_date_after = django_filters.DateFilter(
        field_name='start_date',
        lookup_expr='gte',
        help_text="Filter projects starting after this date"
    )
    start_date_before = django_filters.DateFilter(
        field_name='start_date',
        lookup_expr='lte',
        help_text="Filter projects starting before this date"
    )
    
    end_date = django_filters.DateFilter(
        help_text="Filter projects by exact end date"
    )
    end_date_after = django_filters.DateFilter(
        field_name='end_date',
        lookup_expr='gte',
        help_text="Filter projects ending after this date"
    )
    end_date_before = django_filters.DateFilter(
        field_name='end_date',
        lookup_expr='lte',
        help_text="Filter projects ending before this date"
    )
    
    # Date range filtering with date range widget
    created_at_range = django_filters.DateRangeFilter(
        field_name='created_at',
        help_text="Filter projects by creation date range"
    )
    
    # Search-like filters
    name = django_filters.CharFilter(
        lookup_expr='icontains',
        help_text="Search projects by name"
    )
    description = django_filters.CharFilter(
        lookup_expr='icontains',
        help_text="Search projects by description"
    )
    
    # Budget filtering
    budget_min = django_filters.NumberFilter(
        field_name='budget',
        lookup_expr='gte',
        help_text="Filter projects with budget greater than or equal to this amount"
    )
    budget_max = django_filters.NumberFilter(
        field_name='budget',
        lookup_expr='lte',
        help_text="Filter projects with budget less than or equal to this amount"
    )
    
    # Boolean filters
    is_active = django_filters.BooleanFilter(
        help_text="Filter active/inactive projects"
    )
    is_overdue = django_filters.BooleanFilter(
        method='filter_overdue',
        help_text="Filter overdue projects"
    )
    
    class Meta:
        model = Project
        fields = {
            'status': ['exact'],
            'priority': ['exact'],
            'created_at': ['exact', 'gte', 'lte'],
            'updated_at': ['exact', 'gte', 'lte'],
            'is_active': ['exact'],
        }
    
    def filter_overdue(self, queryset, name, value):
        """
        Custom filter method to filter overdue projects.
        """
        if value is True:
            from django.utils import timezone
            now = timezone.now().date()
            return queryset.filter(
                end_date__lt=now,
                status__in=['planning', 'active', 'on_hold']
            )
        elif value is False:
            from django.utils import timezone
            now = timezone.now().date()
            return queryset.exclude(
                end_date__lt=now,
                status__in=['planning', 'active', 'on_hold']
            )
        return queryset
