from django.db import models
from services.users.models import User
from services.teams.models import Team
from services.projects.models import Project


class Task(models.Model):
    """
    Task model for individual work items.
    """
    STATUS_CHOICES = [
        ('todo', 'To Do'),
        ('in_progress', 'In Progress'),
        ('review', 'In Review'),
        ('completed', 'Completed'),
        ('cancelled', 'Cancelled'),
    ]
    
    PRIORITY_CHOICES = [
        ('low', 'Low'),
        ('medium', 'Medium'),
        ('high', 'High'),
        ('urgent', 'Urgent'),
    ]
    
    title = models.CharField(
        max_length=200,
        help_text="Title of the task"
    )
    description = models.TextField(
        blank=True,
        null=True,
        help_text="Detailed description of the task"
    )
    
    # Task relationships
    project = models.ForeignKey(
        Project,
        on_delete=models.CASCADE,
        related_name='tasks',
        help_text="Project this task belongs to"
    )
    team = models.ForeignKey(
        Team,
        on_delete=models.CASCADE,
        related_name='tasks',
        help_text="Team responsible for the task"
    )
    assigned_to = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='assigned_tasks',
        help_text="User assigned to this task"
    )
    created_by = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='created_tasks',
        help_text="User who created the task"
    )
    
    # Task details
    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default='todo',
        help_text="Current status of the task"
    )
    priority = models.CharField(
        max_length=20,
        choices=PRIORITY_CHOICES,
        default='medium',
        help_text="Priority level of the task"
    )
    
    # Dates
    due_date = models.DateTimeField(
        null=True,
        blank=True,
        help_text="Task due date"
    )
    started_at = models.DateTimeField(
        null=True,
        blank=True,
        help_text="When work on the task started"
    )
    completed_at = models.DateTimeField(
        null=True,
        blank=True,
        help_text="When the task was completed"
    )
    
    # Task metadata
    estimated_hours = models.DecimalField(
        max_digits=6,
        decimal_places=2,
        null=True,
        blank=True,
        help_text="Estimated hours to complete the task"
    )
    actual_hours = models.DecimalField(
        max_digits=6,
        decimal_places=2,
        null=True,
        blank=True,
        help_text="Actual hours spent on the task"
    )
    
    # Task settings
    is_active = models.BooleanField(
        default=True,
        help_text="Whether the task is active"
    )
    is_public = models.BooleanField(
        default=True,
        help_text="Whether the task is visible to all team members"
    )
    
    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'tasks'
        verbose_name = 'Task'
        verbose_name_plural = 'Tasks'
        ordering = ['-created_at']
    
    def __str__(self):
        return f"{self.title} - {self.get_status_display()}"
    
    def is_overdue(self):
        """Check if task is overdue."""
        if self.due_date and self.status not in ['completed', 'cancelled']:
            from django.utils import timezone
            return timezone.now() > self.due_date
        return False
    
    def can_be_accessed_by(self, user):
        """Check if user can access this task."""
        # Admin can access all tasks
        if user.has_role('admin'):
            return True
        
        # Task creator can always access
        if user == self.created_by:
            return True
        
        # Assigned user can access
        if user == self.assigned_to:
            return True
        
        # Team manager can access
        if user == self.team.manager:
            return True
        
        # Project manager can access
        if user == self.project.manager:
            return True
        
        # Team members can access if task is public
        if self.is_public and self.team.is_member(user):
            return True
        
        return False
    
    def can_be_edited_by(self, user):
        """Check if user can edit this task."""
        # Admin can edit all tasks
        if user.has_role('admin'):
            return True
        
        # Task creator can edit
        if user == self.created_by:
            return True
        
        # Assigned user can edit
        if user == self.assigned_to:
            return True
        
        # Team manager can edit
        if user == self.team.manager:
            return True
        
        # Project manager can edit
        if user == self.project.manager:
            return True
        
        return False


class TaskComment(models.Model):
    """
    Comments on tasks for collaboration.
    """
    task = models.ForeignKey(
        Task,
        on_delete=models.CASCADE,
        related_name='comments',
        help_text="Task this comment belongs to"
    )
    author = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='task_comments',
        help_text="User who wrote the comment"
    )
    content = models.TextField(
        help_text="Comment content"
    )
    
    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'task_comments'
        verbose_name = 'Task Comment'
        verbose_name_plural = 'Task Comments'
        ordering = ['created_at']
    
    def __str__(self):
        return f"Comment by {self.author.get_full_name()} on {self.task.title}"


class TaskAttachment(models.Model):
    """
    File attachments for tasks.
    """
    task = models.ForeignKey(
        Task,
        on_delete=models.CASCADE,
        related_name='attachments',
        help_text="Task this attachment belongs to"
    )
    uploaded_by = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='task_attachments',
        help_text="User who uploaded the file"
    )
    file = models.FileField(
        upload_to='task_attachments/',
        help_text="Uploaded file"
    )
    filename = models.CharField(
        max_length=255,
        help_text="Original filename"
    )
    file_size = models.PositiveIntegerField(
        help_text="File size in bytes"
    )
    
    # Timestamps
    uploaded_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        db_table = 'task_attachments'
        verbose_name = 'Task Attachment'
        verbose_name_plural = 'Task Attachments'
        ordering = ['-uploaded_at']
    
    def __str__(self):
        return f"{self.filename} - {self.task.title}"
