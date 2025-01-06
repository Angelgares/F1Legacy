import os, sys, django
from django.shortcuts import render, redirect
from django.db.models import Case, When, Value, IntegerField, F

from f1legacy.scripts.scrapping import get_teams, get_drivers, calculate_age, get_driver_standings, get_team_standings, get_grand_prixes, set_fastest_lap, assign_diff_positions

sys.path.append(os.path.dirname(os.path.abspath(__file__)))
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "f1legacy_project.settings")
django.setup()

from f1legacy.models import Driver, Team, DriverStanding, TeamStanding, GrandPrix, StartingGrid, RaceResult
from whoosh.qparser import MultifieldParser
from whoosh.query import Term, NumericRange
from whoosh.index import EmptyIndexError
from f1legacy.scripts.whoosh_index import create_indexes, get_driver_index, get_team_index

def index(request):
    return render(request, "index.html")


def drivers_view(request):
    query = request.GET.get("q", "").strip()
    number = request.GET.get("number", "").strip()
    championships = request.GET.get("championships", "").strip()
    races = request.GET.get("races", "").strip()
    victories = request.GET.get("victories", "").strip()

    driver_results = []
    filters = []
    try:
        index = get_driver_index()
        with index.searcher() as searcher:
            parser = MultifieldParser(["name", "number", "championships", "races", "victories"], index.schema)

            if query:
                filters.append(parser.parse(query))
            if number:
                filters.append(Term("number", number))
            if championships:
                filters.append(NumericRange("championships", int(championships), None))
            if races:
                filters.append(NumericRange("races", int(races), None))
            if victories:
                filters.append(NumericRange("victories", int(victories), None))

            if filters:
                final_query = filters[0]
                for filter_query in filters[1:]:
                    final_query &= filter_query

                results = searcher.search(final_query, limit=None)
                driver_results = [Driver.objects.get(id=result["id"]) for result in results]
            else:
                driver_results = Driver.objects.all()

    except EmptyIndexError:
        driver_results = Driver.objects.all()

    except FileNotFoundError:
        driver_results = Driver.objects.all()

    return render(request, "drivers.html", {
        "drivers": driver_results, 
        "query": query,
        "request": request,
    })

def teams_view(request):
    query = request.GET.get("q", "").strip()
    championships = request.GET.get("championships", "").strip()
    victories = request.GET.get("victories", "").strip()

    team_results = []
    filters = []

    try:
        index = get_team_index()
        with index.searcher() as searcher:
            parser = MultifieldParser(["name", "championships", "victories"], index.schema)

            if query:
                filters.append(parser.parse(query))
            if championships:
                filters.append(NumericRange("championships", int(championships), None))
            if victories:
                filters.append(NumericRange("victories", int(victories), None))

            if filters:
                final_query = filters[0]
                for filter_query in filters[1:]:
                    final_query &= filter_query

                results = searcher.search(final_query, limit=None)
                team_results = [Team.objects.get(id=result["id"]) for result in results]
            else:
                team_results = Team.objects.all()

    except EmptyIndexError:
        team_results = Team.objects.all()

    except FileNotFoundError:
        team_results = Team.objects.all()

    return render(request, "teams.html", {
        "teams": team_results, 
        "query": query,
        "request": request,
    })

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
    selected_year = request.GET.get("year")
    sort_field = request.GET.get("sort", "position")  
    sort_order = request.GET.get("order", "asc")  
    
    valid_fields = ["position", "name", "car"] 
    if sort_field not in valid_fields:
        sort_field = "position"

    sort_direction = "" if sort_order == "asc" else "-"

    if selected_year:
        standings = (
            DriverStanding.objects.filter(year=selected_year)
            .annotate(
                adjusted_position=Case(
                    When(position=0, then=Value(9999)),
                    default="position",
                    output_field=IntegerField(),
                )
            )
            .order_by(f"{sort_direction}{'adjusted_position' if sort_field == 'position' else sort_field}")
        )
    else:
        standings = None

    years = DriverStanding.objects.values_list("year", flat=True).distinct().order_by("-year")

    return render(request, "driver_standings.html", {
        "driver_standings": standings,
        "years": years,
        "current_sort": sort_field.lstrip("-"),
        "current_order": sort_order,
    })

def team_standings(request):
    selected_year = request.GET.get("year")
    sort_field = request.GET.get("sort", "position")
    sort_order = request.GET.get("order", "asc")

    valid_fields = ["position", "name", "victories"]
    if sort_field not in valid_fields:
        sort_field = "position"
    
    sort_direction = "" if sort_order == "asc" else "-"
    
    if selected_year:
        standings = (
            TeamStanding.objects.filter(year=selected_year)
            .annotate(
                adjusted_position=Case(
                    When(position=0, then=Value(9999)), 
                    default="position",
                    output_field=IntegerField(),
                )
            )
            .order_by(f"{sort_direction}{'adjusted_position' if sort_field == 'position' else sort_field}")
        )
    else:
        standings = None
    
    years = TeamStanding.objects.values_list("year", flat=True).distinct().order_by("-year")

    return render(request, "team_standings.html", {
        "team_standings": standings,
        "years": years,
        "current_sort": sort_field.lstrip("-"),
        "current_order": sort_order,
    })


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

def race_results(request):
    selected_year = request.GET.get("year")

    years = (
        GrandPrix.objects.annotate(year=F("start_date__year"))
        .values_list("year", flat=True)
        .distinct()
        .order_by("-year")
    )

    if selected_year:
        try:
            selected_year = int(selected_year)
            standings = (
                GrandPrix.objects.annotate(year=F("start_date__year"))
                .filter(year=selected_year)
                .order_by("start_date")
            )
        except ValueError:
            standings = None
    else:
        standings = None

    return render(request, "race_results.html", {
        "grand_prixes": standings,
        "years": years,
        "selected_year": selected_year, 
    })

def race_results_detail(request, year, grand_prix_id):
    grand_prix = GrandPrix.objects.get(id=grand_prix_id)
    
    starting_grid = (
        StartingGrid.objects.filter(grand_prix=grand_prix_id)
        .annotate(
            adjusted_position=Case(
                When(position=0, then=Value(9999)),
                default="position",
                output_field=IntegerField(),
            )
        )
        .order_by("adjusted_position")
    )

    race_results = (
        RaceResult.objects.filter(starting_grid__grand_prix=grand_prix_id)
        .annotate(
            adjusted_position=Case(
                When(position=0, then=Value(9999)),
                default="position",
                output_field=IntegerField(),
            )
        )
        .order_by("adjusted_position")
    )

    for race_result in race_results:
        race_result.fastest_lap = set_fastest_lap(race_result)
    assign_diff_positions(starting_grid, race_results)

    return render(request, "race_results_detail.html", {
        "grand_prix": grand_prix,
        "starting_grid": starting_grid,
        "race_results": race_results,
    })
