from rest_framework import generics, status, permissions, filters
from rest_framework.response import Response
from rest_framework.views import APIView
from django.shortcuts import get_object_or_404
from django.db.models import Q
from django_filters.rest_framework import DjangoFilterBackend
from drf_spectacular.utils import extend_schema, OpenApiResponse
from Services.users.permissions import IsManagerUser, IsAdminUser, IsOwnerOrManagerOrAdmin
from Services.teams.models import Team
from Services.projects.models import Project
from .models import Task, TaskComment, TaskAttachment
from .filters import TaskFilter
from .serializers import (
    TaskSerializer, TaskDetailSerializer, TaskCreateSerializer,
    TaskStatusUpdateSerializer, TaskCommentSerializer, TaskCommentCreateSerializer,
    TaskAttachmentSerializer, TaskAttachmentCreateSerializer
)


class TaskListView(generics.ListCreateAPIView):
    """
    List all tasks or create a new task.
    Only managers and admins can create tasks.
    Supports filtering by status, due date range, user, and search.
    """
    serializer_class = TaskSerializer
    permission_classes = [permissions.IsAuthenticated]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_class = TaskFilter
    search_fields = ['title', 'description', 'project__name', 'team__name']
    ordering_fields = ['created_at', 'updated_at', 'due_date', 'priority', 'status']
    ordering = ['-created_at']
    
    def get_queryset(self):
        """Filter tasks based on user role and permissions with team restrictions."""
        user = self.request.user
        
        # Admin can see all tasks
        if user.has_role('admin'):
            return Task.objects.select_related('project', 'team', 'assigned_to', 'created_by').all()
        
        # Manager can see tasks they manage and tasks of teams they manage
        if user.has_role('manager'):
            return Task.objects.select_related('project', 'team', 'assigned_to', 'created_by').filter(
                Q(created_by=user) | Q(assigned_to=user) | 
                Q(team__manager=user) | Q(project__manager=user) |
                Q(team__members=user)  # Only team members can access tasks
            ).distinct()
        
        # Employee can only see tasks they're assigned to or created, but only if they're team members
        return Task.objects.select_related('project', 'team', 'assigned_to', 'created_by').filter(
            Q(assigned_to=user) | Q(created_by=user),
            Q(team__members=user)  # Must be team member to access
        ).distinct()
    
    def get_serializer_class(self):
        """Use different serializer for creation."""
        if self.request.method == 'POST':
            return TaskCreateSerializer
        return TaskSerializer
    
    def get_permissions(self):
        """Set permissions based on request method with employee task assignment restriction."""
        if self.request.method == 'POST':
            # Only managers and admins can create tasks
            return [IsManagerUser()]
        return [permissions.IsAuthenticated()]
    
    def perform_create(self, serializer):
        """
        Override perform_create to ensure proper task creation with team validation.
        """
        user = self.request.user
        project = serializer.validated_data.get('project')
        
        # Ensure the user can create tasks for this project
        if not project.can_be_managed_by(user):
            from rest_framework.exceptions import PermissionDenied
            raise PermissionDenied("You don't have permission to create tasks for this project.")
        
        # Set team based on project
        serializer.save(created_by=user, team=project.team)
    
    @extend_schema(
        summary="List Tasks",
        description="Get list of tasks based on user permissions. Supports filtering by status, due date range, user, and search.",
        responses={200: TaskSerializer(many=True)}
    )
    def get(self, request, *args, **kwargs):
        return super().get(request, *args, **kwargs)
    
    @extend_schema(
        summary="Create Task",
        description="Create a new task (Manager/Admin only)",
        responses={
            201: TaskDetailSerializer,
            400: OpenApiResponse(description="Invalid input data"),
        }
    )
    def post(self, request, *args, **kwargs):
        return super().post(request, *args, **kwargs)


class TaskDetailView(generics.RetrieveUpdateDestroyAPIView):
    """
    Retrieve, update or delete a task.
    Only task creators, assignees, team managers, project managers, and admins can modify tasks.
    """
    queryset = Task.objects.all()
    serializer_class = TaskDetailSerializer
    permission_classes = [permissions.IsAuthenticated]
    
    def get_serializer_class(self):
        """Use different serializer for updates."""
        if self.request.method in ['PUT', 'PATCH']:
            return TaskDetailSerializer
        return TaskDetailSerializer
    
    def get_permissions(self):
        """Set permissions based on request method."""
        if self.request.method in ['PUT', 'PATCH', 'DELETE']:
            return [permissions.IsAuthenticated()]
        return [permissions.IsAuthenticated()]
    
    def check_object_permissions(self, request, obj):
        """Check if user can access this task."""
        super().check_object_permissions(request, obj)
        
        # Check if user can access this task
        if not obj.can_be_accessed_by(request.user):
            self.permission_denied(request)
    
    def check_object_permissions_for_write(self, request, obj):
        """Check if user can edit this task."""
        if not obj.can_be_edited_by(request.user):
            self.permission_denied(request)
    
    def put(self, request, *args, **kwargs):
        """Override put to check edit permissions."""
        obj = self.get_object()
        self.check_object_permissions_for_write(request, obj)
        return super().put(request, *args, **kwargs)
    
    def patch(self, request, *args, **kwargs):
        """Override patch to check edit permissions."""
        obj = self.get_object()
        self.check_object_permissions_for_write(request, obj)
        return super().patch(request, *args, **kwargs)
    
    @extend_schema(
        summary="Get Task Details",
        description="Retrieve detailed task information",
        responses={200: TaskDetailSerializer}
    )
    def get(self, request, *args, **kwargs):
        return super().get(request, *args, **kwargs)
    
    @extend_schema(
        summary="Update Task",
        description="Update task information",
        responses={200: TaskDetailSerializer}
    )
    def put(self, request, *args, **kwargs):
        return super().put(request, *args, **kwargs)
    
    @extend_schema(
        summary="Delete Task",
        description="Delete task (Admin only)",
        responses={204: OpenApiResponse(description="Task deleted")}
    )
    def delete(self, request, *args, **kwargs):
        # Only admins can delete tasks
        if not request.user.has_role('admin'):
            return Response({
                'error': 'Only admins can delete tasks'
            }, status=status.HTTP_403_FORBIDDEN)
        return super().delete(request, *args, **kwargs)


class TaskStatusUpdateView(APIView):
    """
    Update task status.
    Only task assignees, creators, team managers, project managers, and admins can update status.
    """
    permission_classes = [permissions.IsAuthenticated]
    
    @extend_schema(
        summary="Update Task Status",
        description="Update task status",
        request=TaskStatusUpdateSerializer,
        responses={
            200: TaskSerializer,
            400: OpenApiResponse(description="Invalid status transition"),
        }
    )
    def patch(self, request, pk):
        task = get_object_or_404(Task, pk=pk)
        
        # Check if user can edit this task
        if not task.can_be_edited_by(request.user):
            return Response({
                'error': 'You do not have permission to edit this task'
            }, status=status.HTTP_403_FORBIDDEN)
        
        serializer = TaskStatusUpdateSerializer(task, data=request.data, partial=True)
        
        if serializer.is_valid():
            serializer.save()
            return Response(TaskSerializer(task).data)
        
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class ProjectTasksView(generics.ListAPIView):
    """
    List tasks for a specific project.
    Only project team members can see project tasks.
    """
    serializer_class = TaskSerializer
    permission_classes = [permissions.IsAuthenticated]
    
    def get_queryset(self):
        """Get tasks for the specified project."""
        project_id = self.kwargs['project_id']
        project = get_object_or_404(Project, id=project_id)
        
        # Check if user can access this project's tasks
        if not project.can_be_accessed_by(self.request.user):
            return Task.objects.none()
        
        return project.tasks.all()


class TeamTasksView(generics.ListAPIView):
    """
    List tasks for a specific team.
    Only team members can see team tasks.
    """
    serializer_class = TaskSerializer
    permission_classes = [permissions.IsAuthenticated]
    
    def get_queryset(self):
        """Get tasks for the specified team."""
        team_id = self.kwargs['team_id']
        team = get_object_or_404(Team, id=team_id)
        
        # Check if user can access this team's tasks
        if not (team.is_manager(self.request.user) or 
                team.is_member(self.request.user) or 
                self.request.user.has_role('admin')):
            return Task.objects.none()
        
        return team.tasks.all()


class MyTasksView(generics.ListAPIView):
    """
    List tasks assigned to the current user.
    """
    serializer_class = TaskSerializer
    permission_classes = [permissions.IsAuthenticated]
    
    def get_queryset(self):
        """Get tasks assigned to the current user."""
        return Task.objects.filter(assigned_to=self.request.user)
    
    @extend_schema(
        summary="My Tasks",
        description="Get list of tasks assigned to current user",
        responses={200: TaskSerializer(many=True)}
    )
    def get(self, request, *args, **kwargs):
        return super().get(request, *args, **kwargs)


class CreatedTasksView(generics.ListAPIView):
    """
    List tasks created by the current user.
    """
    serializer_class = TaskSerializer
    permission_classes = [permissions.IsAuthenticated]
    
    def get_queryset(self):
        """Get tasks created by the current user."""
        return Task.objects.filter(created_by=self.request.user)
    
    @extend_schema(
        summary="Created Tasks",
        description="Get list of tasks created by current user",
        responses={200: TaskSerializer(many=True)}
    )
    def get(self, request, *args, **kwargs):
        return super().get(request, *args, **kwargs)


class TaskCommentsView(generics.ListCreateAPIView):
    """
    List comments for a task or add a new comment.
    Only users who can access the task can see/add comments.
    """
    serializer_class = TaskCommentSerializer
    permission_classes = [permissions.IsAuthenticated]
    
    def get_queryset(self):
        """Get comments for the specified task."""
        task_id = self.kwargs['task_id']
        task = get_object_or_404(Task, id=task_id)
        
        # Check if user can access this task
        if not task.can_be_accessed_by(self.request.user):
            return TaskComment.objects.none()
        
        return task.comments.all()
    
    def get_serializer_class(self):
        """Use different serializer for creation."""
        if self.request.method == 'POST':
            return TaskCommentCreateSerializer
        return TaskCommentSerializer
    
    def get_serializer_context(self):
        """Add task to serializer context."""
        context = super().get_serializer_context()
        context['task'] = get_object_or_404(Task, id=self.kwargs['task_id'])
        return context
    
    @extend_schema(
        summary="List Task Comments",
        description="Get list of comments for a task",
        responses={200: TaskCommentSerializer(many=True)}
    )
    def get(self, request, *args, **kwargs):
        return super().get(request, *args, **kwargs)
    
    @extend_schema(
        summary="Add Task Comment",
        description="Add a new comment to a task",
        responses={
            201: TaskCommentSerializer,
            400: OpenApiResponse(description="Invalid input data"),
        }
    )
    def post(self, request, *args, **kwargs):
        return super().post(request, *args, **kwargs)


class TaskAttachmentsView(generics.ListCreateAPIView):
    """
    List attachments for a task or add a new attachment.
    Only users who can access the task can see/add attachments.
    """
    serializer_class = TaskAttachmentSerializer
    permission_classes = [permissions.IsAuthenticated]
    
    def get_queryset(self):
        """Get attachments for the specified task."""
        task_id = self.kwargs['task_id']
        task = get_object_or_404(Task, id=task_id)
        
        # Check if user can access this task
        if not task.can_be_accessed_by(self.request.user):
            return TaskAttachment.objects.none()
        
        return task.attachments.all()
    
    def get_serializer_class(self):
        """Use different serializer for creation."""
        if self.request.method == 'POST':
            return TaskAttachmentCreateSerializer
        return TaskAttachmentSerializer
    
    def get_serializer_context(self):
        """Add task to serializer context."""
        context = super().get_serializer_context()
        context['task'] = get_object_or_404(Task, id=self.kwargs['task_id'])
        return context
    
    @extend_schema(
        summary="List Task Attachments",
        description="Get list of attachments for a task",
        responses={200: TaskAttachmentSerializer(many=True)}
    )
    def get(self, request, *args, **kwargs):
        return super().get(request, *args, **kwargs)
    
    @extend_schema(
        summary="Add Task Attachment",
        description="Add a new attachment to a task",
        responses={
            201: TaskAttachmentSerializer,
            400: OpenApiResponse(description="Invalid input data"),
        }
    )
    def post(self, request, *args, **kwargs):
        return super().post(request, *args, **kwargs)


class TaskStatisticsView(APIView):
    """
    Get task statistics for the current user.
    """
    permission_classes = [permissions.IsAuthenticated]
    
    @extend_schema(
        summary="Task Statistics",
        description="Get task statistics for current user",
        responses={200: OpenApiResponse(description="Task statistics")}
    )
    def get(self, request):
        user = request.user
        
        # Get user's tasks
        assigned_tasks = Task.objects.filter(assigned_to=user)
        created_tasks = Task.objects.filter(created_by=user)
        
        # Calculate statistics
        total_assigned = assigned_tasks.count()
        completed_assigned = assigned_tasks.filter(status='completed').count()
        overdue_assigned = sum(1 for task in assigned_tasks if task.is_overdue())
        
        total_created = created_tasks.count()
        completed_created = created_tasks.filter(status='completed').count()
        
        # Status breakdown for assigned tasks
        status_breakdown = {}
        for status_choice in assigned_tasks.values_list('status', flat=True).distinct():
            count = assigned_tasks.filter(status=status_choice).count()
            status_breakdown[status_choice] = count
        
        return Response({
            'assigned_tasks': {
                'total': total_assigned,
                'completed': completed_assigned,
                'pending': total_assigned - completed_assigned,
                'overdue': overdue_assigned,
                'status_breakdown': status_breakdown,
            },
            'created_tasks': {
                'total': total_created,
                'completed': completed_created,
                'pending': total_created - completed_created,
            }
        })
