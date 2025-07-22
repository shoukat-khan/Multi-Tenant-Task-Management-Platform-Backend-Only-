from rest_framework import generics, status, permissions
from rest_framework.response import Response
from rest_framework.views import APIView
from django.shortcuts import get_object_or_404
from django.db.models import Q
from drf_spectacular.utils import extend_schema, OpenApiResponse
from Services.users.permissions import IsManagerUser, IsAdminUser, IsOwnerOrManagerOrAdmin
from .models import Team, TeamMembership
from .serializers import (
    TeamSerializer, TeamDetailSerializer, TeamCreateSerializer,
    TeamMembershipSerializer, TeamMembershipCreateSerializer
)


class TeamListView(generics.ListCreateAPIView):
    """
    List all teams or create a new team.
    Only managers and admins can create teams.
    """
    serializer_class = TeamSerializer
    permission_classes = [permissions.IsAuthenticated]
    
    def get_queryset(self):
        """Filter teams based on user role and permissions."""
        user = self.request.user
        
        # Admin can see all teams
        if user.has_role('admin'):
            return Team.objects.all()
        
        # Manager can see teams they manage and teams they're members of
        if user.has_role('manager'):
            return Team.objects.filter(
                Q(manager=user) | Q(members=user)
            ).distinct()
        
        # Employee can only see teams they're members of
        return Team.objects.filter(members=user)
    
    def get_serializer_class(self):
        """Use different serializer for creation."""
        if self.request.method == 'POST':
            return TeamCreateSerializer
        return TeamSerializer
    
    def get_permissions(self):
        """Set permissions based on request method."""
        if self.request.method == 'POST':
            return [IsManagerUser()]
        return [permissions.IsAuthenticated()]
    
    @extend_schema(
        summary="List Teams",
        description="Get list of teams based on user permissions",
        responses={200: TeamSerializer(many=True)}
    )
    def get(self, request, *args, **kwargs):
        return super().get(request, *args, **kwargs)
    
    @extend_schema(
        summary="Create Team",
        description="Create a new team (Manager/Admin only)",
        responses={
            201: TeamDetailSerializer,
            400: OpenApiResponse(description="Invalid input data"),
        }
    )
    def post(self, request, *args, **kwargs):
        return super().post(request, *args, **kwargs)


class TeamDetailView(generics.RetrieveUpdateDestroyAPIView):
    """
    Retrieve, update or delete a team.
    Only team managers and admins can modify teams.
    """
    queryset = Team.objects.all()
    serializer_class = TeamDetailSerializer
    permission_classes = [IsOwnerOrManagerOrAdmin]
    
    def get_serializer_class(self):
        """Use different serializer for updates."""
        if self.request.method in ['PUT', 'PATCH']:
            return TeamDetailSerializer
        return TeamDetailSerializer
    
    def get_permissions(self):
        """Set permissions based on request method."""
        if self.request.method in ['PUT', 'PATCH', 'DELETE']:
            return [IsManagerUser()]
        return [permissions.IsAuthenticated()]
    
    @extend_schema(
        summary="Get Team Details",
        description="Retrieve detailed team information",
        responses={200: TeamDetailSerializer}
    )
    def get(self, request, *args, **kwargs):
        return super().get(request, *args, **kwargs)
    
    @extend_schema(
        summary="Update Team",
        description="Update team information (Manager/Admin only)",
        responses={200: TeamDetailSerializer}
    )
    def put(self, request, *args, **kwargs):
        return super().put(request, *args, **kwargs)
    
    def patch(self, request, *args, **kwargs):
        return super().patch(request, *args, **kwargs)
    
    @extend_schema(
        summary="Delete Team",
        description="Delete team (Admin only)",
        responses={204: OpenApiResponse(description="Team deleted")}
    )
    def delete(self, request, *args, **kwargs):
        # Only admins can delete teams
        if not request.user.has_role('admin'):
            return Response({
                'error': 'Only admins can delete teams'
            }, status=status.HTTP_403_FORBIDDEN)
        return super().delete(request, *args, **kwargs)


class TeamMembersView(generics.ListCreateAPIView):
    """
    List team members or add new members.
    Only team managers and admins can add members.
    """
    serializer_class = TeamMembershipSerializer
    permission_classes = [permissions.IsAuthenticated]
    
    def get_queryset(self):
        """Get team members for the specified team."""
        team_id = self.kwargs['team_id']
        team = get_object_or_404(Team, id=team_id)
        
        # Check if user can access this team
        if not (team.is_manager(self.request.user) or 
                team.is_member(self.request.user) or 
                self.request.user.has_role('admin')):
            return TeamMembership.objects.none()
        
        return team.memberships.all()
    
    def get_serializer_class(self):
        """Use different serializer for creation."""
        if self.request.method == 'POST':
            return TeamMembershipCreateSerializer
        return TeamMembershipSerializer
    
    def get_permissions(self):
        """Set permissions based on request method."""
        if self.request.method == 'POST':
            return [IsManagerUser()]
        return [permissions.IsAuthenticated()]
    
    def get_serializer_context(self):
        """Add team to serializer context."""
        context = super().get_serializer_context()
        context['team'] = get_object_or_404(Team, id=self.kwargs['team_id'])
        return context
    
    @extend_schema(
        summary="List Team Members",
        description="Get list of team members",
        responses={200: TeamMembershipSerializer(many=True)}
    )
    def get(self, request, *args, **kwargs):
        return super().get(request, *args, **kwargs)
    
    @extend_schema(
        summary="Add Team Member",
        description="Add a new member to the team (Manager/Admin only)",
        responses={
            201: TeamMembershipSerializer,
            400: OpenApiResponse(description="Invalid input data"),
        }
    )
    def post(self, request, *args, **kwargs):
        return super().post(request, *args, **kwargs)


class TeamMemberDetailView(generics.RetrieveUpdateDestroyAPIView):
    """
    Retrieve, update or remove a team member.
    Only team managers and admins can modify memberships.
    """
    serializer_class = TeamMembershipSerializer
    permission_classes = [IsManagerUser]
    
    def get_queryset(self):
        """Get team membership for the specified team and member."""
        team_id = self.kwargs['team_id']
        member_id = self.kwargs['member_id']
        team = get_object_or_404(Team, id=team_id)
        
        # Check if user can manage this team
        if not (team.is_manager(self.request.user) or self.request.user.has_role('admin')):
            return TeamMembership.objects.none()
        
        return team.memberships.filter(member_id=member_id)
    
    @extend_schema(
        summary="Get Team Member",
        description="Get team member details",
        responses={200: TeamMembershipSerializer}
    )
    def get(self, request, *args, **kwargs):
        return super().get(request, *args, **kwargs)
    
    @extend_schema(
        summary="Update Team Member",
        description="Update team member role (Manager/Admin only)",
        responses={200: TeamMembershipSerializer}
    )
    def put(self, request, *args, **kwargs):
        return super().put(request, *args, **kwargs)
    
    def patch(self, request, *args, **kwargs):
        return super().patch(request, *args, **kwargs)
    
    @extend_schema(
        summary="Remove Team Member",
        description="Remove member from team (Manager/Admin only)",
        responses={204: OpenApiResponse(description="Member removed")}
    )
    def delete(self, request, *args, **kwargs):
        return super().delete(request, *args, **kwargs)


class MyTeamsView(generics.ListAPIView):
    """
    List teams that the current user is a member of.
    """
    serializer_class = TeamSerializer
    permission_classes = [permissions.IsAuthenticated]
    
    def get_queryset(self):
        """Get teams where user is a member."""
        return Team.objects.filter(members=self.request.user)
    
    @extend_schema(
        summary="My Teams",
        description="Get list of teams where current user is a member",
        responses={200: TeamSerializer(many=True)}
    )
    def get(self, request, *args, **kwargs):
        return super().get(request, *args, **kwargs)


class ManagedTeamsView(generics.ListAPIView):
    """
    List teams that the current user manages.
    Only managers and admins can access this.
    """
    serializer_class = TeamSerializer
    permission_classes = [IsManagerUser]
    
    def get_queryset(self):
        """Get teams where user is the manager."""
        return Team.objects.filter(manager=self.request.user)
    
    @extend_schema(
        summary="Managed Teams",
        description="Get list of teams managed by current user (Manager/Admin only)",
        responses={200: TeamSerializer(many=True)}
    )
    def get(self, request, *args, **kwargs):
        return super().get(request, *args, **kwargs)
