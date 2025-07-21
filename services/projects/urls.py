from django.urls import path
from . import views

app_name = 'projects'

urlpatterns = [
    # Project endpoints
    path('', views.ProjectListView.as_view(), name='project-list'),
    path('<int:pk>/', views.ProjectDetailView.as_view(), name='project-detail'),
    path('<int:pk>/status/', views.ProjectStatusUpdateView.as_view(), name='project-status-update'),
    path('<int:pk>/statistics/', views.ProjectStatisticsView.as_view(), name='project-statistics'),
    
    # Team projects endpoint
    path('team/<int:team_id>/', views.TeamProjectsView.as_view(), name='team-projects'),
    
    # User-specific project endpoints
    path('my/', views.MyProjectsView.as_view(), name='my-projects'),
    path('managed/', views.ManagedProjectsView.as_view(), name='managed-projects'),
]
