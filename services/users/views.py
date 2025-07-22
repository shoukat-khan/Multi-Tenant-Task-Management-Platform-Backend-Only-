from rest_framework import generics, status, permissions
from rest_framework.response import Response
from rest_framework.views import APIView
from django.shortcuts import get_object_or_404
from drf_spectacular.utils import extend_schema, OpenApiResponse
from .models import User, UserProfile
from .permissions import IsAdminUser, IsManagerUser, IsOwnerOrManagerOrAdmin
from services.authentication.serializers import (
    UserListSerializer, 
    UserDetailSerializer
)


class UserListView(generics.ListCreateAPIView):
    """
    List all users or create a new user.
    Only managers and admins can access this endpoint.
    """
    queryset = User.objects.all()
    serializer_class = UserListSerializer
    permission_classes = [IsManagerUser]
    
    @extend_schema(
        summary="List Users",
        description="Get list of all users (Manager/Admin only)",
        responses={200: UserListSerializer(many=True)}
    )
    def get(self, request, *args, **kwargs):
        return super().get(request, *args, **kwargs)


class UserDetailView(generics.RetrieveUpdateDestroyAPIView):
    """
    Retrieve, update or delete a user.
    Users can access their own data, managers and admins can access any user.
    """
    queryset = User.objects.all()
    serializer_class = UserDetailSerializer
    permission_classes = [IsOwnerOrManagerOrAdmin]
    
    @extend_schema(
        summary="Get User Details",
        description="Retrieve user details",
        responses={200: UserDetailSerializer}
    )
    def get(self, request, *args, **kwargs):
        return super().get(request, *args, **kwargs)
    
    @extend_schema(
        summary="Update User",
        description="Update user information",
        responses={200: UserDetailSerializer}
    )
    def put(self, request, *args, **kwargs):
        return super().put(request, *args, **kwargs)
    
    def patch(self, request, *args, **kwargs):
        return super().patch(request, *args, **kwargs)
    
    @extend_schema(
        summary="Delete User",
        description="Delete user (Admin only)",
        responses={204: OpenApiResponse(description="User deleted")}
    )
    def delete(self, request, *args, **kwargs):
        # Only admins can delete users
        if not request.user.has_role(Role.ADMIN):
            return Response({
                'error': 'Only admins can delete users'
            }, status=status.HTTP_403_FORBIDDEN)
        return super().delete(request, *args, **kwargs)


class UserRoleManagementView(APIView):
    """
    View user role information.
    """
    permission_classes = [IsOwnerOrManagerOrAdmin]
    
    @extend_schema(
        summary="Get User Role",
        description="Get role assigned to a user",
        responses={200: OpenApiResponse(description="User role")}
    )
    def get(self, request, pk):
        user = get_object_or_404(User, pk=pk)
        self.check_object_permissions(request, user)
        
        return Response({
            'user': {
                'id': user.id,
                'email': user.email,
                'full_name': user.get_full_name(),
            },
            'role': {
                'name': user.role,
                'display_name': user.get_role_display(),
            }
        })


class UpdateUserRoleView(APIView):
    """
    Update a user's role.
    Only admins can update roles.
    """
    permission_classes = [IsAdminUser]
    
    @extend_schema(
        summary="Update User Role",
        description="Update a user's role (Admin only)",
        request={
            'application/json': {
                'type': 'object',
                'properties': {
                    'role': {
                        'type': 'string',
                        'enum': ['admin', 'manager', 'employee'],
                        'description': 'New role for the user'
                    },
                },
                'required': ['role']
            }
        },
        responses={
            200: OpenApiResponse(description="Role updated successfully"),
            400: OpenApiResponse(description="Invalid role"),
            404: OpenApiResponse(description="User not found"),
        }
    )
    def patch(self, request, pk):
        user = get_object_or_404(User, pk=pk)
        new_role = request.data.get('role')
        
        if not new_role:
            return Response({
                'error': 'role is required'
            }, status=status.HTTP_400_BAD_REQUEST)
        
        # Validate role choice
        from .models import Role
        valid_roles = [choice[0] for choice in Role.choices]
        if new_role not in valid_roles:
            return Response({
                'error': f'Invalid role. Must be one of: {", ".join(valid_roles)}'
            }, status=status.HTTP_400_BAD_REQUEST)
        
        # Prevent self-demotion from admin
        if request.user == user and request.user.role == 'admin' and new_role != 'admin':
            return Response({
                'error': 'You cannot remove your own admin privileges'
            }, status=status.HTTP_400_BAD_REQUEST)
        
        old_role = user.get_role_display()
        user.role = new_role
        user.save()
        
        return Response({
            'message': f'User role updated from {old_role} to {user.get_role_display()}',
            'user': {
                'id': user.id,
                'email': user.email,
                'full_name': user.get_full_name(),
                'role': user.role,
                'role_display': user.get_role_display(),
            }
        })


class UserProfileDetailView(generics.RetrieveUpdateAPIView):
    """
    Retrieve and update user profile details.
    """
    queryset = UserProfile.objects.all()
    permission_classes = [IsOwnerOrManagerOrAdmin]
    
    def get_object(self):
        user = get_object_or_404(User, pk=self.kwargs['pk'])
        self.check_object_permissions(self.request, user)
        profile, created = UserProfile.objects.get_or_create(user=user)
        return profile
    
    @extend_schema(
        summary="Get User Profile",
        description="Get detailed user profile information",
        responses={200: OpenApiResponse(description="User profile")}
    )
    def get(self, request, *args, **kwargs):
        profile = self.get_object()
        
        data = {
            'user': {
                'id': profile.user.id,
                'email': profile.user.email,
                'full_name': profile.user.get_full_name(),
            },
            'bio': profile.bio,
            'department': profile.department,
            'employee_id': profile.employee_id,
            'hire_date': profile.hire_date,
            'manager': {
                'id': profile.manager.id,
                'name': profile.manager.get_full_name(),
                'email': profile.manager.email,
            } if profile.manager else None,
            'timezone': profile.timezone,
            'preferences': profile.preferences,
            'created_at': profile.created_at,
            'updated_at': profile.updated_at,
        }
        
        return Response(data)
