from django.contrib.auth.models import AbstractUser, UserManager
from django.db import models


class Role(models.TextChoices):
    """
    Role choices for users in the system.
    """
    ADMIN = "admin", "Admin"
    MANAGER = "manager", "Manager"
    EMPLOYEE = "employee", "Employee"


class CustomUserManager(UserManager):
    """
    Custom user manager to handle superuser creation with proper role assignment.
    """
    
    def create_superuser(self, username_or_email=None, email=None, password=None, **extra_fields):
        """
        Create and return a superuser with admin role.
        Supports both old (username, email, password) and new (email, password) patterns.
        """
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)
        extra_fields.setdefault('role', Role.ADMIN)  # Set admin role for superusers
        
        if extra_fields.get('is_staff') is not True:
            raise ValueError('Superuser must have is_staff=True.')
        if extra_fields.get('is_superuser') is not True:
            raise ValueError('Superuser must have is_superuser=True.')
        
        # Handle both calling patterns
        if email is None:
            email = username_or_email
        
        if not email:
            raise ValueError('Email is required for superuser creation')
        
        # Generate username from email or use provided username in extra_fields
        username = extra_fields.get('username')
        if not username:
            if username_or_email and '@' not in username_or_email:
                # First argument was username
                username = username_or_email
            else:
                # Generate username from email
                username = email.split('@')[0]
                counter = 1
                original_username = username
                while self.filter(username=username).exists():
                    username = f"{original_username}_{counter}"
                    counter += 1
        
        # Clean up extra_fields
        extra_fields.pop('username', None)
        
        return self.create_user(username, email, password, **extra_fields)


class User(AbstractUser):
    """
    Abstract User model with minimal role implementation.
    All concrete behavior handled in serializers.
    """
    email = models.EmailField(unique=True)  # Make email unique for USERNAME_FIELD
    role = models.CharField(
        max_length=10, 
        choices=Role.choices, 
        default=Role.EMPLOYEE
    )
    
    # Use email as the username field
    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['username']
    
    # Use custom manager
    objects = CustomUserManager()
    
    def has_role(self, role_name):
        """Check if user has a specific role."""
        return self.role == role_name


class UserProfile(models.Model):
    """
    Extended user profile information.
    Contains all the concrete user data that was moved out of the abstract User model.
    """
    user = models.OneToOneField(
        User,
        on_delete=models.CASCADE,
        related_name='profile',
        help_text="User this profile belongs to"
    )
    
    # Personal Information
    phone_number = models.CharField(
        max_length=20,
        blank=True,
        null=True,
        help_text="User's phone number"
    )
    date_of_birth = models.DateField(
        blank=True,
        null=True,
        help_text="User's date of birth"
    )
    profile_picture = models.ImageField(
        upload_to='profile_pictures/',
        blank=True,
        null=True,
        help_text="User's profile picture"
    )
    bio = models.TextField(
        blank=True,
        null=True,
        max_length=500,
        help_text="User's biography"
    )
    
    # Work Information
    department = models.CharField(
        max_length=100,
        blank=True,
        null=True,
        help_text="User's department"
    )
    employee_id = models.CharField(
        max_length=50,
        blank=True,
        null=True,
        unique=True,
        help_text="Employee ID"
    )
    hire_date = models.DateField(
        blank=True,
        null=True,
        help_text="Date when user was hired"
    )
    manager = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='managed_employees',
        help_text="User's manager"
    )
    
    # System Information
    is_email_verified = models.BooleanField(
        default=False,
        help_text="Whether user's email is verified"
    )
    last_login_ip = models.GenericIPAddressField(
        blank=True,
        null=True,
        help_text="User's last login IP address"
    )
    timezone = models.CharField(
        max_length=50,
        default='UTC',
        help_text="User's timezone"
    )
    preferences = models.JSONField(
        default=dict,
        blank=True,
        help_text="User preferences as JSON"
    )
    
    # Contact Information
    address = models.TextField(
        blank=True,
        null=True,
        help_text="User's address"
    )
    emergency_contact_name = models.CharField(
        max_length=100,
        blank=True,
        null=True,
        help_text="Emergency contact name"
    )
    emergency_contact_phone = models.CharField(
        max_length=20,
        blank=True,
        null=True,
        help_text="Emergency contact phone number"
    )
    
    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'auth_user_profiles'
        verbose_name = 'User Profile'
        verbose_name_plural = 'User Profiles'
    
    def __str__(self):
        return f"{self.user.get_full_name()}'s Profile"
