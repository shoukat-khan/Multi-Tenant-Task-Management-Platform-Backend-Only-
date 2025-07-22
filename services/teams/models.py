from django.db import models
from Services.users.models import User


class Team(models.Model):
    """
    Team model for organizing users into groups.
    """
    name = models.CharField(
        max_length=100,
        help_text="Name of the team"
    )
    description = models.TextField(
        blank=True,
        null=True,
        help_text="Description of the team"
    )
    manager = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='managed_teams',
        help_text="Team manager"
    )
    members = models.ManyToManyField(
        User,
        through='TeamMembership',
        related_name='teams',
        help_text="Team members"
    )
    
    # Team settings
    is_active = models.BooleanField(
        default=True,
        help_text="Whether the team is active"
    )
    max_members = models.PositiveIntegerField(
        default=20,
        help_text="Maximum number of team members"
    )
    
    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'teams'
        verbose_name = 'Team'
        verbose_name_plural = 'Teams'
        ordering = ['-created_at']
    
    def __str__(self):
        return f"{self.name} (Manager: {self.manager.get_full_name()})"
    
    def get_member_count(self):
        """Get the number of team members."""
        return self.members.count()
    
    def can_add_member(self):
        """Check if team can accept more members."""
        return self.get_member_count() < self.max_members
    
    def is_member(self, user):
        """Check if user is a member of this team."""
        return self.members.filter(id=user.id).exists()
    
    def is_manager(self, user):
        """Check if user is the manager of this team."""
        return self.manager == user


class TeamMembership(models.Model):
    """
    Through model for Team-Member relationship with additional fields.
    """
    ROLE_CHOICES = [
        ('member', 'Member'),
        ('lead', 'Lead'),
        ('senior', 'Senior Member'),
    ]
    
    team = models.ForeignKey(
        Team,
        on_delete=models.CASCADE,
        related_name='memberships'
    )
    member = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='team_memberships'
    )
    role = models.CharField(
        max_length=20,
        choices=ROLE_CHOICES,
        default='member',
        help_text="Role within the team"
    )
    joined_at = models.DateTimeField(auto_now_add=True)
    is_active = models.BooleanField(default=True)
    
    class Meta:
        db_table = 'team_memberships'
        unique_together = ['team', 'member']
        verbose_name = 'Team Membership'
        verbose_name_plural = 'Team Memberships'
    
    def __str__(self):
        return f"{self.member.get_full_name()} - {self.team.name} ({self.get_role_display()})"
