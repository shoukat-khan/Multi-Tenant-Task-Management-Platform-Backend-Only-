"""
URL configuration for team_management project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/4.2/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin #admin is a module that is used to manage the admin site of the project and it is used to manage the models and the data in the database
from django.urls import path, include #path is a function that is used to create the URL patterns for the project and include is a function that is used to include the URL patterns of the other apps in the project

urlpatterns = [
    path('admin/', admin.site.urls),  #this model is placed in the admin site of the project and it is used to manage the models and the data in the database
    path('api/', include('backend.urls')),
]
