from django.urls import path
from . import views

urlpatterns = [
    path('', views.index, name='index'),
    path('drivers/', views.drivers_view, name='drivers'),
    path('teams/', views.teams_view, name='teams'),
    path('load_data/', views.load_data, name='load_data'),
    path('drivers/<int:id>/', views.driver_detail, name='driver_detail'),
    path('teams/<int:id>/', views.team_detail, name='team_detail'),
]
