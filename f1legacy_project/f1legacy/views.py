from django.shortcuts import render

def index(request):
    return render(request, 'index.html')

def drivers_view(request):
    return render(request, 'drivers.html')

def teams_view(request):
    return render(request, 'teams.html')