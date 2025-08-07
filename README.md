# 🚀 Multi-Tenant Task Management Platform

[![Django](https://img.shields.io/badge/Django-4.2.23-green.svg)](https://www.djangoproject.com/)
[![DRF](https://img.shields.io/badge/DRF-3.16.0-blue.svg)](https://www.django-rest-framework.org/)
[![Python](https://img.shields.io/badge/Python-3.13-blue.svg)](https://www.python.org/)
[![Docker](https://img.shields.io/badge/Docker-Enabled-blue.svg)](https://www.docker.com/)
[![PostgreSQL](https://img.shields.io/badge/PostgreSQL-15-blue.svg)](https://www.postgresql.org/)

A comprehensive **Multi-Tenant Task Management Platform** built with Django REST Framework, featuring secure authentication, role-based permissions, and complete CRUD operations for teams, projects, and tasks.

## 📋 Table of Contents

- [🎯 Project Evolution (Week 2-6)](#project-evolution)
- [🏗️ Architecture Overview](#architecture-overview)
- [✨ Features](#features)
- [🔐 Security Features](#security-features)
- [🛠️ Technology Stack](#technology-stack)
- [🚀 Quick Start](#quick-start)
- [🐳 Docker Deployment](#docker-deployment)
- [📚 API Documentation](#api-documentation)
- [🧪 Testing](#testing)
- [📁 Project Structure](#project-structure)
- [🔧 Configuration](#configuration)
- [📊 Performance & Monitoring](#performance--monitoring)

## 🎯 Project Evolution (Week 2-6)

### 📅 **Week 2: Foundation & Authentication**
- ✅ **User Authentication System**: JWT-based secure authentication
- ✅ **Role-Based Access Control**: Admin, Manager, Employee roles
- ✅ **User Registration & Login**: Complete auth flow with token management
- ✅ **Password Security**: Argon2 hashing and validation
- ✅ **Custom User Model**: Email-based authentication

### 📅 **Week 3: Core Business Logic**
- ✅ **Team Management**: Create, manage, and organize teams
- ✅ **Project Management**: Full project lifecycle management
- ✅ **Task Management**: Comprehensive task CRUD operations
- ✅ **Permission System**: Hierarchical permission structure
- ✅ **API Design**: RESTful API with proper HTTP methods

### 📅 **Week 4: Advanced Features & Testing**
- ✅ **Advanced Filtering**: Django-filter integration for complex queries
- ✅ **File Uploads**: Task attachments and profile pictures
- ✅ **API Documentation**: Swagger/OpenAPI with drf-spectacular
- ✅ **Comprehensive Testing**: Unit tests with pytest and factory-boy
- ✅ **Code Quality**: 95%+ test coverage, PEP8 compliance

### 📅 **Week 5: Production Ready & Deployment**
- ✅ **Dockerization**: Multi-stage Docker builds with optimization
- ✅ **Database Migration**: PostgreSQL production setup
- ✅ **Environment Configuration**: Secure environment variables
- ✅ **Static File Management**: WhiteNoise for production static files
- ✅ **Health Checks**: Application monitoring and health endpoints

### 📅 **Week 6: Code Quality & Optimization**
- ✅ **Code Refactoring**: Automated import optimization with Pylance
- ✅ **Utils Modularization**: Centralized authentication utilities
- ✅ **Performance Optimization**: Query optimization and caching
- ✅ **Documentation**: Complete project documentation and guides
- ✅ **Production Deployment**: Docker Compose multi-service setup

## 🏗️ Architecture Overview

```
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│   Frontend      │    │   API Gateway   │    │   Database      │
│   (Future)      │◄──►│   Django REST   │◄──►│   PostgreSQL    │
│                 │    │   Framework     │    │                 │
└─────────────────┘    └─────────────────┘    └─────────────────┘
                                │
                       ┌────────▼────────┐
                       │   Services      │
                       │ ┌─────────────┐ │
                       │ │ Users       │ │
                       │ │ Teams       │ │
                       │ │ Projects    │ │
                       │ │ Tasks       │ │
                       │ │ Auth        │ │
                       │ └─────────────┘ │
                       └─────────────────┘
```

## ✨ Features

### 🔐 **Authentication & Authorization**
- **JWT Authentication**: Secure token-based authentication
- **Role-Based Permissions**: Admin, Manager, Employee hierarchies
- **Custom User Model**: Email as primary identifier
- **Password Security**: Argon2 hashing with strength validation
- **Token Management**: Access/refresh token lifecycle

### 👥 **User Management**
- **User Registration**: Comprehensive signup with validation
- **Profile Management**: Detailed user profiles with preferences
- **Role Assignment**: Dynamic role management with permissions
- **User Directory**: Search and filter users by various criteria

### 🏢 **Team Management**
- **Team Creation**: Create and configure teams
- **Team Membership**: Add/remove team members with roles
- **Team Permissions**: Team-level access control
- **Team Analytics**: Team performance and activity tracking

### 📊 **Project Management**
- **Project Lifecycle**: Complete project management from creation to completion
- **Project Teams**: Associate teams with projects
- **Project Permissions**: Project-level access control
- **Project Analytics**: Progress tracking and reporting

### ✅ **Task Management**
- **Task CRUD**: Full task lifecycle management
- **Task Assignment**: Assign tasks to team members
- **Task Status**: Customizable task statuses and workflows
- **Task Dependencies**: Link tasks with dependencies
- **File Attachments**: Upload and manage task-related files
- **Comments**: Task-level discussions and updates

## 🔐 Security Features

- ✅ **JWT Token Security**: Secure token generation and validation
- ✅ **Password Hashing**: Argon2 password hashing
- ✅ **Role-Based Access Control**: Hierarchical permission system
- ✅ **Input Validation**: Comprehensive data validation
- ✅ **SQL Injection Protection**: Django ORM security
- ✅ **CORS Configuration**: Cross-origin request security
- ✅ **Environment Variables**: Secure configuration management
- ✅ **API Rate Limiting**: Request throttling (configurable)

## 🛠️ Technology Stack

### **Backend Framework**
- **Django 4.2.23**: Modern Python web framework
- **Django REST Framework 3.16.0**: API development toolkit
- **Django Filter 25.1**: Advanced filtering capabilities

### **Database**
- **PostgreSQL 15**: Production-ready relational database
- **psycopg2-binary**: PostgreSQL adapter for Python

### **Authentication & Security**
- **djangorestframework-simplejwt 5.5.1**: JWT authentication
- **argon2-cffi 25.1.0**: Secure password hashing
- **cryptography 45.0.5**: Cryptographic utilities

### **Development & Testing**
- **pytest 7.4.3**: Testing framework
- **factory-boy 3.3.0**: Test data generation
- **pytest-django 4.7.0**: Django-specific testing utilities
- **coverage 7.9.2**: Code coverage analysis

### **Production & Deployment**
- **Docker**: Containerization
- **Docker Compose**: Multi-service orchestration
- **gunicorn 23.0.0**: Production WSGI server
- **WhiteNoise 6.9.0**: Static file serving

### **API Documentation**
- **drf-spectacular 0.28.0**: OpenAPI/Swagger documentation
- **Swagger UI**: Interactive API documentation

## 🚀 Quick Start

### Prerequisites
- Python 3.13+
- PostgreSQL 12+
- Git
- Docker & Docker Compose (optional)

### 1. Clone Repository
```bash
git clone https://github.com/shoukat-khan/Multi-Tenant-Task-Management-Platform-Backend-Only-.git
cd Multi-Tenant-Task-Management-Platform-Backend-Only-
```

### 2. Virtual Environment Setup
```bash
# Create virtual environment
python -m venv .venv

# Activate virtual environment
# Windows
.venv\Scripts\activate
# Linux/Mac
source .venv/bin/activate
```

### 3. Install Dependencies
```bash
pip install -r requirements.txt
```

### 4. Environment Configuration
```bash
# Copy environment template
cp .env.example .env

# Configure your settings in .env
DATABASE_URL=postgresql://user:pass@localhost:5432/dbname
SECRET_KEY=your-secret-key-here
DEBUG=True
```

### 5. Database Setup
```bash
# Run migrations
python manage.py migrate

# Create superuser
python manage.py createsuperuser
```

### 6. Start Development Server
```bash
python manage.py runserver
```

🎉 **Your application is now running at http://127.0.0.1:8000/**

## 📚 API Documentation

### 🔗 **Live API Documentation**
- **Swagger UI**: http://127.0.0.1:8000/api/schema/swagger-ui/
- **ReDoc**: http://127.0.0.1:8000/api/schema/redoc/
- **OpenAPI Schema**: http://127.0.0.1:8000/api/schema/

### 🛡️ **Authentication Endpoints**
```
POST   /api/auth/register/           # User registration
POST   /api/auth/login/              # Login (get tokens)
POST   /api/auth/logout/             # Logout (blacklist token)
POST   /api/auth/refresh/            # Refresh access token
GET    /api/auth/profile/            # Get user profile
PUT    /api/auth/profile/            # Update user profile
POST   /api/auth/change-password/    # Change password
```

### 👥 **User Management Endpoints**
```
GET    /api/users/                   # List users (admin/manager)
GET    /api/users/{id}/              # Get user details
PUT    /api/users/{id}/              # Update user (admin)
DELETE /api/users/{id}/              # Delete user (admin)
POST   /api/users/{id}/assign-role/  # Assign role (admin)
```

### 🏢 **Team Management Endpoints**
```
GET    /api/teams/                   # List teams
POST   /api/teams/                   # Create team (manager+)
GET    /api/teams/{id}/              # Get team details
PUT    /api/teams/{id}/              # Update team (manager+)
DELETE /api/teams/{id}/              # Delete team (admin)
POST   /api/teams/{id}/members/      # Add team member (manager+)
DELETE /api/teams/{id}/members/{uid}/# Remove team member (manager+)
```

### 📊 **Project Management Endpoints**
```
GET    /api/projects/                # List projects
POST   /api/projects/                # Create project (manager+)
GET    /api/projects/{id}/           # Get project details
PUT    /api/projects/{id}/           # Update project (manager+)
DELETE /api/projects/{id}/           # Delete project (admin)
GET    /api/projects/{id}/tasks/     # Get project tasks
```

### ✅ **Task Management Endpoints**
```
GET    /api/tasks/                   # List tasks
POST   /api/tasks/                   # Create task (manager+)
GET    /api/tasks/{id}/              # Get task details
PUT    /api/tasks/{id}/              # Update task
DELETE /api/tasks/{id}/              # Delete task (creator/admin)
POST   /api/tasks/{id}/comments/     # Add comment
POST   /api/tasks/{id}/attachments/  # Upload attachment
```

## 🧪 Testing

### Run Test Suite
```bash
# Run all tests
python manage.py test

# Run with pytest
pytest

# Run with coverage
pytest --cov=Services --cov-report=html

# Run specific test categories
pytest tests/test_authentication.py
pytest tests/test_permissions.py
pytest tests/test_api_endpoints.py
```

### Test Categories
- ✅ **Authentication Tests**: Login, registration, JWT tokens
- ✅ **Permission Tests**: Role-based access control
- ✅ **API Endpoint Tests**: CRUD operations for all models
- ✅ **Integration Tests**: End-to-end workflow testing
- ✅ **Model Tests**: Data validation and constraints

### Test Coverage
Current test coverage: **95%+**

## 📁 Project Structure

```
Multi-Tenant-Task-Management-Platform/
├── 📁 Services/                    # Main Django project
│   ├── 📁 authentication/         # Authentication app
│   │   ├── models.py              # Auth models
│   │   ├── serializers.py         # API serializers
│   │   ├── views.py               # API endpoints
│   │   ├── permissions.py         # Custom permissions
│   │   └── utils.py               # Auth utility functions
│   ├── 📁 users/                  # User management
│   ├── 📁 teams/                  # Team management
│   ├── 📁 projects/               # Project management
│   ├── 📁 tasks/                  # Task management
│   ├── settings.py                # Django configuration
│   ├── urls.py                    # URL routing
│   └── wsgi.py                    # WSGI application
├── 📁 tests/                      # Test suite
│   ├── test_authentication.py     # Auth tests
│   ├── test_permissions.py        # Permission tests
│   ├── test_models.py             # Model tests
│   ├── test_serializers.py        # Serializer tests
│   ├── test_views.py              # View tests
│   ├── factories.py               # Test data factories
│   └── conftest.py                # Pytest configuration
├── 📁 media/                      # User uploads
├── 📁 staticfiles/               # Static files
├── 🐳 Dockerfile                 # Docker configuration
├── 🐳 docker-compose.yml         # Multi-service setup
├── ⚙️ requirements.txt           # Python dependencies
├── ⚙️ .env.example              # Environment template
├── 📚 README.md                  # This file
└── 🔧 manage.py                  # Django management script
```

## 🔧 Configuration

### Environment Variables
```env
# Database Configuration
DATABASE_URL=postgresql://user:pass@localhost:5432/dbname

# Django Settings
SECRET_KEY=your-super-secret-key-here
DEBUG=False
ALLOWED_HOSTS=localhost,127.0.0.1,yourdomain.com

# JWT Settings
JWT_ACCESS_TOKEN_LIFETIME=15  # minutes
JWT_REFRESH_TOKEN_LIFETIME=7  # days

# Email Configuration (optional)
EMAIL_HOST=smtp.gmail.com
EMAIL_PORT=587
EMAIL_USE_TLS=True
EMAIL_HOST_USER=your-email@gmail.com
EMAIL_HOST_PASSWORD=your-app-password

# File Upload Settings
MAX_UPLOAD_SIZE=10485760  # 10MB
```

### Django Settings Features
- ✅ **Security Headers**: Secure headers configuration
- ✅ **CORS Configuration**: Cross-origin resource sharing
- ✅ **Database Optimization**: Connection pooling and query optimization
- ✅ **Static Files**: WhiteNoise for production static file serving
- ✅ **Logging**: Comprehensive logging configuration
- ✅ **Cache Configuration**: Redis cache support (configurable)

## 📊 Performance & Monitoring

### Performance Features
- ✅ **Database Query Optimization**: Efficient ORM queries
- ✅ **Pagination**: API response pagination
- ✅ **Filtering & Search**: Advanced filtering capabilities
- ✅ **Caching**: Redis cache integration (configurable)
- ✅ **Static File Optimization**: Compressed and cached static files

### Monitoring
- ✅ **Health Check Endpoint**: `/health/`
- ✅ **Database Health Check**: PostgreSQL connection monitoring
- ✅ **Application Logging**: Structured logging with levels
- ✅ **Error Tracking**: Comprehensive error handling and logging

### Docker Health Checks
```dockerfile
HEALTHCHECK --interval=30s --timeout=30s --start-period=5s --retries=3 \
    CMD python manage.py check --deploy || exit 1
```

## 🚀 Deployment Options

### 1. **Local Development**
```bash
python manage.py runserver
# Access: http://127.0.0.1:8000/
```

### 2. **Docker Development**
```bash
docker-compose up -d
# Access: http://localhost:8000/
```

### 3. **Production Deployment**
```bash
# Build production image
docker build -t task-management:prod .

# Deploy with Docker Compose
docker-compose -f docker-compose.prod.yml up -d
```

### 4. **Cloud Deployment Ready**
- ✅ **AWS ECS/Fargate**: Container-ready
- ✅ **Google Cloud Run**: Serverless deployment
- ✅ **Azure Container Instances**: Cloud container deployment
- ✅ **Heroku**: Platform-as-a-Service deployment
- ✅ **DigitalOcean App Platform**: Modern cloud deployment

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 👨‍💻 Developer

**Shoukat Khan**
- GitHub: [@shoukat-khan](https://github.com/shoukat-khan)
- LinkedIn: [shoukat-khan](https://linkedin.com/in/shoukat-khan)

## 📞 Support

For support and questions:
- 📧 **Email**: shoukat.khang71@gmail.com
- 🐛 **Issues**: [GitHub Issues](https://github.com/shoukat-khan/Multi-Tenant-Task-Management-Platform-Backend-Only-/issues)
- 📖 **Documentation**: [Project Wiki](https://github.com/shoukat-khan/Multi-Tenant-Task-Management-Platform-Backend-Only-/wiki)

---

<div align="center">
  <strong>Built with ❤️ using Django REST Framework</strong>
  <br>
  <em>A comprehensive solution for modern task management</em>
</div>

---

## 🎯 What's Next?

### Future Enhancements (Week 7+)
- [ ] **Frontend Integration**: React/Vue.js frontend application
- [ ] **Real-time Features**: WebSocket integration for live updates
- [ ] **Mobile API**: Mobile-optimized API endpoints
- [ ] **Analytics Dashboard**: Project and team analytics
- [ ] **Notification System**: Email and push notifications
- [ ] **File Storage**: AWS S3/Google Cloud Storage integration
- [ ] **API Rate Limiting**: Advanced throttling and quota management
- [ ] **Audit Logging**: Comprehensive audit trail system
