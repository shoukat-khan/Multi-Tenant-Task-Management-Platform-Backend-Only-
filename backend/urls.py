from rest_framework.routers import DefaultRouter #DefaultRouter is a router that is used to handle the URLs for the API
from .views import UserViewSet, TeamViewSet #UserViewSet and TeamViewSet are the views that are used to handle the HTTP requests and responses for the API
from django.urls import path, include  

router = DefaultRouter()
router.register(r'users', UserViewSet)
router.register(r'teams', TeamViewSet)

urlpatterns = [
    path('', include(router.urls)),
] 