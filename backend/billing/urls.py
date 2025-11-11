from django.urls import path
from .views import status_view, subscribe_view

app_name = "billing"

urlpatterns = [
	path("status/", status_view, name="status"),
	path("subscribe/", subscribe_view, name="subscribe"),
]


