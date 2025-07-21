from django.urls import path
from . import views

app_name = 'tasks'

urlpatterns = [
    # Task endpoints
    path('', views.TaskListView.as_view(), name='task-list'),
    path('<int:pk>/', views.TaskDetailView.as_view(), name='task-detail'),
    path('<int:pk>/status/', views.TaskStatusUpdateView.as_view(), name='task-status-update'),
    
    # Project tasks endpoint
    path('project/<int:project_id>/', views.ProjectTasksView.as_view(), name='project-tasks'),
    
    # Team tasks endpoint
    path('team/<int:team_id>/', views.TeamTasksView.as_view(), name='team-tasks'),
    
    # User-specific task endpoints
    path('my/', views.MyTasksView.as_view(), name='my-tasks'),
    path('created/', views.CreatedTasksView.as_view(), name='created-tasks'),
    path('statistics/', views.TaskStatisticsView.as_view(), name='task-statistics'),
    
    # Task comments endpoints
    path('<int:task_id>/comments/', views.TaskCommentsView.as_view(), name='task-comments'),
    
    # Task attachments endpoints
    path('<int:task_id>/attachments/', views.TaskAttachmentsView.as_view(), name='task-attachments'),
]
