from rest_framework import generics, status, permissions, filters
from rest_framework.response import Response
from rest_framework.views import APIView
from django.shortcuts import get_object_or_404
from django.db.models import Q
from django_filters.rest_framework import DjangoFilterBackend
from drf_spectacular.utils import extend_schema, OpenApiResponse
from Services.users.permissions import IsManagerUser
from Services.teams.models import Team
from .models import Project
from .filters import ProjectFilter
from .serializers import (
    ProjectSerializer, ProjectDetailSerializer, ProjectCreateSerializer,
    ProjectStatusUpdateSerializer
)


class ProjectListView(generics.ListCreateAPIView):
    """
    List all projects or create a new project.
    Only managers and admins can create projects.
    Supports filtering by team, owner, status and search.
    """
    serializer_class = ProjectSerializer
    permission_classes = [permissions.IsAuthenticated]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_class = ProjectFilter
    search_fields = ['name', 'description', 'team__name', 'manager__email']
    ordering_fields = ['created_at', 'updated_at', 'start_date', 'end_date', 'priority', 'status']
    ordering = ['-created_at']
    
    def get_queryset(self):
        """Filter projects based on user role and team membership permissions."""
        user = self.request.user
        
        # Admin can see all projects
        if user.has_role('admin'):
            return Project.objects.select_related('team', 'manager', 'created_by').all()
        
        # Manager can see projects they manage and projects of teams they manage
        if user.has_role('manager'):
            return Project.objects.select_related('team', 'manager', 'created_by').filter(
                Q(manager=user) | Q(team__manager=user) | Q(team__members=user)
            ).distinct()
        
        # Employee can only see projects of teams they're members of
        return Project.objects.select_related('team', 'manager', 'created_by').filter(
            team__members=user
        )
    
    def get_serializer_class(self):
        """Use different serializer for creation."""
        if self.request.method == 'POST':
            return ProjectCreateSerializer
        return ProjectSerializer
    
    def get_permissions(self):
        """Set permissions based on request method."""
        if self.request.method == 'POST':
            return [IsManagerUser()]
        return [permissions.IsAuthenticated()]
    
    @extend_schema(
        summary="List Projects",
        description="Get list of projects based on user permissions. Supports filtering by team, owner, status and search.",
        responses={200: ProjectSerializer(many=True)}
    )
    def get(self, request, *args, **kwargs):
        return super().get(request, *args, **kwargs)
    
    @extend_schema(
        summary="Create Project",
        description="Create a new project (Manager/Admin only)",
        responses={
            201: ProjectDetailSerializer,
            400: OpenApiResponse(description="Invalid input data"),
            403: OpenApiResponse(description="Permission denied"),
        }
    )
    def post(self, request, *args, **kwargs):
        """
        Create a new project with proper team validation.
        """
        # Check permissions first
        if not (request.user.has_role('manager') or request.user.has_role('admin')):
            return Response({
                'error': 'Only managers and admins can create projects'
            }, status=status.HTTP_403_FORBIDDEN)
        
        serializer = self.get_serializer(data=request.data)
        if serializer.is_valid():
            team = serializer.validated_data.get('team')
            
            # Ensure the user can create projects for this team (must be manager or admin)
            if not (team.is_manager(request.user) or request.user.has_role('admin')):
                return Response({
                    'error': "You don't have permission to create projects for this team."
                }, status=status.HTTP_403_FORBIDDEN)
            
            # Set created_by and default manager if not provided
            manager = serializer.validated_data.get('manager', request.user)
            project = serializer.save(created_by=request.user, manager=manager)
            
            # Return detailed project information
            response_serializer = ProjectDetailSerializer(project)
            return Response(response_serializer.data, status=status.HTTP_201_CREATED)
        
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class ProjectDetailView(generics.RetrieveUpdateDestroyAPIView):
    """
    Retrieve, update or delete a project.
    Only project managers, team managers, and admins can modify projects.
    """
    queryset = Project.objects.all()
    serializer_class = ProjectDetailSerializer
    permission_classes = [permissions.IsAuthenticated]
    
    def get_serializer_class(self):
        """Use different serializer for updates."""
        if self.request.method in ['PUT', 'PATCH']:
            return ProjectDetailSerializer
        return ProjectDetailSerializer
    
    def get_permissions(self):
        """Set permissions based on request method."""
        if self.request.method in ['PUT', 'PATCH', 'DELETE']:
            return [IsManagerUser()]
        return [permissions.IsAuthenticated()]
    
    def check_object_permissions(self, request, obj):
        """Check if user can access this project."""
        super().check_object_permissions(request, obj)
        
        # Check if user can access this project
        if not obj.can_be_accessed_by(request.user):
            self.permission_denied(request)
    
    @extend_schema(
        summary="Get Project Details",
        description="Retrieve detailed project information",
        responses={200: ProjectDetailSerializer}
    )
    def get(self, request, *args, **kwargs):
        return super().get(request, *args, **kwargs)
    
    @extend_schema(
        summary="Update Project",
        description="Update project information (Manager/Admin only)",
        responses={200: ProjectDetailSerializer}
    )
    def put(self, request, *args, **kwargs):
        return super().put(request, *args, **kwargs)
    
    def patch(self, request, *args, **kwargs):
        return super().patch(request, *args, **kwargs)
    
    @extend_schema(
        summary="Delete Project",
        description="Delete project (Admin only)",
        responses={204: OpenApiResponse(description="Project deleted")}
    )
    def delete(self, request, *args, **kwargs):
        # Only admins can delete projects
        if not request.user.has_role('admin'):
            return Response({
                'error': 'Only admins can delete projects'
            }, status=status.HTTP_403_FORBIDDEN)
        return super().delete(request, *args, **kwargs)


class ProjectStatusUpdateView(APIView):
    """
    Update project status.
    Only project managers, team managers, and admins can update status.
    """
    permission_classes = [IsManagerUser]
    
    @extend_schema(
        summary="Update Project Status",
        description="Update project status (Manager/Admin only)",
        request=ProjectStatusUpdateSerializer,
        responses={
            200: ProjectSerializer,
            400: OpenApiResponse(description="Invalid status transition"),
        }
    )
    def patch(self, request, pk):
        project = get_object_or_404(Project, pk=pk)
        
        # Check if user can manage this project
        if not project.can_be_managed_by(request.user):
            return Response({
                'error': 'You do not have permission to manage this project'
            }, status=status.HTTP_403_FORBIDDEN)
        
        serializer = ProjectStatusUpdateSerializer(project, data=request.data, partial=True)
        
        if serializer.is_valid():
            serializer.save()
            return Response(ProjectSerializer(project).data)
        
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class TeamProjectsView(generics.ListAPIView):
    """
    List projects for a specific team.
    Only team members can see team projects.
    """
    serializer_class = ProjectSerializer
    permission_classes = [permissions.IsAuthenticated]
    
    def get_queryset(self):
        """Get projects for the specified team."""
        team_id = self.kwargs['team_id']
        team = get_object_or_404(Team, id=team_id)
        
        # Check if user can access this team's projects
        if not (team.is_manager(self.request.user) or 
                team.is_member(self.request.user) or 
                self.request.user.has_role('admin')):
            return Project.objects.none()
        
        return team.projects.all()


class MyProjectsView(generics.ListAPIView):
    """
    List projects where the current user is a member of the team.
    """
    serializer_class = ProjectSerializer
    permission_classes = [permissions.IsAuthenticated]
    
    def get_queryset(self):
        """Get projects where user is a team member."""
        return Project.objects.filter(team__members=self.request.user)
    
    @extend_schema(
        summary="My Projects",
        description="Get list of projects where current user is a team member",
        responses={200: ProjectSerializer(many=True)}
    )
    def get(self, request, *args, **kwargs):
        return super().get(request, *args, **kwargs)


class ManagedProjectsView(generics.ListAPIView):
    """
    List projects that the current user manages.
    Only managers and admins can access this.
    """
    serializer_class = ProjectSerializer
    permission_classes = [IsManagerUser]
    
    def get_queryset(self):
        """Get projects where user is the manager."""
        return Project.objects.filter(manager=self.request.user)
    
    @extend_schema(
        summary="Managed Projects",
        description="Get list of projects managed by current user (Manager/Admin only)",
        responses={200: ProjectSerializer(many=True)}
    )
    def get(self, request, *args, **kwargs):
        return super().get(request, *args, **kwargs)


class ProjectStatisticsView(APIView):
    """
    Get project statistics.
    Only project managers, team managers, and admins can access this.
    """
    permission_classes = [permissions.IsAuthenticated]
    
    @extend_schema(
        summary="Project Statistics",
        description="Get project statistics and metrics",
        responses={200: OpenApiResponse(description="Project statistics")}
    )
    def get(self, request, pk):
        project = get_object_or_404(Project, pk=pk)
        
        # Check if user can access this project
        if not project.can_be_accessed_by(request.user):
            return Response({
                'error': 'You do not have permission to access this project'
            }, status=status.HTTP_403_FORBIDDEN)
        
        # Calculate statistics
        total_tasks = project.get_task_count()
        completed_tasks = project.get_completed_task_count()
        progress_percentage = project.get_progress_percentage()
        is_overdue = project.is_overdue()
        
        # Task status breakdown
        task_status_breakdown = {}
        for status_choice in project.tasks.values_list('status', flat=True).distinct():
            count = project.tasks.filter(status=status_choice).count()
            task_status_breakdown[status_choice] = count
        
        return Response({
            'project': {
                'id': project.id,
                'name': project.name,
                'status': project.status,
                'progress_percentage': progress_percentage,
                'is_overdue': is_overdue,
            },
            'statistics': {
                'total_tasks': total_tasks,
                'completed_tasks': completed_tasks,
                'pending_tasks': total_tasks - completed_tasks,
                'task_status_breakdown': task_status_breakdown,
            }
        })
