import os, sys, django
from django.shortcuts import render, redirect
from django.http import HttpResponseBadRequest

from f1legacy.scripts.scrapping import get_teams, get_drivers, calculate_age, get_driver_standings, get_team_standings, get_grand_prixes

sys.path.append(os.path.dirname(os.path.abspath(__file__)))
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "f1legacy_project.settings")
django.setup()

from f1legacy.models import Driver, Team


def index(request):
    return render(request, "index.html")


def drivers_view(request):
    return render(request, "drivers.html", {"drivers": Driver.objects.all()})


def teams_view(request):
    return render(request, "teams.html", {"teams": Team.objects.all()})


def load_data(request):
    try:
        start_year = int(request.GET.get("start_year", 2024))
        end_year = int(request.GET.get("end_year", 2024))

        get_teams()
        get_drivers()
        get_driver_standings(start_year, end_year)
        get_team_standings(start_year, end_year)
        get_grand_prixes(start_year, end_year)

        return redirect("/?data_loaded=true")

    except ValueError:
        return redirect("/?bad_year_format=true")


def driver_detail(request, id):
    driver = Driver.objects.get(id=id)
    if driver.birth_date:
        driver.age = calculate_age(driver.birth_date.strftime("%d/%m/%Y"))
    else:
        driver.age = None
    return render(request, "driver_detail.html", {"driver": driver})


def team_detail(request, id):
    team = Team.objects.get(id=id)
    return render(request, "team_detail.html", {"team": team})
