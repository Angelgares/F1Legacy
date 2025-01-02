import os, sys, django
from django.shortcuts import render, redirect

from f1legacy.scripts.scrapping import get_teams, get_drivers, calculate_age, get_driver_standings, get_team_standings, get_grand_prixes

sys.path.append(os.path.dirname(os.path.abspath(__file__)))
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "f1legacy_project.settings")
django.setup()

from f1legacy.models import Driver, Team, DriverStanding, TeamStanding
from whoosh.qparser import QueryParser
from f1legacy.scripts.whoosh_index import create_indexes, get_driver_index, get_team_index


def index(request):
    return render(request, "index.html")


def drivers_view(request):
    query = request.GET.get("q", "")
    driver_results = []

    if query:
        index = get_driver_index()
        with index.searcher() as searcher:
            parser = QueryParser("name", index.schema)
            whoosh_query = parser.parse(query)
            results = searcher.search(whoosh_query, limit=None)
            driver_results = [Driver.objects.get(id=result["id"]) for result in results]
    else:
        driver_results = Driver.objects.all()

    return render(request, "drivers.html", {"drivers": driver_results, "query": query})


def teams_view(request):
    query = request.GET.get("q", "")
    team_results = []

    if query:
        index = get_team_index()
        with index.searcher() as searcher:
            parser = QueryParser("name", index.schema)
            whoosh_query = parser.parse(query)
            results = searcher.search(whoosh_query, l)
            team_results = [Team.objects.get(id=result["id"]) for result in results]
    else:
        team_results = Team.objects.all()

    return render(request, "teams.html", {"teams": team_results, "query": query})


def load_data(request):
    try:
        start_year = int(request.GET.get("start_year", 2024))
        end_year = int(request.GET.get("end_year", 2024))

        create_indexes()
        get_teams()
        get_drivers()
        get_driver_standings(start_year, end_year)
        get_team_standings(start_year, end_year)
        get_grand_prixes(start_year, end_year)

        return redirect("/?data_loaded=true")

    except ValueError:
        return redirect("/?bad_year_format=true")

def driver_standings(request):
    return render(request, "driver_standings.html", {"driver_standings": DriverStanding.objects.all()})

def team_standings(request):
    return render(request, "team_standings.html", {"team_standings": TeamStanding.objects.all()})

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
