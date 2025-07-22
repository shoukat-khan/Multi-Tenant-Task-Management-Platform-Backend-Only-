# Secure User Authentication Implementation

This project implements secure user authentication using Django REST Framework (DRF) with JWT tokens.

## Overview

Implement secure user authentication system with role-based permissions and JWT token management.

## Tasks

### 1. Authentication Integration
- Integrate DRF SimpleJWT for authentication
- Configure JWT token settings for security

### 2. Build APIs

#### User Registration (Sign Up)
- Create user registration endpoint
- Validate user input and email uniqueness
- Hash passwords securely
- Return appropriate success/error responses

#### Login (Token Generation)
- Implement login endpoint with email/username and password
- Generate JWT access and refresh tokens
- Return tokens with user information
- Handle authentication failures

#### Logout (Token Blacklist - Optional)
- Implement token blacklist functionality
- Invalidate refresh tokens on logout
- Secure token cleanup process

### 3. User Roles

Implement three distinct user roles with different permission levels:

#### Admin
- **Full access** to all system features
- User management capabilities
- System configuration access
- Complete CRUD operations on all resources

#### Manager
- **Team/project/task creation** permissions
- Team member management
- Project oversight and reporting
- Task assignment and monitoring
- Limited administrative functions

#### Employee
- **View & update own tasks** only
- Personal profile management
- Task status updates
- Time tracking for assigned tasks
- Read-only access to team information

### 4. Permission System

#### Permission Levels:
- **Admin Permissions**: Full system access, user management, system settings
- **Manager Permissions**: Team leadership, project creation, task management for their teams
- **Employee Permissions**: Self-service access, own task management, profile updates

#### Implementation Requirements:
- Role-based permission decorators
- API endpoint protection based on user roles
- Hierarchical permission structure
- Secure permission validation

## Security Features

- JWT token-based authentication
- Password hashing and validation
- Role-based access control (RBAC)
- Token refresh mechanism
- Optional token blacklisting for logout
- Input validation and sanitization
- Secure API endpoints

## Technical Stack

- **Backend**: Django REST Framework (DRF)
- **Authentication**: DRF SimpleJWT
- **Database**: Django ORM (supports PostgreSQL, MySQL, SQLite)
- **Security**: JWT tokens, password hashing, permission classes

## Getting Started

1. Install required dependencies
2. Configure JWT settings in Django settings
3. Create user models with role fields
4. Implement authentication views and serializers
5. Set up permission classes
6. Create API endpoints
7. Test authentication flow

## API Endpoints

```
POST /api/auth/register/     # User registration
POST /api/auth/login/        # User login (token generation)
POST /api/auth/logout/       # User logout (token blacklist)
POST /api/auth/refresh/      # Token refresh
GET  /api/auth/profile/      # Get user profile
PUT  /api/auth/profile/      # Update user profile
```

## Role-Based Permissions

- Admins can access all endpoints
- Managers can create teams, projects, and manage tasks
- Employees can only view and update their own tasks

This implementation ensures secure, scalable user authentication with proper role-based access control.
