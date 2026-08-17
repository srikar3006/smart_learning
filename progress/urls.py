from django.urls import path
from . import views

app_name = 'progress'

urlpatterns = [
    path('', views.progress_dashboard, name='dashboard'),
    path('api/summary/', views.api_progress_summary, name='api_summary'),
]
