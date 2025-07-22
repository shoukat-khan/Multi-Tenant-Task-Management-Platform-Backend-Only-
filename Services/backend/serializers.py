from rest_framework import serializers
from .models import User, Team

class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['id', 'username', 'email', 'first_name', 'last_name']

class TeamSerializer(serializers.ModelSerializer):   #serializers are used to convert model instances to JSON so that the frontend can use them
    members = UserSerializer(many=True, read_only=True)
    class Meta:
        model = Team
        fields = ['id', 'name', 'members', 'created_at'] 