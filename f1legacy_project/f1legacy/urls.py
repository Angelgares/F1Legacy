from django.urls import path
from . import views

urlpatterns = [
    path('', views.index, name='index'),
    path('drivers/', views.drivers_view, name='drivers'),
    path('teams/', views.teams_view, name='teams'),
]
