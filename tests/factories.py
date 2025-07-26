"""
Test factories for creating test data using Factory Boy.
"""
import factory
from factory import fuzzy
from django.contrib.auth import get_user_model
from Services.users.models import UserProfile, Role

User = get_user_model()


class UserFactory(factory.django.DjangoModelFactory):
    """Factory for creating User instances."""
    
    class Meta:
        model = User
    
    username = factory.Sequence(lambda n: f"user{n}")
    email = factory.Sequence(lambda n: f"user{n}@example.com")
    first_name = factory.Faker('first_name')
    last_name = factory.Faker('last_name')
    role = Role.EMPLOYEE
    is_active = True
    is_staff = False
    is_superuser = False


class AdminUserFactory(UserFactory):
    """Factory for creating Admin User instances."""
    
    role = Role.ADMIN
    is_staff = True


class ManagerUserFactory(UserFactory):
    """Factory for creating Manager User instances."""
    
    role = Role.MANAGER


class UserProfileFactory(factory.django.DjangoModelFactory):
    """Factory for creating UserProfile instances."""
    
    class Meta:
        model = UserProfile
    
    user = factory.SubFactory(UserFactory)
    phone_number = factory.Sequence(lambda n: f"+155500{n:05d}")
    bio = factory.Faker('text', max_nb_chars=200)
    department = factory.Faker('job')
    employee_id = factory.Sequence(lambda n: f"EMP{n:04d}")
    timezone = 'UTC'
    address = factory.Faker('address')
    emergency_contact_name = factory.Faker('name')
    emergency_contact_phone = factory.Sequence(lambda n: f"+155510{n:05d}")


class AdminProfileFactory(UserProfileFactory):
    """Factory for creating Admin UserProfile instances."""
    
    user = factory.SubFactory(AdminUserFactory)


class ManagerProfileFactory(UserProfileFactory):
    """Factory for creating Manager UserProfile instances."""
    
    user = factory.SubFactory(ManagerUserFactory)
