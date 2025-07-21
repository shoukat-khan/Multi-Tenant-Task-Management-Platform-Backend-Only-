from rest_framework import serializers
from services.users.models import User
from services.users.serializers import UserListSerializer
from .models import Team, TeamMembership


class TeamMembershipSerializer(serializers.ModelSerializer):
    """
    Serializer for team membership with user details.
    """
    member = UserListSerializer(read_only=True)
    member_id = serializers.PrimaryKeyRelatedField(
        queryset=User.objects.all(),
        source='member',
        write_only=True,
        help_text="User ID to add to team"
    )
    
    class Meta:
        model = TeamMembership
        fields = [
            'id', 'member', 'member_id', 'role', 'joined_at', 'is_active'
        ]
        read_only_fields = ['joined_at']


class TeamSerializer(serializers.ModelSerializer):
    """
    Basic serializer for Team model.
    """
    manager_name = serializers.CharField(source='manager.get_full_name', read_only=True)
    member_count = serializers.SerializerMethodField()
    
    class Meta:
        model = Team
        fields = [
            'id', 'name', 'description', 'manager', 'manager_name',
            'is_active', 'max_members', 'member_count',
            'created_at', 'updated_at'
        ]
        read_only_fields = ['created_at', 'updated_at']
    
    def get_member_count(self, obj):
        """Get the number of team members."""
        return obj.get_member_count()


class TeamDetailSerializer(serializers.ModelSerializer):
    """
    Detailed serializer for Team model with members.
    """
    manager = UserListSerializer(read_only=True)
    manager_id = serializers.PrimaryKeyRelatedField(
        queryset=User.objects.all(),
        source='manager',
        write_only=True,
        help_text="Team manager ID"
    )
    members = TeamMembershipSerializer(many=True, read_only=True)
    member_count = serializers.SerializerMethodField()
    can_add_member = serializers.SerializerMethodField()
    
    class Meta:
        model = Team
        fields = [
            'id', 'name', 'description', 'manager', 'manager_id',
            'members', 'is_active', 'max_members', 'member_count',
            'can_add_member', 'created_at', 'updated_at'
        ]
        read_only_fields = ['created_at', 'updated_at']
    
    def get_member_count(self, obj):
        """Get the number of team members."""
        return obj.get_member_count()
    
    def get_can_add_member(self, obj):
        """Check if team can accept more members."""
        return obj.can_add_member()
    
    def validate_manager(self, value):
        """Validate that manager has appropriate role."""
        if not (value.has_role('manager') or value.has_role('admin')):
            raise serializers.ValidationError(
                "Team manager must have manager or admin role."
            )
        return value


class TeamCreateSerializer(serializers.ModelSerializer):
    """
    Serializer for creating teams.
    """
    manager_id = serializers.PrimaryKeyRelatedField(
        queryset=User.objects.all(),
        source='manager',
        help_text="Team manager ID"
    )
    
    class Meta:
        model = Team
        fields = [
            'name', 'description', 'manager_id', 'max_members'
        ]
    
    def validate_manager_id(self, value):
        """Validate that manager has appropriate role."""
        if not (value.has_role('manager') or value.has_role('admin')):
            raise serializers.ValidationError(
                "Team manager must have manager or admin role."
            )
        return value
    
    def create(self, validated_data):
        """Create team and add manager as first member."""
        team = super().create(validated_data)
        
        # Add manager as first member
        TeamMembership.objects.create(
            team=team,
            member=team.manager,
            role='lead'
        )
        
        return team


class TeamMembershipCreateSerializer(serializers.ModelSerializer):
    """
    Serializer for adding members to teams.
    """
    member_id = serializers.PrimaryKeyRelatedField(
        queryset=User.objects.all(),
        source='member',
        help_text="User ID to add to team"
    )
    
    class Meta:
        model = TeamMembership
        fields = ['member_id', 'role']
    
    def validate(self, attrs):
        """Validate team membership."""
        team = self.context['team']
        member = attrs['member']
        
        # Check if user is already a member
        if team.is_member(member):
            raise serializers.ValidationError(
                "User is already a member of this team."
            )
        
        # Check if team can accept more members
        if not team.can_add_member():
            raise serializers.ValidationError(
                "Team has reached maximum member limit."
            )
        
        return attrs
    
    def create(self, validated_data):
        """Create team membership."""
        team = self.context['team']
        return TeamMembership.objects.create(
            team=team,
            **validated_data
        ) 