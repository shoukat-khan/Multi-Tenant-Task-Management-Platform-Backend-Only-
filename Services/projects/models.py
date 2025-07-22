from django.db import models
from Services.users.models import User
from Services.teams.models import Team


class Project(models.Model):
    """
    Project model for organizing work and tasks.
    """
    STATUS_CHOICES = [
        ('planning', 'Planning'),
        ('active', 'Active'),
        ('on_hold', 'On Hold'),
        ('completed', 'Completed'),
        ('cancelled', 'Cancelled'),
    ]
    
    PRIORITY_CHOICES = [
        ('low', 'Low'),
        ('medium', 'Medium'),
        ('high', 'High'),
        ('urgent', 'Urgent'),
    ]
    
    name = models.CharField(
        max_length=200,
        help_text="Name of the project"
    )
    description = models.TextField(
        blank=True,
        null=True,
        help_text="Description of the project"
    )
    
    # Project relationships
    team = models.ForeignKey(
        Team,
        on_delete=models.CASCADE,
        related_name='projects',
        help_text="Team responsible for the project"
    )
    manager = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='managed_projects',
        help_text="Project manager"
    )
    created_by = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='created_projects',
        help_text="User who created the project"
    )
    
    # Project details
    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default='planning',
        help_text="Current status of the project"
    )
    priority = models.CharField(
        max_length=20,
        choices=PRIORITY_CHOICES,
        default='medium',
        help_text="Priority level of the project"
    )
    
    # Dates
    start_date = models.DateField(
        null=True,
        blank=True,
        help_text="Project start date"
    )
    end_date = models.DateField(
        null=True,
        blank=True,
        help_text="Project end date"
    )
    completed_date = models.DateField(
        null=True,
        blank=True,
        help_text="Date when project was completed"
    )
    
    # Project settings
    is_active = models.BooleanField(
        default=True,
        help_text="Whether the project is active"
    )
    budget = models.DecimalField(
        max_digits=12,
        decimal_places=2,
        null=True,
        blank=True,
        help_text="Project budget"
    )
    
    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'projects'
        verbose_name = 'Project'
        verbose_name_plural = 'Projects'
        ordering = ['-created_at']
    
    def __str__(self):
        return f"{self.name} - {self.get_status_display()}"
    
    def get_task_count(self):
        """Get the number of tasks in this project."""
        return self.tasks.count()
    
    def get_completed_task_count(self):
        """Get the number of completed tasks in this project."""
        return self.tasks.filter(status='completed').count()
    
    def get_progress_percentage(self):
        """Calculate project progress based on completed tasks."""
        total_tasks = self.get_task_count()
        if total_tasks == 0:
            return 0
        completed_tasks = self.get_completed_task_count()
        return round((completed_tasks / total_tasks) * 100, 2)
    
    def is_overdue(self):
        """Check if project is overdue."""
        if self.end_date and self.status not in ['completed', 'cancelled']:
            from django.utils import timezone
            return timezone.now().date() > self.end_date
        return False
    
    def can_be_managed_by(self, user):
        """Check if user can manage this project."""
        return (
            user == self.manager or
            user == self.team.manager or
            user.has_role('admin')
        )
    
    def can_be_accessed_by(self, user):
        """Check if user can access this project."""
        # Admin can access all projects
        if user.has_role('admin'):
            return True
        
        # Project manager can access
        if user == self.manager:
            return True
        
        # Team manager can access
        if user == self.team.manager:
            return True
        
        # Team members can access
        if self.team.is_member(user):
            return True
        
        return False
