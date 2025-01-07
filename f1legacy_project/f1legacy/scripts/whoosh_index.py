import os, shutil
from whoosh.fields import Schema, TEXT, ID, NUMERIC
from whoosh.index import create_in, open_dir, EmptyIndexError
from whoosh.analysis import NgramWordAnalyzer

driver_schema = Schema(
    id=ID(stored=True, unique=True),
    name=TEXT(stored=True, analyzer=NgramWordAnalyzer(minsize=2)),
    number=NUMERIC(stored=True, numtype=int),
    country=TEXT(stored=True),
    country_flag=TEXT(stored=True),
    team=ID(stored=True),
    birth_date=TEXT(stored=True),
    points=NUMERIC(stored=True, numtype=float),
    podiums=NUMERIC(stored=True, numtype=int),
    championships=NUMERIC(stored=True, numtype=int),
    races=NUMERIC(stored=True, numtype=int),
    victories=NUMERIC(stored=True, numtype=int),
    image=TEXT(stored=True),
)

team_schema = Schema(
    id=ID(stored=True, unique=True),
    name=TEXT(stored=True, analyzer=NgramWordAnalyzer(minsize=2)),
    base=TEXT(stored=True),
    team_principal=TEXT(stored=True),
    chassis=TEXT(stored=True),
    power_unit=TEXT(stored=True),
    championships=NUMERIC(stored=True, numtype=int),
    victories=NUMERIC(stored=True, numtype=int),
    pole_positions=NUMERIC(stored=True, numtype=int),
    fastest_laps=NUMERIC(stored=True, numtype=int),
    image=TEXT(stored=True),
)

driver_standings_schema = Schema(
    id=ID(stored=True, unique=True),
    name=TEXT(stored=True),
    car=TEXT(stored=True),
    year=NUMERIC(stored=True, numtype=int),
    position=NUMERIC(stored=True, numtype=int),
    points=NUMERIC(stored=True, numtype=float),
)

team_standings_schema = Schema(
    id=ID(stored=True, unique=True),
    name=TEXT(stored=True),
    year=NUMERIC(stored=True, numtype=int),
    position=NUMERIC(stored=True, numtype=int),
    points=NUMERIC(stored=True, numtype=float),
)

grand_prix_schema = Schema(
    id=ID(stored=True, unique=True),
    name=TEXT(stored=True),
    location=TEXT(stored=True),
    start_date=TEXT(stored=True),
    end_date=TEXT(stored=True),
)

starting_grid_schema = Schema(
    id=ID(stored=True, unique=True),
    grand_prix=ID(stored=True),
    driver=TEXT(stored=True),
    car=TEXT(stored=True),
    position=NUMERIC(stored=True, numtype=int),
    lap_time=TEXT(stored=True),
)

race_result_schema = Schema(
    id=ID(stored=True, unique=True),
    starting_grid=ID(stored=True),
    position=NUMERIC(stored=True, numtype=int),
    laps_completed=NUMERIC(stored=True, numtype=int),
    total_time=TEXT(stored=True),
    points=NUMERIC(stored=True, numtype=float),
)

INDEX_DIR = "whoosh_indexes"

def create_indexes():
    if os.path.exists(INDEX_DIR):
        shutil.rmtree(INDEX_DIR)
    
    os.makedirs(INDEX_DIR)
    
    team_index_path = os.path.join(INDEX_DIR, "teams")
    os.mkdir(team_index_path)
    team_index = create_in(team_index_path, team_schema)
    add_team_data(team_index)
    
    driver_index_path = os.path.join(INDEX_DIR, "drivers")
    os.mkdir(driver_index_path)
    driver_index = create_in(driver_index_path, driver_schema)
    add_driver_data(driver_index)

    driver_standings_index_path = os.path.join(INDEX_DIR, "driver_standings")
    os.mkdir(driver_standings_index_path)
    driver_standings_index = create_in(driver_standings_index_path, driver_standings_schema)
    add_driver_data(driver_standings_index)

    team_standings_index_path = os.path.join(INDEX_DIR, "team_standings")
    os.mkdir(team_standings_index_path)
    team_standings_index = create_in(team_standings_index_path, team_standings_schema)
    add_team_data(team_standings_index)
    
    grand_prix_index_path = os.path.join(INDEX_DIR, "grand_prix")
    os.mkdir(grand_prix_index_path)
    grand_prix_index = create_in(grand_prix_index_path, grand_prix_schema)
    add_grand_prix_data(grand_prix_index)

    starting_grid_index_path = os.path.join(INDEX_DIR, "starting_grid")
    os.mkdir(starting_grid_index_path)
    starting_grid_index = create_in(starting_grid_index_path, starting_grid_schema)
    add_starting_grid_data(starting_grid_index)

    race_result_index_path = os.path.join(INDEX_DIR, "race_result")
    os.mkdir(race_result_index_path)
    race_result_index = create_in(race_result_index_path, race_result_schema)
    add_race_result_data(race_result_index)

def add_driver_data(index):
    """Indexes Driver data in Whoosh."""
    from f1legacy.models import Driver
    writer = index.writer()
    for driver in Driver.objects.all():
        writer.add_document(
            id=str(driver.id),
            name=driver.name,
            number=driver.number if driver.number else None,
            country=driver.country if driver.country else None,
            country_flag=driver.country_flag if driver.country_flag else None,
            team=str(driver.team.id) if driver.team else None,
            birth_date=driver.birth_date.strftime("%d-%m-%Y") if driver.birth_date else None,
            points=driver.points if driver.points else None,
            podiums=driver.podiums if driver.podiums else None,
            championships=driver.championships if driver.championships else None,
            races=driver.races if driver.races else None,
            victories=driver.victories if driver.victories else None,
            image=driver.image if driver.image else None,
        )
    writer.commit()

def add_team_data(index):
    """Indexes Team data in Whoosh."""
    from f1legacy.models import Team
    writer = index.writer()
    for team in Team.objects.all():
        writer.add_document(
            id=str(team.id),
            name=team.name,
            base=team.base,
            team_principal=team.team_principal,
            chassis=team.chassis,
            power_unit=team.power_unit,
            championships=team.championships,
            victories=team.victories,
            pole_positions=team.pole_positions,
            fastest_laps=team.fastest_laps,
            image=team.image,
        )
    writer.commit()

def add_driver_standings_data(index):
    """Indexes Driver Standings data in Whoosh."""
    from f1legacy.models import DriverStanding
    writer = index.writer()
    for driver_standing in DriverStanding.objects.all():
        writer.add_document(
            id=str(driver_standing.id),
            name=driver_standing.name,
            car=driver_standing.car,
            year=driver_standing.year,
            position=driver_standing.position,
            points=driver_standing.points,
        )
    writer.commit()

def add_team_standings_data(index):
    """Indexes Team Standings data in Whoosh."""
    from f1legacy.models import TeamStanding
    writer = index.writer()
    for team_standing in TeamStanding.objects.all():
        writer.add_document(
            id=str(team_standing.id),
            name=team_standing.name,
            year=team_standing.year,
            position=team_standing.position,
            points=team_standing.points,
        )
    writer.commit()

def add_grand_prix_data(index):
    """Indexes Grand Prix data in Whoosh."""
    from f1legacy.models import GrandPrix
    writer = index.writer()
    for grand_prix in GrandPrix.objects.all():
        writer.add_document(
            id=str(grand_prix.id),
            name=grand_prix.name,
            location=grand_prix.location,
            start_date=grand_prix.start_date.strftime("%d-%m-%Y"),
            end_date=grand_prix.end_date.strftime("%d-%m-%Y"),
        )
    writer.commit()

def add_starting_grid_data(index):
    """Indexes Starting Grid data in Whoosh."""
    from f1legacy.models import StartingGrid
    writer = index.writer()
    for starting_grid in StartingGrid.objects.all():
        writer.add_document(
            id=str(starting_grid.id),
            grand_prix=str(starting_grid.grand_prix.id),
            driver=starting_grid.driver,
            car=starting_grid.car,
            position=starting_grid.position,
            lap_time=starting_grid.lap_time,
        )
    writer.commit()

def add_race_result_data(index):
    """Indexes Race Result data in Whoosh."""
    from f1legacy.models import RaceResult
    writer = index.writer()
    for race_result in RaceResult.objects.all():
        writer.add_document(
            id=str(race_result.id),
            starting_grid=str(race_result.starting_grid.id),
            position=race_result.position,
            laps_completed=race_result.laps_completed,
            total_time=race_result.total_time,
            points=race_result.points,
        )
    writer.commit()

def get_driver_index():
    """Returns the driver index or creates it if it does not exist."""
    driver_index_path = os.path.join(INDEX_DIR, "drivers")
    try:
        return open_dir(driver_index_path)
    except EmptyIndexError:
        create_in(driver_index_path, driver_schema)
        return open_dir(driver_index_path)

def get_team_index():
    """Returns the team index or creates it if it does not exist."""
    team_index_path = os.path.join(INDEX_DIR, "teams")
    try:
        return open_dir(team_index_path)
    except EmptyIndexError:
        create_in(team_index_path, team_schema)
        return open_dir(team_index_path)

def get_driver_standings_index():
    """Returns the driver_standings index or creates it if it does not exist."""
    driver_standings_index_path = os.path.join(INDEX_DIR, "driver_standings")
    try:
        return open_dir(driver_standings_index_path)
    except EmptyIndexError:
        create_in(driver_standings_index_path, driver_standings_schema)
        return open_dir(driver_standings_index_path)
    
def get_team_standings_index():
    """Returns the team_standings index or creates it if it does not exist."""
    team_standings_index_path = os.path.join(INDEX_DIR, "team_standings")
    try:
        return open_dir(team_standings_index_path)
    except EmptyIndexError:
        create_in(team_standings_index_path, team_standings_schema)
        return open_dir(team_standings_index_path)
    
def get_grand_prix_index():
    """Returns the grand_prix index or creates it if it does not exist."""
    grand_prix_index_path = os.path.join(INDEX_DIR, "grand_prix")
    try:
        return open_dir(grand_prix_index_path)
    except EmptyIndexError:
        create_in(grand_prix_index_path, grand_prix_schema)
        return open_dir(grand_prix_index_path)
    
def get_starting_grid_index():
    """Returns the starting_grid index or creates it if it does not exist."""
    starting_grid_index_path = os.path.join(INDEX_DIR, "starting_grid")
    try:
        return open_dir(starting_grid_index_path)
    except EmptyIndexError:
        create_in(starting_grid_index_path, starting_grid_schema)
        return open_dir(starting_grid_index_path)
    
def get_race_result_index():
    """Returns the race_result index or creates it if it does not exist."""
    get_race_result_index_path = os.path.join(INDEX_DIR, "race_result")
    try:
        return open_dir(get_race_result_index_path)
    except EmptyIndexError:
        create_in(get_race_result_index_path, race_result_schema)
        return open_dir(get_race_result_index_path)