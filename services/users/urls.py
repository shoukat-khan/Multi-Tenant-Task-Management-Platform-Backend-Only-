from django.urls import path
from . import views

app_name = 'users'

urlpatterns = [
    # User management endpoints
    path('', views.UserListView.as_view(), name='user-list'),
    path('<int:pk>/', views.UserDetailView.as_view(), name='user-detail'),
    path('<int:pk>/role/', views.UserRoleManagementView.as_view(), name='user-role'),
    path('<int:pk>/profile/', views.UserProfileDetailView.as_view(), name='user-profile'),
    
    # Admin endpoints
    path('<int:pk>/update-role/', views.UpdateUserRoleView.as_view(), name='update-user-role'),
]
