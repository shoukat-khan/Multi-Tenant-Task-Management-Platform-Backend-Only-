from django.shortcuts import render
from rest_framework import viewsets    #viewsets are a way to handle HTTP requests and responses this is inside the rest framework library of django
from .models import User, Team
from .serializers import UserSerializer, TeamSerializer

# Create your views here.

class UserViewSet(viewsets.ModelViewSet):
    queryset = User.objects.all()
    serializer_class = UserSerializer

class TeamViewSet(viewsets.ModelViewSet):
    queryset = Team.objects.all()
    serializer_class = TeamSerializer
