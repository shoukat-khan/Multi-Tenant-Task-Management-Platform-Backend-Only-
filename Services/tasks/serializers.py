from rest_framework import serializers
from Services.users.models import User
from Services.teams.models import Team
from Services.projects.models import Project
from Services.users.serializers import UserListSerializer
from Services.teams.serializers import TeamSerializer
from Services.projects.serializers import ProjectSerializer
from .models import Task, TaskComment, TaskAttachment


class TaskCommentSerializer(serializers.ModelSerializer):
    """
    Serializer for task comments.
    """
    author = UserListSerializer(read_only=True)
    
    class Meta:
        model = TaskComment
        fields = [
            'id', 'author', 'content', 'created_at', 'updated_at'
        ]
        read_only_fields = ['created_at', 'updated_at']


class TaskAttachmentSerializer(serializers.ModelSerializer):
    """
    Serializer for task attachments.
    """
    uploaded_by = UserListSerializer(read_only=True)
    
    class Meta:
        model = TaskAttachment
        fields = [
            'id', 'uploaded_by', 'file', 'filename', 'file_size', 'uploaded_at'
        ]
        read_only_fields = ['uploaded_at']


class TaskSerializer(serializers.ModelSerializer):
    """
    Basic serializer for Task model.
    """
    assigned_to_name = serializers.CharField(source='assigned_to.get_full_name', read_only=True)
    created_by_name = serializers.CharField(source='created_by.get_full_name', read_only=True)
    project_name = serializers.CharField(source='project.name', read_only=True)
    team_name = serializers.CharField(source='team.name', read_only=True)
    is_overdue = serializers.SerializerMethodField()
    comment_count = serializers.SerializerMethodField()
    
    class Meta:
        model = Task
        fields = [
            'id', 'title', 'description', 'project', 'project_name', 'team', 'team_name',
            'assigned_to', 'assigned_to_name', 'created_by', 'created_by_name', 'status',
            'priority', 'due_date', 'started_at', 'completed_at', 'estimated_hours',
            'actual_hours', 'is_active', 'is_public', 'is_overdue', 'comment_count',
            'created_at', 'updated_at'
        ]
        read_only_fields = ['created_at', 'updated_at', 'started_at', 'completed_at']
    
    def get_is_overdue(self, obj):
        """Check if task is overdue."""
        return obj.is_overdue()
    
    def get_comment_count(self, obj):
        """Get the number of comments on this task."""
        return obj.comments.count()


class TaskDetailSerializer(serializers.ModelSerializer):
    """
    Detailed serializer for Task model with comments and attachments.
    """
    assigned_to = UserListSerializer(read_only=True)
    assigned_to_id = serializers.PrimaryKeyRelatedField(
        queryset=User.objects.all(),
        source='assigned_to',
        write_only=True,
        required=False,
        allow_null=True,
        help_text="User ID to assign task to"
    )
    created_by = UserListSerializer(read_only=True)
    project = ProjectSerializer(read_only=True)
    project_id = serializers.PrimaryKeyRelatedField(
        queryset=Project.objects.all(),
        source='project',
        write_only=True,
        help_text="Project ID"
    )
    team = TeamSerializer(read_only=True)
    team_id = serializers.PrimaryKeyRelatedField(
        queryset=Team.objects.all(),
        source='team',
        write_only=True,
        help_text="Team ID"
    )
    comments = TaskCommentSerializer(many=True, read_only=True)
    attachments = TaskAttachmentSerializer(many=True, read_only=True)
    is_overdue = serializers.SerializerMethodField()
    comment_count = serializers.SerializerMethodField()
    attachment_count = serializers.SerializerMethodField()
    
    class Meta:
        model = Task
        fields = [
            'id', 'title', 'description', 'project', 'project_id', 'team', 'team_id',
            'assigned_to', 'assigned_to_id', 'created_by', 'status', 'priority',
            'due_date', 'started_at', 'completed_at', 'estimated_hours', 'actual_hours',
            'is_active', 'is_public', 'comments', 'attachments', 'is_overdue',
            'comment_count', 'attachment_count', 'created_at', 'updated_at'
        ]
        read_only_fields = ['created_at', 'updated_at', 'started_at', 'completed_at']
    
    def get_is_overdue(self, obj):
        """Check if task is overdue."""
        return obj.is_overdue()
    
    def get_comment_count(self, obj):
        """Get the number of comments on this task."""
        return obj.comments.count()
    
    def get_attachment_count(self, obj):
        """Get the number of attachments on this task."""
        return obj.attachments.count()
    
    def validate_assigned_to_id(self, value):
        """
        Validate that assigned user is a team member.
        Also restrict employees from assigning tasks to others.
        """
        request_user = self.context['request'].user
        
        # Employees cannot assign tasks to others (only managers and admins can)
        if request_user.has_role('employee') and value:
            current_assignee = self.instance.assigned_to if self.instance else None
            if value != request_user and value != current_assignee:
                raise serializers.ValidationError(
                    "Employees cannot assign tasks to other users."
                )
        
        if value:
            # Get the team from context or instance
            team = None
            if self.instance:
                team = self.instance.team
            elif 'team_id' in self.initial_data:
                team = Team.objects.get(id=self.initial_data['team_id'])
            
            if team and not team.is_member(value):
                raise serializers.ValidationError(
                    "Assigned user must be a member of the task's team."
                )
        return value
    
    def validate_team_id(self, value):
        """Validate that team is active."""
        if not value.is_active:
            raise serializers.ValidationError(
                "Cannot assign task to inactive team."
            )
        return value


class TaskCreateSerializer(serializers.ModelSerializer):
    """
    Serializer for creating tasks.
    """
    assigned_to_id = serializers.PrimaryKeyRelatedField(
        queryset=User.objects.all(),
        source='assigned_to',
        required=False,
        allow_null=True,
        help_text="User ID to assign task to"
    )
    project_id = serializers.PrimaryKeyRelatedField(
        queryset=Project.objects.all(),
        source='project',
        help_text="Project ID"
    )
    team_id = serializers.PrimaryKeyRelatedField(
        queryset=Team.objects.all(),
        source='team',
        help_text="Team ID"
    )
    
    class Meta:
        model = Task
        fields = [
            'title', 'description', 'project_id', 'team_id', 'assigned_to_id',
            'status', 'priority', 'due_date', 'estimated_hours', 'is_public'
        ]
    
    def validate_assigned_to_id(self, value):
        """
        Validate that assigned user is a team member.
        Also restrict employees from assigning tasks to others.
        """
        request_user = self.context['request'].user
        
        # Employees cannot assign tasks to others (only managers and admins can)
        if request_user.has_role('employee') and value and value != request_user:
            raise serializers.ValidationError(
                "Employees cannot assign tasks to other users."
            )
        
        if value:
            # Get the team from context
            team_id = self.initial_data.get('team_id')
            if team_id:
                try:
                    team = Team.objects.get(id=team_id)
                    if not team.is_member(value):
                        raise serializers.ValidationError(
                            "Assigned user must be a member of the task's team."
                        )
                except Team.DoesNotExist:
                    pass
        return value
    
    def validate_team_id(self, value):
        """Validate that team is active."""
        if not value.is_active:
            raise serializers.ValidationError(
                "Cannot assign task to inactive team."
            )
        return value
    
    def validate_project_id(self, value):
        """Validate that project is active."""
        if not value.is_active:
            raise serializers.ValidationError(
                "Cannot assign task to inactive project."
            )
        return value
    
    def create(self, validated_data):
        """Create task with current user as creator."""
        validated_data['created_by'] = self.context['request'].user
        return super().create(validated_data)


class TaskStatusUpdateSerializer(serializers.ModelSerializer):
    """
    Serializer for updating task status.
    """
    class Meta:
        model = Task
        fields = ['status']
    
    def validate_status(self, value):
        """Validate status transition."""
        instance = self.instance
        if instance:
            # Check if status transition is valid
            valid_transitions = {
                'todo': ['in_progress', 'cancelled'],
                'in_progress': ['review', 'completed', 'cancelled'],
                'review': ['in_progress', 'completed', 'cancelled'],
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
        """Update task status and set timestamps if needed."""
        new_status = validated_data.get('status')
        
        if new_status == 'in_progress' and instance.status != 'in_progress':
            from django.utils import timezone
            validated_data['started_at'] = timezone.now()
        
        if new_status == 'completed' and instance.status != 'completed':
            from django.utils import timezone
            validated_data['completed_at'] = timezone.now()
        
        return super().update(instance, validated_data)


class TaskCommentCreateSerializer(serializers.ModelSerializer):
    """
    Serializer for creating task comments.
    """
    class Meta:
        model = TaskComment
        fields = ['content']
    
    def create(self, validated_data):
        """Create comment with current user as author."""
        validated_data['author'] = self.context['request'].user
        validated_data['task'] = self.context['task']
        return super().create(validated_data)


class TaskAttachmentCreateSerializer(serializers.ModelSerializer):
    """
    Serializer for creating task attachments.
    """
    class Meta:
        model = TaskAttachment
        fields = ['file']
    
    def validate_file(self, value):
        """Validate uploaded file."""
        # Check file size (max 10MB)
        if value.size > 10 * 1024 * 1024:
            raise serializers.ValidationError(
                "File size must be less than 10MB."
            )
        
        # Check file type
        allowed_types = [
            'image/jpeg', 'image/png', 'image/gif',
            'application/pdf', 'text/plain',
            'application/msword', 'application/vnd.openxmlformats-officedocument.wordprocessingml.document',
            'application/vnd.ms-excel', 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
        ]
        
        if hasattr(value, 'content_type') and value.content_type not in allowed_types:
            raise serializers.ValidationError(
                "File type not allowed. Please upload images, PDFs, text files, or Office documents."
            )
        
        return value
    
    def create(self, validated_data):
        """Create attachment with current user as uploader."""
        file_obj = validated_data['file']
        validated_data['uploaded_by'] = self.context['request'].user
        validated_data['task'] = self.context['task']
        validated_data['filename'] = file_obj.name
        validated_data['file_size'] = file_obj.size
        return super().create(validated_data) 