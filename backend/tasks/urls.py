from django.urls import path
from .views import hello


app_name = 'tasks'

urlpatterns = [
    path('',hello)
]
