from rest_framework import status, generics, permissions
from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework_simplejwt.token_blacklist.models import BlacklistedToken
from django.contrib.auth import authenticate
from django.utils import timezone
from drf_spectacular.utils import extend_schema, OpenApiResponse
from services.users.models import UserProfile
from .serializers import (
    UserRegistrationSerializer, 
    CustomTokenObtainPairSerializer,
    UserProfileSerializer,
    ChangePasswordSerializer
)
from services.users.models import User


class UserRegistrationView(generics.CreateAPIView):
    """
    User registration endpoint.
    Creates a new user account and assigns default employee role.
    """
    queryset = User.objects.all()
    serializer_class = UserRegistrationSerializer
    permission_classes = [permissions.AllowAny]
    
    @extend_schema(
        summary="User Registration",
        description="Register a new user account with email and password",
        responses={
            201: OpenApiResponse(description="User created successfully"),
            400: OpenApiResponse(description="Invalid input data"),
        }
    )
    def post(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        if serializer.is_valid():
            user = serializer.save()
            
            # User automatically gets employee role by default from the model
            # No need to create separate role assignment
            
            # Generate tokens for immediate login
            refresh = RefreshToken.for_user(user)
            
            return Response({
                'message': 'User registered successfully',
                'user': {
                    'id': user.id,
                    'email': user.email,
                    'full_name': user.get_full_name(),
                    'role': user.get_role_display()
                },
                'tokens': {
                    'access': str(refresh.access_token),
                    'refresh': str(refresh),
                }
            }, status=status.HTTP_201_CREATED)
        
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class CustomTokenObtainPairView(TokenObtainPairView):
    """
    Custom login view that returns user info along with tokens.
    """
    serializer_class = CustomTokenObtainPairSerializer
    
    @extend_schema(
        summary="User Login",
        description="Authenticate user and return JWT tokens with user information",
        responses={
            200: OpenApiResponse(description="Login successful"),
            401: OpenApiResponse(description="Invalid credentials"),
        }
    )
    def post(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        
        try:
            serializer.is_valid(raise_exception=True)
        except Exception as e:
            return Response({
                'error': 'Invalid credentials',
                'detail': str(e)
            }, status=status.HTTP_401_UNAUTHORIZED)
        
        user = serializer.user
        
        # Update last login IP in profile if exists
        if hasattr(request, 'META') and hasattr(user, 'profile'):
            x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
            if x_forwarded_for:
                ip = x_forwarded_for.split(',')[0]
            else:
                ip = request.META.get('REMOTE_ADDR')
            user.profile.last_login_ip = ip
            user.profile.save(update_fields=['last_login_ip'])
        
        return Response(serializer.validated_data, status=status.HTTP_200_OK)


class LogoutView(APIView):
    """
    Logout view that blacklists the refresh token.
    """
    permission_classes = [permissions.IsAuthenticated]
    
    @extend_schema(
        summary="User Logout",
        description="Logout user and blacklist refresh token",
        request={
            'application/json': {
                'type': 'object',
                'properties': {
                    'refresh_token': {'type': 'string'}
                },
                'required': ['refresh_token']
            }
        },
        responses={
            200: OpenApiResponse(description="Logout successful"),
            400: OpenApiResponse(description="Invalid token"),
        }
    )
    def post(self, request):
        try:
            # Accept both 'refresh' and 'refresh_token' field names
            refresh_token = request.data.get('refresh') or request.data.get('refresh_token')
            if not refresh_token:
                return Response({
                    'error': 'Refresh token is required'
                }, status=status.HTTP_400_BAD_REQUEST)
            
            token = RefreshToken(refresh_token)
            token.blacklist()
            
            return Response({
                'message': 'Successfully logged out'
            }, status=status.HTTP_205_RESET_CONTENT)
            
        except Exception as e:
            return Response({
                'error': 'Invalid token',
                'detail': str(e)
            }, status=status.HTTP_400_BAD_REQUEST)


class UserProfileView(generics.RetrieveUpdateAPIView):
    """
    View for retrieving and updating user profile.
    """
    serializer_class = UserProfileSerializer
    permission_classes = [permissions.IsAuthenticated]
    
    def get_object(self):
        user = self.request.user
        # Get or create the user profile
        profile, created = UserProfile.objects.get_or_create(user=user)
        return profile
    
    @extend_schema(
        summary="Get User Profile",
        description="Retrieve current user's profile information",
        responses={
            200: UserProfileSerializer,
        }
    )
    def get(self, request, *args, **kwargs):
        return super().get(request, *args, **kwargs)
    
    @extend_schema(
        summary="Update User Profile",
        description="Update current user's profile information",
        responses={
            200: UserProfileSerializer,
            400: OpenApiResponse(description="Invalid input data"),
        }
    )
    def put(self, request, *args, **kwargs):
        return super().put(request, *args, **kwargs)
    
    def patch(self, request, *args, **kwargs):
        return super().patch(request, *args, **kwargs)


class ChangePasswordView(APIView):
    """
    View for changing user password.
    """
    permission_classes = [permissions.IsAuthenticated]
    
    @extend_schema(
        summary="Change Password",
        description="Change current user's password",
        request=ChangePasswordSerializer,
        responses={
            200: OpenApiResponse(description="Password changed successfully"),
            400: OpenApiResponse(description="Invalid input data"),
        }
    )
    def post(self, request):
        serializer = ChangePasswordSerializer(data=request.data, context={'request': request})
        
        if serializer.is_valid():
            user = request.user
            validated_data = serializer.validated_data
            if validated_data and 'new_password' in validated_data:
                user.set_password(validated_data['new_password'])
                user.save()
                
                return Response({
                    'message': 'Password changed successfully'
                }, status=status.HTTP_200_OK)
        
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@extend_schema(
    summary="Verify Token",
    description="Verify if the provided JWT token is valid",
    responses={
        200: OpenApiResponse(description="Token is valid"),
        401: OpenApiResponse(description="Token is invalid"),
    }
)
@api_view(['POST'])
@permission_classes([permissions.IsAuthenticated])
def verify_token(request):
    """
    Simple endpoint to verify if token is valid.
    """
    user = request.user
    
    return Response({
        'valid': True,
        'user': {
            'id': user.id,
            'email': user.email,
            'full_name': user.get_full_name(),
            'role': user.get_role_display(),
        }
    }, status=status.HTTP_200_OK)
