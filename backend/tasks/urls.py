from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import TaskViewSet, TaskTemplateViewSet


app_name = 'tasks'

router = DefaultRouter()
# Register templates first (more specific routes should come before generic ones)
router.register(r'templates', TaskTemplateViewSet, basename='template')
router.register(r'', TaskViewSet, basename='task')

urlpatterns = [
    path('', include(router.urls)),
]
