import os, sys, django
from django.shortcuts import render, redirect
from django.db import transaction
from django.db.models import Case, When, Value, IntegerField, F
from datetime import datetime

from f1legacy.scripts.scrapping import get_teams, get_drivers, calculate_age, get_driver_standings, get_team_standings, get_grand_prixes, set_fastest_lap, assign_diff_positions

sys.path.append(os.path.dirname(os.path.abspath(__file__)))
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "f1legacy_project.settings")
django.setup()

from f1legacy.models import Driver, Team, GrandPrix, StartingGrid, RaceResult
from whoosh.qparser import MultifieldParser
from whoosh.query import Term, NumericRange
from whoosh.sorting import FieldFacet
from whoosh.index import EmptyIndexError
from f1legacy.scripts.whoosh_index import create_indexes, get_driver_index, get_team_index, get_driver_standings_index, get_team_standings_index

def index(request):
    return render(request, "index.html")


def drivers_view(request):
    query = request.GET.get("q", "").strip()
    number = request.GET.get("number", "").strip()
    championships = request.GET.get("championships", "").strip()
    races = request.GET.get("races", "").strip()
    victories = request.GET.get("victories", "").strip()

    filters_applied = any([query, number, championships, races, victories])

    try:
        index = get_driver_index()
        parser = MultifieldParser(["name", "number", "championships", "races", "victories"], index.schema)
        filters = build_driver_filters(query, number, championships, races, victories, parser)

        if filters_applied:
            driver_results = get_driver_results_from_index(index, filters)
        else:
            driver_results = get_driver_results_from_db()
    except (EmptyIndexError, FileNotFoundError):
        driver_results = [] if filters_applied else get_driver_results_from_db()

    return render(request, "drivers.html", {
        "drivers": driver_results,
        "query": query,
        "request": request,
    })

def teams_view(request):
    query = request.GET.get("q", "").strip()
    championships = request.GET.get("championships", "").strip()
    victories = request.GET.get("victories", "").strip()

    filters_applied = any([query, championships, victories])

    try:
        index = get_team_index()
        parser = MultifieldParser(["name", "championships", "victories"], index.schema)
        filters = build_team_filters(query, championships, victories, parser)
        
        if filters_applied:
            team_results = get_team_results_from_index(index, filters)
        else:
            team_results = get_team_results_from_db()
    except (EmptyIndexError, FileNotFoundError):
        team_results = [] if filters_applied else get_team_results_from_db()

    return render(request, "teams.html", {
        "teams": team_results,
        "query": query,
        "request": request,
    })

@transaction.atomic
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
    selected_driver = request.GET.get("driver")
    sort_field = request.GET.get("sort", "position")
    sort_order = request.GET.get("order", "asc")

    valid_fields = ["position", "name", "car"]
    if sort_field not in valid_fields:
        sort_field = "position"

    sort_direction = sort_order == "desc"

    try:
        index = get_driver_standings_index()
        results = []
        with index.searcher() as searcher:
            parser = MultifieldParser(["name", "car", "year", "position"], schema=index.schema)
            query = None

            if selected_driver:
                query = parser.parse(f'name:"{selected_driver}"')
            elif selected_year:
                query = parser.parse(f'year:{selected_year}')

            if query:
                search_results = searcher.search(query, limit=None)
                for result in search_results:
                    position = result["position"] if result["position"] != 0 else float('inf')
                    results.append({
                        "id": result["id"],
                        "name": result["name"],
                        "car": result["car"],
                        "year": result["year"],
                        "position": position,
                        "points": result["points"],
                    })

        if sort_field == "car":
            results.sort(key=lambda x: x["car"].lower(), reverse=sort_direction)
        elif sort_field == "name":
            results.sort(key=lambda x: x["name"].lower(), reverse=sort_direction)
        else:  
            results.sort(key=lambda x: (x["position"] if x["position"] != float('inf') else float('inf')), reverse=sort_direction)

        years = set()
        drivers = set()

        with index.searcher() as searcher:
            all_results = searcher.search(parser.parse("*"), limit=None)
            for result in all_results:
                years.add(result["year"])
                drivers.add(result["name"])

        years = sorted(years, reverse=True)
        drivers = sorted(drivers)

    except (EmptyIndexError, FileNotFoundError):
        results = []
        years = []
        drivers = []

    return render(request, "driver_standings.html", {
        "driver_standings": results if selected_year or selected_driver else [],
        "years": years,
        "drivers": drivers,
        "current_sort": sort_field,
        "current_order": sort_order,
    })



def team_standings(request):
    selected_year = request.GET.get("year")
    selected_team = request.GET.get("team")
    sort_field = request.GET.get("sort", "position")
    sort_order = request.GET.get("order", "asc")

    valid_fields = ["position", "name"]
    if sort_field not in valid_fields:
        sort_field = "position"

    sort_direction = sort_order == "desc"

    try:
        index = get_team_standings_index()
        results = []
        with index.searcher() as searcher:
            parser = MultifieldParser(["name", "year", "position"], schema=index.schema)
            query = None

            if selected_team:
                query = parser.parse(f'name:"{selected_team}"')
            elif selected_year:
                query = parser.parse(f'year:{selected_year}')

            if query:
                search_results = searcher.search(query, limit=None)
                for result in search_results:
                    position = result["position"] if result["position"] != 0 else float('inf')
                    results.append({
                        "id": result["id"],
                        "name": result["name"],
                        "year": result["year"],
                        "position": position,
                        "points": result["points"],
                    })

        reverse = sort_direction
        results.sort(key=lambda x: (x["position"] if x["position"] != float('inf') else float('inf')), reverse=reverse)

        years = set()
        teams = set()

        with index.searcher() as searcher:
            all_results = searcher.search(parser.parse("*"), limit=None)
            for result in all_results:
                years.add(result["year"])
                teams.add(result["name"])

        years = sorted(years, reverse=True)
        teams = sorted(teams)

    except (EmptyIndexError, FileNotFoundError):
        results = []
        years = []
        teams = []

    return render(request, "team_standings.html", {
        "team_standings": results if selected_year or selected_team else [],
        "years": years,
        "teams": teams,
        "current_sort": sort_field,
        "current_order": sort_order,
    })


def driver_detail(request, id):
    try:
        index = get_driver_index()
        filters = [Term("id", str(id))]
        driver_results = get_driver_results_from_index(index, filters)
        driver = driver_results[0] if driver_results else None
    except Exception as e:
        print(f"Error accessing driver index: {e}")
        driver = None

    if not driver:
        drivers_from_db = get_driver_results_from_db()
        driver = next((d for d in drivers_from_db if d["id"] == str(id)), None)

    if driver and driver.get("birth_date"):
        driver["age"] = calculate_age(datetime.strptime(driver["birth_date"], "%Y-%m-%d").strftime("%d/%m/%Y"))
        driver["birth_date"] = datetime.strptime(driver["birth_date"], "%Y-%m-%d").strftime("%d/%m/%Y")
    else:
        driver["age"] = None

    return render(request, "driver_detail.html", {"driver": driver})

def team_detail(request, id):
    try:
        index = get_team_index()
        filters = [Term("id", str(id))]
        team_results = get_team_results_from_index(index, filters)
        team = team_results[0] if team_results else None
    except Exception as e:
        print(f"Error accessing team index: {e}")
        team = None

    if not team:
        teams_from_db = get_team_results_from_db()
        team = next((t for t in teams_from_db if t["id"] == str(id)), None)

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

def build_driver_filters(query, number, championships, races, victories, parser):
    filters = []
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
    return filters

def build_team_filters(query, championships, victories, parser):
    filters = []
    if query:
        filters.append(parser.parse(query))
    if championships:
        filters.append(NumericRange("championships", int(championships), None))
    if victories:
        filters.append(NumericRange("victories", int(victories), None))
    return filters


def get_driver_results_from_index(index, filters):
    with index.searcher() as searcher:
        if not filters:
            return []
        final_query = filters[0]
        for filter_query in filters[1:]:
            final_query &= filter_query
        results = searcher.search(final_query, limit=None)
        return [
            {
                "id": result.get("id"),
                "name": result.get("name"),
                "number": result.get("number"),
                "country": result.get("country"),
                "country_flag": result.get("country_flag"),
                "team": result.get("team"),
                "birth_date": result.get("birth_date"),
                "points": result.get("points"),
                "podiums": result.get("podiums"),
                "championships": result.get("championships"),
                "races": result.get("races"),
                "victories": result.get("victories"),
                "image": result.get("image"),
            }
            for result in results
        ]

def get_team_results_from_index(index, filters):
    if not filters:
        return []

    final_query = filters[0]
    for filter_query in filters[1:]:
        final_query &= filter_query

    with index.searcher() as searcher:
        results = searcher.search(final_query, limit=None)
        return [
            {
                "id": result["id"],
                "name": result["name"],
                "base": result.get("base"),
                "team_principal": result.get("team_principal"),
                "chassis": result.get("chassis"),
                "power_unit": result.get("power_unit"),
                "championships": result.get("championships"),
                "victories": result.get("victories"),
                "pole_positions": result.get("pole_positions"),
                "fastest_laps": result.get("fastest_laps"),
                "image": result.get("image"),
            }
            for result in results
        ]

def get_driver_results_from_db():
    return [
        {
            "id": str(driver.id),
            "name": driver.name,
            "number": driver.number,
            "country": driver.country,
            "country_flag": driver.country_flag,
            "team": str(driver.team.id) if driver.team else None,
            "birth_date": driver.birth_date.strftime("%d-%m-%Y") if driver.birth_date else None,
            "points": driver.points,
            "podiums": driver.podiums,
            "championships": driver.championships,
            "races": driver.races,
            "victories": driver.victories,
            "image": driver.image,
        }
        for driver in Driver.objects.all()
    ]

def get_team_results_from_db():
    return [
        {
            "id": str(team.id),
            "name": team.name,
            "base": team.base,
            "team_principal": team.team_principal,
            "chassis": team.chassis,
            "power_unit": team.power_unit,
            "championships": team.championships,
            "victories": team.victories,
            "pole_positions": team.pole_positions,
            "fastest_laps": team.fastest_laps,
            "image": team.image,
        }
        for team in Team.objects.all()
    ]