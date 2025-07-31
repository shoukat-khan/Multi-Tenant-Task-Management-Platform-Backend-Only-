"""
Unit tests for filtering and search functionality (Week 5).
Tests for DjangoFilterBackend, SearchFilter, and query parameters.
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
class TestTaskFiltering:
    """Test cases for task filtering functionality."""
    
    def setup_method(self):
        """Set up test data for filtering tests."""
        self.client = APIClient()
        self.admin_user = AdminUserFactory()
        self.manager_user = ManagerUserFactory()
        self.employee_user = UserFactory(role=Role.EMPLOYEE)
        
        # Create team and project
        self.team = TeamFactory(manager=self.manager_user)
        self.team.members.add(self.employee_user, self.manager_user)
        self.project = ProjectFactory(team=self.team, manager=self.manager_user)
        
        # Create tasks with different statuses, priorities, and due dates
        self.task1 = TaskFactory(
            title='Urgent Bug Fix',
            project=self.project,
            team=self.team,
            assigned_to=self.employee_user,
            status='todo',
            priority='urgent',
            due_date=date.today() + timedelta(days=1)
        )
        
        self.task2 = TaskFactory(
            title='Feature Development',
            project=self.project,
            team=self.team,
            assigned_to=self.employee_user,
            status='in_progress',
            priority='high',
            due_date=date.today() + timedelta(days=7)
        )
        
        self.task3 = TaskFactory(
            title='Code Review',
            project=self.project,
            team=self.team,
            assigned_to=self.manager_user,
            status='completed',
            priority='medium',
            due_date=date.today() - timedelta(days=1)  # Overdue
        )
        
        self.task_url = reverse('tasks:task-list')
        
        # Authenticate as admin to see all tasks
        refresh = RefreshToken.for_user(self.admin_user)
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {refresh.access_token}')
    
    def test_filter_tasks_by_status(self):
        """Test filtering tasks by status."""
        # Filter by 'todo' status
        response = self.client.get(self.task_url, {'status': 'todo'})
        
        assert response.status_code == status.HTTP_200_OK
        assert len(response.data['results']) == 1
        assert response.data['results'][0]['title'] == 'Urgent Bug Fix'
        
        # Filter by 'in_progress' status
        response = self.client.get(self.task_url, {'status': 'in_progress'})
        
        assert response.status_code == status.HTTP_200_OK
        assert len(response.data['results']) == 1
        assert response.data['results'][0]['title'] == 'Feature Development'
    
    def test_filter_tasks_by_priority(self):
        """Test filtering tasks by priority."""
        # Filter by 'urgent' priority
        response = self.client.get(self.task_url, {'priority': 'urgent'})
        
        assert response.status_code == status.HTTP_200_OK
        assert len(response.data['results']) == 1
        assert response.data['results'][0]['title'] == 'Urgent Bug Fix'
        
        # Filter by 'high' priority
        response = self.client.get(self.task_url, {'priority': 'high'})
        
        assert response.status_code == status.HTTP_200_OK
        assert len(response.data['results']) == 1
        assert response.data['results'][0]['title'] == 'Feature Development'
    
    def test_filter_tasks_by_assigned_user(self):
        """Test filtering tasks by assigned user."""
        # Filter by employee user
        response = self.client.get(self.task_url, {'assigned_to': self.employee_user.id})
        
        assert response.status_code == status.HTTP_200_OK
        assert len(response.data['results']) == 2
        titles = [task['title'] for task in response.data['results']]
        assert 'Urgent Bug Fix' in titles
        assert 'Feature Development' in titles
        
        # Filter by manager user
        response = self.client.get(self.task_url, {'assigned_to': self.manager_user.id})
        
        assert response.status_code == status.HTTP_200_OK
        assert len(response.data['results']) == 1
        assert response.data['results'][0]['title'] == 'Code Review'
    
    def test_filter_tasks_by_due_date_range(self):
        """Test filtering tasks by due date range."""
        today = date.today()
        
        # Filter tasks due after today
        response = self.client.get(self.task_url, {'due_date_after': today.isoformat()})
        
        assert response.status_code == status.HTTP_200_OK
        assert len(response.data['results']) == 2
        titles = [task['title'] for task in response.data['results']]
        assert 'Urgent Bug Fix' in titles
        assert 'Feature Development' in titles
        
        # Filter tasks due before today
        response = self.client.get(self.task_url, {'due_date_before': today.isoformat()})
        
        assert response.status_code == status.HTTP_200_OK
        assert len(response.data['results']) == 1
        assert response.data['results'][0]['title'] == 'Code Review'
    
    def test_filter_tasks_by_project(self):
        """Test filtering tasks by project."""
        response = self.client.get(self.task_url, {'project': self.project.id})
        
        assert response.status_code == status.HTTP_200_OK
        assert len(response.data['results']) == 3
    
    def test_filter_tasks_by_team(self):
        """Test filtering tasks by team."""
        response = self.client.get(self.task_url, {'team': self.team.id})
        
        assert response.status_code == status.HTTP_200_OK
        assert len(response.data['results']) == 3
    
    def test_search_tasks_by_title(self):
        """Test searching tasks by title."""
        response = self.client.get(self.task_url, {'search': 'Bug'})
        
        assert response.status_code == status.HTTP_200_OK
        assert len(response.data['results']) == 1
        assert response.data['results'][0]['title'] == 'Urgent Bug Fix'
    
    def test_search_tasks_by_description(self):
        """Test searching tasks by description."""
        # Update a task with specific unique description
        unique_term = 'UNIQUE_SECURITY_VULNERABILITY_FIX_12345'
        self.task1.description = f'Critical {unique_term} implementation'
        self.task1.save()
        
        response = self.client.get(self.task_url, {'search': unique_term})
        
        assert response.status_code == status.HTTP_200_OK
        assert len(response.data['results']) == 1
        assert response.data['results'][0]['title'] == 'Urgent Bug Fix'
    
    def test_combined_filtering(self):
        """Test combining multiple filters."""
        response = self.client.get(self.task_url, {
            'status': 'todo',
            'priority': 'urgent',
            'assigned_to': self.employee_user.id
        })
        
        assert response.status_code == status.HTTP_200_OK
        assert len(response.data['results']) == 1
        assert response.data['results'][0]['title'] == 'Urgent Bug Fix'
    
    def test_ordering_tasks(self):
        """Test ordering tasks by different fields."""
        # Order by due date ascending
        response = self.client.get(self.task_url, {'ordering': 'due_date'})
        
        assert response.status_code == status.HTTP_200_OK
        results = response.data['results']
        assert len(results) == 3
        # Should be ordered: Code Review (overdue), Urgent Bug Fix (tomorrow), Feature Development (next week)
        assert results[0]['title'] == 'Code Review'
        assert results[1]['title'] == 'Urgent Bug Fix'
        assert results[2]['title'] == 'Feature Development'
        
        # Order by due date descending
        response = self.client.get(self.task_url, {'ordering': '-due_date'})
        
        assert response.status_code == status.HTTP_200_OK
        results = response.data['results']
        assert results[0]['title'] == 'Feature Development'
        assert results[2]['title'] == 'Code Review'


@pytest.mark.django_db
class TestProjectFiltering:
    """Test cases for project filtering functionality."""
    
    def setup_method(self):
        """Set up test data for project filtering tests."""
        self.client = APIClient()
        self.admin_user = AdminUserFactory()
        self.manager_user = ManagerUserFactory()
        self.manager_user2 = ManagerUserFactory()
        
        # Create teams
        self.team1 = TeamFactory(name='Backend Team', manager=self.manager_user)
        self.team2 = TeamFactory(name='Frontend Team', manager=self.manager_user2)
        
        # Create projects with different attributes
        self.project1 = ProjectFactory(
            name='E-commerce Backend',
            team=self.team1,
            manager=self.manager_user,
            status='active',
            priority='high',
            start_date=date.today(),
            end_date=date.today() + timedelta(days=90)
        )
        
        self.project2 = ProjectFactory(
            name='Mobile App Frontend',
            team=self.team2,
            manager=self.manager_user2,
            status='planning',
            priority='medium',
            start_date=date.today() + timedelta(days=7),
            end_date=date.today() + timedelta(days=120)
        )
        
        self.project3 = ProjectFactory(
            name='Legacy System Migration',
            team=self.team1,
            manager=self.manager_user,
            status='completed',
            priority='low',
            start_date=date.today() - timedelta(days=30),
            end_date=date.today() - timedelta(days=1)
        )
        
        self.project_url = reverse('projects:project-list')
        
        # Authenticate as admin to see all projects
        refresh = RefreshToken.for_user(self.admin_user)
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {refresh.access_token}')
    
    def test_filter_projects_by_team(self):
        """Test filtering projects by team."""
        # Filter by team1
        response = self.client.get(self.project_url, {'team': self.team1.id})
        
        assert response.status_code == status.HTTP_200_OK
        assert len(response.data['results']) == 2
        titles = [proj['name'] for proj in response.data['results']]
        assert 'E-commerce Backend' in titles
        assert 'Legacy System Migration' in titles
        
        # Filter by team2
        response = self.client.get(self.project_url, {'team': self.team2.id})
        
        assert response.status_code == status.HTTP_200_OK
        assert len(response.data['results']) == 1
        assert response.data['results'][0]['name'] == 'Mobile App Frontend'
    
    def test_filter_projects_by_team_name(self):
        """Test filtering projects by team name."""
        response = self.client.get(self.project_url, {'team_name': 'Backend'})
        
        assert response.status_code == status.HTTP_200_OK
        assert len(response.data['results']) == 2
    
    def test_filter_projects_by_manager(self):
        """Test filtering projects by manager (owner)."""
        # Filter by manager_user
        response = self.client.get(self.project_url, {'manager': self.manager_user.id})
        
        assert response.status_code == status.HTTP_200_OK
        assert len(response.data['results']) == 2
        titles = [proj['name'] for proj in response.data['results']]
        assert 'E-commerce Backend' in titles
        assert 'Legacy System Migration' in titles
        
        # Filter by manager_user2
        response = self.client.get(self.project_url, {'manager': self.manager_user2.id})
        
        assert response.status_code == status.HTTP_200_OK
        assert len(response.data['results']) == 1
        assert response.data['results'][0]['name'] == 'Mobile App Frontend'
    
    def test_filter_projects_by_status(self):
        """Test filtering projects by status."""
        # Filter by 'active' status
        response = self.client.get(self.project_url, {'status': 'active'})
        
        assert response.status_code == status.HTTP_200_OK
        assert len(response.data['results']) == 1
        assert response.data['results'][0]['name'] == 'E-commerce Backend'
        
        # Filter by 'completed' status
        response = self.client.get(self.project_url, {'status': 'completed'})
        
        assert response.status_code == status.HTTP_200_OK
        assert len(response.data['results']) == 1
        assert response.data['results'][0]['name'] == 'Legacy System Migration'
    
    def test_filter_projects_by_priority(self):
        """Test filtering projects by priority."""
        response = self.client.get(self.project_url, {'priority': 'high'})
        
        assert response.status_code == status.HTTP_200_OK
        assert len(response.data['results']) == 1
        assert response.data['results'][0]['name'] == 'E-commerce Backend'
    
    def test_filter_projects_by_date_range(self):
        """Test filtering projects by date range."""
        today = date.today()
        
        # Filter projects starting after today
        response = self.client.get(self.project_url, {'start_date_after': today.isoformat()})
        
        assert response.status_code == status.HTTP_200_OK
        assert len(response.data['results']) == 2  # Today and future starts
        
        # Filter projects ending before today
        response = self.client.get(self.project_url, {'end_date_before': today.isoformat()})
        
        assert response.status_code == status.HTTP_200_OK
        assert len(response.data['results']) == 1
        assert response.data['results'][0]['name'] == 'Legacy System Migration'
    
    def test_search_projects_by_name(self):
        """Test searching projects by name."""
        # Update project with unique name to avoid conflicts with random data
        unique_name = 'UNIQUE_BACKEND_PROJECT_12345'
        self.project1.name = unique_name
        self.project1.save()
        
        response = self.client.get(self.project_url, {'search': unique_name})
        
        assert response.status_code == status.HTTP_200_OK
        assert len(response.data['results']) == 1
        assert response.data['results'][0]['name'] == unique_name
    
    def test_search_projects_by_description(self):
        """Test searching projects by description."""
        # Update project description
        self.project1.description = 'Building scalable e-commerce platform'
        self.project1.save()
        
        response = self.client.get(self.project_url, {'search': 'scalable'})
        
        assert response.status_code == status.HTTP_200_OK
        assert len(response.data['results']) == 1
        assert response.data['results'][0]['name'] == 'E-commerce Backend'
    
    def test_combined_project_filtering(self):
        """Test combining multiple project filters."""
        response = self.client.get(self.project_url, {
            'team': self.team1.id,
            'status': 'active',
            'priority': 'high'
        })
        
        assert response.status_code == status.HTTP_200_OK
        assert len(response.data['results']) == 1
        assert response.data['results'][0]['name'] == 'E-commerce Backend'
    
    def test_ordering_projects(self):
        """Test ordering projects by different fields."""
        # Order by start date ascending
        response = self.client.get(self.project_url, {'ordering': 'start_date'})
        
        assert response.status_code == status.HTTP_200_OK
        results = response.data['results']
        assert len(results) == 3
        # Should be ordered by start date
        assert results[0]['name'] == 'Legacy System Migration'  # Oldest start date
        assert results[2]['name'] == 'Mobile App Frontend'  # Latest start date


@pytest.mark.django_db
class TestPermissionBasedFiltering:
    """Test that filtering respects user permissions and team membership."""
    
    def setup_method(self):
        """Set up test data for permission-based filtering."""
        self.client = APIClient()
        self.manager_user = ManagerUserFactory()
        self.employee_user = UserFactory(role=Role.EMPLOYEE)
        
        # Create teams - employee is only member of team1
        self.team1 = TeamFactory(manager=self.manager_user)
        self.team1.members.add(self.employee_user, self.manager_user)
        
        self.team2 = TeamFactory()  # Employee is not a member
        
        # Create projects for both teams
        self.project1 = ProjectFactory(team=self.team1, name='Accessible Project')
        self.project2 = ProjectFactory(team=self.team2, name='Inaccessible Project')
        
        # Create tasks for both projects
        self.task1 = TaskFactory(
            project=self.project1, 
            team=self.team1, 
            title='Accessible Task',
            assigned_to=self.employee_user
        )
        self.task2 = TaskFactory(
            project=self.project2, 
            team=self.team2, 
            title='Inaccessible Task'
        )
    
    def test_employee_filtering_respects_team_membership(self):
        """Test that employee filtering only shows results from their teams."""
        # Authenticate as employee
        refresh = RefreshToken.for_user(self.employee_user)
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {refresh.access_token}')
        
        # Test project filtering
        project_url = reverse('projects:project-list')
        response = self.client.get(project_url)
        
        assert response.status_code == status.HTTP_200_OK
        project_names = [p['name'] for p in response.data['results']]
        assert 'Accessible Project' in project_names
        assert 'Inaccessible Project' not in project_names
        
        # Test task filtering
        task_url = reverse('tasks:task-list')
        response = self.client.get(task_url)
        
        assert response.status_code == status.HTTP_200_OK
        task_titles = [t['title'] for t in response.data['results']]
        assert 'Accessible Task' in task_titles
        assert 'Inaccessible Task' not in task_titles
    
    def test_manager_filtering_includes_managed_teams(self):
        """Test that manager filtering includes teams they manage."""
        # Authenticate as manager
        refresh = RefreshToken.for_user(self.manager_user)
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {refresh.access_token}')
        
        # Manager should see projects from team1 (which they manage)
        project_url = reverse('projects:project-list')
        response = self.client.get(project_url)
        
        assert response.status_code == status.HTTP_200_OK
        project_names = [p['name'] for p in response.data['results']]
        assert 'Accessible Project' in project_names
        # May or may not see team2 projects depending on implementation
