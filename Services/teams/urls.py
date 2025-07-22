from django.urls import path
from . import views

app_name = 'teams'

urlpatterns = [
    # Team endpoints
    path('', views.TeamListView.as_view(), name='team-list'),
    path('<int:pk>/', views.TeamDetailView.as_view(), name='team-detail'),
    
    # Team members endpoints
    path('<int:team_id>/members/', views.TeamMembersView.as_view(), name='team-members'),
    path('<int:team_id>/members/<int:member_id>/', views.TeamMemberDetailView.as_view(), name='team-member-detail'),
    
    # User-specific team endpoints
    path('my/', views.MyTeamsView.as_view(), name='my-teams'),
    path('managed/', views.ManagedTeamsView.as_view(), name='managed-teams'),
]
