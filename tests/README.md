# Week Three Authentication System - Test Suite

This directory contains comprehensive pytest tests for the Django authentication system.

## Test Structure

### Test Files

1. **`conftest.py`** - Pytest configuration and Django setup
2. **`factories.py`** - Factory Boy factories for creating test data
3. **`test_models.py`** - Tests for User and UserProfile models
4. **`test_serializers.py`** - Tests for authentication serializers
5. **`test_views.py`** - Tests for API endpoints and views
6. **`test_permissions.py`** - Tests for custom permissions and security
7. **`test_integration.py`** - Integration tests for complete workflows

### Test Categories

#### Model Tests (`test_models.py`)
- User model creation and validation
- UserProfile model functionality
- Role-based user creation (Admin, Manager, Employee)
- Model relationships and constraints
- String representations and methods

#### Serializer Tests (`test_serializers.py`)
- User registration serializer validation
- Token serializer functionality
- Profile serializer operations
- Role utility functions
- Password validation and security

#### View Tests (`test_views.py`)
- User registration API endpoint
- Login/logout functionality
- Profile management endpoints
- Role-based permissions
- JWT token handling

#### Permission Tests (`test_permissions.py`)
- Role-based permission classes
- JWT authentication
- Password security
- Account security features
- Permission hierarchy

#### Integration Tests (`test_integration.py`)
- Complete user journeys
- Authentication flow testing
- Security integration
- Error handling scenarios
- Multi-user workflows

### Test Data

The test suite uses Factory Boy for creating test data:

- **UserFactory** - Creates standard employee users
- **AdminUserFactory** - Creates admin users with staff privileges
- **ManagerUserFactory** - Creates manager users
- **UserProfileFactory** - Creates user profiles with realistic data

### Features Tested

#### Authentication System
- User registration with role assignment
- JWT token-based authentication
- Login/logout functionality
- Token refresh and blacklisting
- Password security and validation

#### Role Management
- Three-tier role system (Admin, Manager, Employee)
- Role-based permissions
- Staff privilege assignment
- Role hierarchy validation

#### User Profiles
- Profile creation and management
- Profile data validation
- One-to-one user relationships
- Profile update functionality

#### Security Features
- Password hashing with Argon2
- JWT token security
- Token blacklisting on logout
- Role-based access control
- Account activation/deactivation

## Running Tests

### Install Test Dependencies
```bash
pip install -r test_requirements.txt
```

### Run All Tests
```bash
pytest tests/
```

### Run Specific Test Files
```bash
pytest tests/test_models.py
pytest tests/test_views.py
pytest tests/test_integration.py
```

### Run Tests with Coverage
```bash
pytest tests/ --cov=services --cov-report=html
```

### Run Tests in Parallel
```bash
pytest tests/ -n auto
```

### Run Tests with Verbose Output
```bash
pytest tests/ -v
```

## Test Configuration

The test suite is configured in `conftest.py` with:
- Django settings configuration
- Database setup for testing
- Session management
- Proper cleanup procedures

## Database Testing

Tests use Django's test database which:
- Creates a temporary database for testing
- Runs each test in a transaction
- Rolls back changes after each test
- Ensures test isolation

## Coverage Goals

The test suite aims for comprehensive coverage of:
- All model methods and properties
- All serializer validation logic
- All API endpoints and responses
- All permission classes
- All security features
- All error scenarios

## Test Best Practices

1. **Isolation** - Each test is independent
2. **Factories** - Use Factory Boy for consistent test data
3. **Assertions** - Clear and specific assertions
4. **Coverage** - Test both success and error scenarios
5. **Security** - Comprehensive security testing
6. **Integration** - Test complete user workflows

## Maintenance

- Update tests when adding new features
- Maintain factory definitions for new models
- Add integration tests for new workflows
- Keep test documentation current
- Regular coverage analysis
