"""
Test factories for creating test data using Factory Boy.
"""
import factory
from factory import fuzzy
from datetime import date, timedelta
from django.contrib.auth import get_user_model
from Services.users.models import UserProfile, Role
from Services.teams.models import Team
from Services.projects.models import Project
from Services.tasks.models import Task

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


class TeamFactory(factory.django.DjangoModelFactory):
    """Factory for creating Team instances."""
    
    class Meta:
        model = Team
    
    name = factory.Sequence(lambda n: f"Team {n}")
    description = factory.Faker('text', max_nb_chars=200)
    manager = factory.SubFactory(ManagerUserFactory)
    is_active = True
    
    @factory.post_generation
    def members(self, create, extracted, **kwargs):
        if not create:
            return
        
        if extracted:
            for member in extracted:
                self.members.add(member)


class ProjectFactory(factory.django.DjangoModelFactory):
    """Factory for creating Project instances."""
    
    class Meta:
        model = Project
    
    name = factory.Sequence(lambda n: f"Project {n}")
    description = factory.Faker('text', max_nb_chars=300)
    team = factory.SubFactory(TeamFactory)
    manager = factory.SubFactory(ManagerUserFactory)
    created_by = factory.SubFactory(ManagerUserFactory)
    status = fuzzy.FuzzyChoice(['planning', 'active', 'on_hold', 'completed'])
    priority = fuzzy.FuzzyChoice(['low', 'medium', 'high', 'urgent'])
    start_date = factory.LazyFunction(lambda: date.today())
    end_date = factory.LazyFunction(lambda: date.today() + timedelta(days=90))
    is_active = True


class TaskFactory(factory.django.DjangoModelFactory):
    """Factory for creating Task instances."""
    
    class Meta:
        model = Task
    
    title = factory.Sequence(lambda n: f"Task {n}")
    description = factory.Faker('text', max_nb_chars=500)
    project = factory.SubFactory(ProjectFactory)
    team = factory.SubFactory(TeamFactory)
    assigned_to = factory.SubFactory(UserFactory)
    created_by = factory.SubFactory(ManagerUserFactory)
    status = fuzzy.FuzzyChoice(['todo', 'in_progress', 'review', 'completed'])
    priority = fuzzy.FuzzyChoice(['low', 'medium', 'high', 'urgent'])
    due_date = factory.LazyFunction(lambda: date.today() + timedelta(days=7))
    is_active = True
    is_public = True
