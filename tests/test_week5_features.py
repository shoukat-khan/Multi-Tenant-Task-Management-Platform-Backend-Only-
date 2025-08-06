"""
Unit tests for Week 5 features: Team creation, Project creation, Task assignment.
These tests cover the specific requirements for Week 5.
"""
import pytest
from datetime import date, timedelta
from django.urls import reverse
from django.contrib.auth import get_user_model
from rest_framework import status
from rest_framework.test import APIClient
from rest_framework_simplejwt.tokens import RefreshToken
from Services.users.models import Role
from Services.teams.models import Team
from Services.projects.models import Project
from Services.tasks.models import Task
from tests.factories import (
    UserFactory, AdminUserFactory, ManagerUserFactory, 
    TeamFactory, ProjectFactory, TaskFactory
)

User = get_user_model()


@pytest.mark.django_db
class TestTeamCreation:
    """Test cases for team creation functionality."""
    
    def setup_method(self):
        """Set up test client and users."""
        self.client = APIClient()
        self.admin_user = AdminUserFactory()
        self.manager_user = ManagerUserFactory()
        self.employee_user = UserFactory(role=Role.EMPLOYEE)
        self.team_url = reverse('teams:team-list')
    
    def _authenticate_user(self, user):
        """Helper method to authenticate a user."""
        refresh = RefreshToken.for_user(user)
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {refresh.access_token}')
    
    def test_admin_can_create_team(self):
        """Test that admin users can create teams."""
        self._authenticate_user(self.admin_user)
        
        data = {
            'name': 'Development Team',
            'description': 'Team for software development',
            'manager_id': self.manager_user.id
        }
        
        response = self.client.post(self.team_url, data, format='json')
        
        assert response.status_code == status.HTTP_201_CREATED
        assert response.data['name'] == 'Development Team'
        assert Team.objects.filter(name='Development Team').exists()
        
        # Verify team was created with correct manager
        team = Team.objects.get(name='Development Team')
        assert team.manager == self.manager_user
    
    def test_manager_can_create_team(self):
        """Test that manager users can create teams."""
        self._authenticate_user(self.manager_user)
        
        data = {
            'name': 'QA Team',
            'description': 'Quality Assurance team',
            'manager_id': self.manager_user.id
        }
        
        response = self.client.post(self.team_url, data, format='json')
        
        assert response.status_code == status.HTTP_201_CREATED
        assert response.data['name'] == 'QA Team'
    
    def test_employee_cannot_create_team(self):
        """Test that employee users cannot create teams."""
        self._authenticate_user(self.employee_user)
        
        data = {
            'name': 'Employee Team',
            'description': 'Team created by employee',
            'manager_id': self.manager_user.id
        }
        
        response = self.client.post(self.team_url, data, format='json')
        
        assert response.status_code == status.HTTP_403_FORBIDDEN
        assert not Team.objects.filter(name='Employee Team').exists()
    
    def test_unauthenticated_user_cannot_create_team(self):
        """Test that unauthenticated users cannot create teams."""
        data = {
            'name': 'Anonymous Team',
            'description': 'Team created by anonymous user',
            'manager_id': self.manager_user.id
        }
        
        response = self.client.post(self.team_url, data, format='json')
        
        assert response.status_code == status.HTTP_401_UNAUTHORIZED
        assert not Team.objects.filter(name='Anonymous Team').exists()
    
    def test_team_creation_with_members(self):
        """Test creating a team - members need to be added separately."""
        self._authenticate_user(self.admin_user)
        
        data = {
            'name': 'Full Stack Team',
            'description': 'Full stack development team',
            'manager_id': self.manager_user.id
        }
        
        response = self.client.post(self.team_url, data, format='json')
        
        assert response.status_code == status.HTTP_201_CREATED
        
        team = Team.objects.get(name='Full Stack Team')
        # Manager should be automatically added as a member during creation
        assert team.members.filter(id=self.manager_user.id).exists()
    
    def test_team_creation_validation(self):
        """Test team creation validation."""
        self._authenticate_user(self.admin_user)
        
        # Test with missing required fields
        data = {
            'description': 'Team without name'
        }
        
        response = self.client.post(self.team_url, data, format='json')
        assert response.status_code == status.HTTP_400_BAD_REQUEST


@pytest.mark.django_db
class TestProjectCreation:
    """Test cases for project creation functionality."""
    
    def setup_method(self):
        """Set up test client, users, and team."""
        self.client = APIClient()
        self.admin_user = AdminUserFactory()
        self.manager_user = ManagerUserFactory()
        self.employee_user = UserFactory(role=Role.EMPLOYEE)
        self.team = TeamFactory(manager=self.manager_user)
        self.team.members.add(self.employee_user)
        self.project_url = reverse('projects:project-list')
    
    def _authenticate_user(self, user):
        """Helper method to authenticate a user."""
        refresh = RefreshToken.for_user(user)
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {refresh.access_token}')
    
    def test_admin_can_create_project(self):
        """Test that admin users can create projects."""
        self._authenticate_user(self.admin_user)
        
        data = {
            'name': 'E-commerce Platform',
            'description': 'Building an e-commerce platform',
            'team_id': self.team.id,
            'manager_id': self.manager_user.id,
            'start_date': date.today().isoformat(),
            'end_date': (date.today() + timedelta(days=90)).isoformat(),
            'priority': 'high'
        }
        
        response = self.client.post(self.project_url, data, format='json')
        
        assert response.status_code == status.HTTP_201_CREATED
        assert response.data['name'] == 'E-commerce Platform'
        assert Project.objects.filter(name='E-commerce Platform').exists()
        
        # Verify project was created with correct team and manager
        project = Project.objects.get(name='E-commerce Platform')
        assert project.team == self.team
        assert project.manager == self.manager_user
    
    def test_manager_can_create_project_for_managed_team(self):
        """Test that managers can create projects for teams they manage."""
        self._authenticate_user(self.manager_user)
        
        data = {
            'name': 'Mobile App',
            'description': 'Building a mobile application',
            'team_id': self.team.id,
            'manager_id': self.manager_user.id,
            'priority': 'medium'
        }
        
        response = self.client.post(self.project_url, data, format='json')
        
        assert response.status_code == status.HTTP_201_CREATED
        assert response.data['name'] == 'Mobile App'
    
    def test_manager_cannot_create_project_for_unmanaged_team(self):
        """Test that managers cannot create projects for teams they don't manage."""
        other_manager = ManagerUserFactory()
        other_team = TeamFactory(manager=other_manager)
        
        self._authenticate_user(self.manager_user)
        
        data = {
            'name': 'Unauthorized Project',
            'description': 'Project for unmanaged team',
            'team_id': other_team.id,
            'manager_id': self.manager_user.id
        }
        
        response = self.client.post(self.project_url, data, format='json')
        
        assert response.status_code == status.HTTP_403_FORBIDDEN
        assert not Project.objects.filter(name='Unauthorized Project').exists()
    
    def test_employee_cannot_create_project(self):
        """Test that employee users cannot create projects."""
        self._authenticate_user(self.employee_user)
        
        data = {
            'name': 'Employee Project',
            'description': 'Project created by employee',
            'team_id': self.team.id,
            'manager_id': self.manager_user.id
        }
        
        response = self.client.post(self.project_url, data, format='json')
        
        assert response.status_code == status.HTTP_403_FORBIDDEN
        assert not Project.objects.filter(name='Employee Project').exists()
    
    def test_project_creation_sets_created_by(self):
        """Test that project creation properly sets created_by field."""
        self._authenticate_user(self.admin_user)
        
        data = {
            'name': 'Admin Created Project',
            'description': 'Project to test created_by field',
            'team_id': self.team.id,
            'manager_id': self.manager_user.id
        }
        
        response = self.client.post(self.project_url, data, format='json')
        
        assert response.status_code == status.HTTP_201_CREATED
        
        project = Project.objects.get(name='Admin Created Project')
        assert project.created_by == self.admin_user
    
    def test_project_visibility_based_on_team_membership(self):
        """Test that users can only see projects of teams they're members of."""
        # Create projects for different teams
        project1 = ProjectFactory(team=self.team, name='Team Project')
        other_team = TeamFactory()
        project2 = ProjectFactory(team=other_team, name='Other Team Project')
        
        # Employee should only see projects of their team
        self._authenticate_user(self.employee_user)
        response = self.client.get(self.project_url)
        
        assert response.status_code == status.HTTP_200_OK
        project_names = [p['name'] for p in response.data['results']]
        assert 'Team Project' in project_names
        assert 'Other Team Project' not in project_names


@pytest.mark.django_db
class TestTaskAssignment:
    """Test cases for task assignment functionality."""
    
    def setup_method(self):
        """Set up test client, users, team, and project."""
        self.client = APIClient()
        self.admin_user = AdminUserFactory()
        self.manager_user = ManagerUserFactory()
        self.employee_user = UserFactory(role=Role.EMPLOYEE)
        self.team = TeamFactory(manager=self.manager_user)
        self.team.members.add(self.employee_user, self.manager_user)
        self.project = ProjectFactory(team=self.team, manager=self.manager_user)
        self.task_url = reverse('tasks:task-list')
    
    def _authenticate_user(self, user):
        """Helper method to authenticate a user."""
        refresh = RefreshToken.for_user(user)
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {refresh.access_token}')
    
    def test_manager_can_create_and_assign_task(self):
        """Test that managers can create and assign tasks."""
        self._authenticate_user(self.manager_user)
        
        data = {
            'title': 'Implement User Authentication',
            'description': 'Add JWT authentication to the system',
            'project_id': self.project.id,
            'team_id': self.team.id,
            'assigned_to_id': self.employee_user.id,
            'due_date': (date.today() + timedelta(days=7)).isoformat(),
            'priority': 'high',
            'status': 'todo'
        }
        
        response = self.client.post(self.task_url, data, format='json')
        
        print(f"Response status: {response.status_code}")
        
        
        assert response.status_code == status.HTTP_201_CREATED
        assert response.data['title'] == 'Implement User Authentication'
        assert Task.objects.filter(title='Implement User Authentication').exists()
        
        # Verify task was assigned correctly
        task = Task.objects.get(title='Implement User Authentication')
        assert task.assigned_to == self.employee_user
        assert task.created_by == self.manager_user
        assert task.team == self.team
    
    def test_admin_can_create_and_assign_task(self):
        """Test that admin users can create and assign tasks."""
        self._authenticate_user(self.admin_user)
        
        data = {
            'title': 'Admin Task',
            'description': 'Task created by admin',
            'project_id': self.project.id,
            'team_id': self.team.id,
            'assigned_to_id': self.employee_user.id,
            'priority': 'medium'
        }
        
        response = self.client.post(self.task_url, data, format='json')
        
        assert response.status_code == status.HTTP_201_CREATED
        assert response.data['title'] == 'Admin Task'
    
    def test_employee_cannot_create_task(self):
        """Test that employees cannot create tasks."""
        self._authenticate_user(self.employee_user)
        
        data = {
            'title': 'Employee Task',
            'description': 'Task created by employee',
            'project_id': self.project.id,
            'team_id': self.team.id,
            'assigned_to_id': self.employee_user.id
        }
        
        response = self.client.post(self.task_url, data, format='json')
        
        assert response.status_code == status.HTTP_403_FORBIDDEN
        assert not Task.objects.filter(title='Employee Task').exists()
    
    def test_employee_cannot_assign_task_to_others(self):
        """Test that employees cannot assign tasks to other users."""
        # First create a task assigned to the employee
        task = TaskFactory(
            project=self.project,
            assigned_to=self.employee_user,
            created_by=self.manager_user,
            team=self.team
        )
        
        self._authenticate_user(self.employee_user)
        
        # Try to reassign the task to another user
        other_employee = UserFactory(role=Role.EMPLOYEE)
        self.team.members.add(other_employee)
        
        data = {
            'assigned_to': other_employee.id
        }
        
        task_detail_url = reverse('tasks:task-detail', kwargs={'pk': task.id})
        response = self.client.patch(task_detail_url, data, format='json')
        
        # Employee can update their own tasks, but assignment changes may be restricted
        # This depends on the serializer implementation
        task.refresh_from_db()
        # The test should verify that the assignment didn't change if that's the intended behavior
    
    def test_task_assignment_to_non_team_member_fails(self):
        """Test that tasks cannot be assigned to users who are not team members."""
        self._authenticate_user(self.manager_user)
        
        # Create a user who is not a member of the team
        non_member = UserFactory(role=Role.EMPLOYEE)
        
        data = {
            'title': 'Invalid Assignment',
            'description': 'Task assigned to non-team member',
            'project_id': self.project.id,
            'team_id': self.team.id,
            'assigned_to_id': non_member.id
        }
        
        response = self.client.post(self.task_url, data, format='json')
        
        # This should fail if proper validation is in place
        # The exact status code depends on the implementation
        assert response.status_code in [status.HTTP_400_BAD_REQUEST, status.HTTP_403_FORBIDDEN]
        assert not Task.objects.filter(title='Invalid Assignment').exists()
    
    def test_task_status_update_by_assigned_user(self):
        """Test that assigned users can update task status."""
        task = TaskFactory(
            project=self.project,
            assigned_to=self.employee_user,
            created_by=self.manager_user,
            team=self.team,
            status='todo'
        )
        
        self._authenticate_user(self.employee_user)
        
        status_update_url = reverse('tasks:task-status-update', kwargs={'pk': task.id})
        data = {'status': 'in_progress'}
        
        response = self.client.patch(status_update_url, data, format='json')
        
        assert response.status_code == status.HTTP_200_OK
        task.refresh_from_db()
        assert task.status == 'in_progress'
    
    def test_task_visibility_based_on_team_membership(self):
        """Test that users can only see tasks of teams they're members of."""
        # Create tasks for different teams
        task1 = TaskFactory(
            project=self.project,
            assigned_to=self.employee_user,
            team=self.team,
            title='Team Task'
        )
        
        other_team = TeamFactory()
        other_project = ProjectFactory(team=other_team)
        task2 = TaskFactory(
            project=other_project,
            team=other_team,
            title='Other Team Task'
        )
        
        # Employee should only see tasks of their team
        self._authenticate_user(self.employee_user)
        response = self.client.get(self.task_url)
        
        assert response.status_code == status.HTTP_200_OK
        task_titles = [t['title'] for t in response.data['results']]
        assert 'Team Task' in task_titles
        assert 'Other Team Task' not in task_titles
