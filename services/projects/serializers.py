from rest_framework import serializers
from services.users.models import User
from services.teams.models import Team
from services.users.serializers import UserListSerializer
from services.teams.serializers import TeamSerializer
from .models import Project


class ProjectSerializer(serializers.ModelSerializer):
    """
    Basic serializer for Project model.
    """
    manager_name = serializers.CharField(source='manager.get_full_name', read_only=True)
    team_name = serializers.CharField(source='team.name', read_only=True)
    created_by_name = serializers.CharField(source='created_by.get_full_name', read_only=True)
    task_count = serializers.SerializerMethodField()
    progress_percentage = serializers.SerializerMethodField()
    is_overdue = serializers.SerializerMethodField()
    
    class Meta:
        model = Project
        fields = [
            'id', 'name', 'description', 'team', 'team_name', 'manager', 'manager_name',
            'created_by', 'created_by_name', 'status', 'priority', 'start_date', 'end_date',
            'completed_date', 'is_active', 'budget', 'task_count', 'progress_percentage',
            'is_overdue', 'created_at', 'updated_at'
        ]
        read_only_fields = ['created_at', 'updated_at', 'completed_date']
    
    def get_task_count(self, obj):
        """Get the number of tasks in this project."""
        return obj.get_task_count()
    
    def get_progress_percentage(self, obj):
        """Get project progress percentage."""
        return obj.get_progress_percentage()
    
    def get_is_overdue(self, obj):
        """Check if project is overdue."""
        return obj.is_overdue()


class ProjectDetailSerializer(serializers.ModelSerializer):
    """
    Detailed serializer for Project model.
    """
    manager = UserListSerializer(read_only=True)
    manager_id = serializers.PrimaryKeyRelatedField(
        queryset=User.objects.all(),
        source='manager',
        write_only=True,
        help_text="Project manager ID"
    )
    team = TeamSerializer(read_only=True)
    team_id = serializers.PrimaryKeyRelatedField(
        queryset=Team.objects.all(),
        source='team',
        write_only=True,
        help_text="Team ID"
    )
    created_by = UserListSerializer(read_only=True)
    task_count = serializers.SerializerMethodField()
    completed_task_count = serializers.SerializerMethodField()
    progress_percentage = serializers.SerializerMethodField()
    is_overdue = serializers.SerializerMethodField()
    
    class Meta:
        model = Project
        fields = [
            'id', 'name', 'description', 'team', 'team_id', 'manager', 'manager_id',
            'created_by', 'status', 'priority', 'start_date', 'end_date',
            'completed_date', 'is_active', 'budget', 'task_count', 'completed_task_count',
            'progress_percentage', 'is_overdue', 'created_at', 'updated_at'
        ]
        read_only_fields = ['created_at', 'updated_at', 'completed_date']
    
    def get_task_count(self, obj):
        """Get the number of tasks in this project."""
        return obj.get_task_count()
    
    def get_completed_task_count(self, obj):
        """Get the number of completed tasks in this project."""
        return obj.get_completed_task_count()
    
    def get_progress_percentage(self, obj):
        """Get project progress percentage."""
        return obj.get_progress_percentage()
    
    def get_is_overdue(self, obj):
        """Check if project is overdue."""
        return obj.is_overdue()
    
    def validate_manager_id(self, value):
        """Validate that manager has appropriate role."""
        if not (value.has_role('manager') or value.has_role('admin')):
            raise serializers.ValidationError(
                "Project manager must have manager or admin role."
            )
        return value
    
    def validate_team_id(self, value):
        """Validate that team is active."""
        if not value.is_active:
            raise serializers.ValidationError(
                "Cannot assign project to inactive team."
            )
        return value


class ProjectCreateSerializer(serializers.ModelSerializer):
    """
    Serializer for creating projects.
    """
    manager_id = serializers.PrimaryKeyRelatedField(
        queryset=User.objects.all(),
        source='manager',
        help_text="Project manager ID"
    )
    team_id = serializers.PrimaryKeyRelatedField(
        queryset=Team.objects.all(),
        source='team',
        help_text="Team ID"
    )
    
    class Meta:
        model = Project
        fields = [
            'name', 'description', 'team_id', 'manager_id', 'status', 'priority',
            'start_date', 'end_date', 'budget'
        ]
    
    def validate_manager_id(self, value):
        """Validate that manager has appropriate role."""
        if not (value.has_role('manager') or value.has_role('admin')):
            raise serializers.ValidationError(
                "Project manager must have manager or admin role."
            )
        return value
    
    def validate_team_id(self, value):
        """Validate that team is active."""
        if not value.is_active:
            raise serializers.ValidationError(
                "Cannot assign project to inactive team."
            )
        return value
    
    def validate(self, attrs):
        """Validate project dates."""
        start_date = attrs.get('start_date')
        end_date = attrs.get('end_date')
        
        if start_date and end_date and start_date > end_date:
            raise serializers.ValidationError(
                "End date must be after start date."
            )
        
        return attrs
    
    def create(self, validated_data):
        """Create project with current user as creator."""
        validated_data['created_by'] = self.context['request'].user
        return super().create(validated_data)


class ProjectStatusUpdateSerializer(serializers.ModelSerializer):
    """
    Serializer for updating project status.
    """
    class Meta:
        model = Project
        fields = ['status']
    
    def validate_status(self, value):
        """Validate status transition."""
        instance = self.instance
        if instance:
            # Check if status transition is valid
            valid_transitions = {
                'planning': ['active', 'cancelled'],
                'active': ['on_hold', 'completed', 'cancelled'],
                'on_hold': ['active', 'cancelled'],
                'completed': [],  # Cannot change from completed
                'cancelled': [],  # Cannot change from cancelled
            }
            
            current_status = instance.status
            if value not in valid_transitions.get(current_status, []):
                raise serializers.ValidationError(
                    f"Cannot transition from {current_status} to {value}."
                )
        
        return value
    
    def update(self, instance, validated_data):
        """Update project status and set completion date if needed."""
        new_status = validated_data.get('status')
        
        if new_status == 'completed' and instance.status != 'completed':
            from django.utils import timezone
            validated_data['completed_date'] = timezone.now().date()
        
        return super().update(instance, validated_data) 