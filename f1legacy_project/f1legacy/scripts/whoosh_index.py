import os, shutil
from whoosh.fields import Schema, TEXT, ID, NUMERIC
from whoosh.index import create_in, open_dir, EmptyIndexError
from whoosh.analysis import NgramWordAnalyzer
from django.db import transaction

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

INDEX_DIR = "whoosh_indexes"

@transaction.atomic
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
    add_driver_standings_data(driver_standings_index)

    team_standings_index_path = os.path.join(INDEX_DIR, "team_standings")
    os.mkdir(team_standings_index_path)
    team_standings_index = create_in(team_standings_index_path, team_standings_schema)
    add_team_standings_data(team_standings_index)

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
            points=driver.points,
            podiums=driver.podiums,
            championships=driver.championships,
            races=driver.races if driver.races else None,
            victories=driver.victories,
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
            base=team.base if team.base else None,
            team_principal=team.team_principal if team.team_principal else None,
            chassis=team.chassis if team.chassis else None,
            power_unit=team.power_unit if team.power_unit else None,
            championships=team.championships,
            victories=team.victories if team.victories else None,
            pole_positions=team.pole_positions if team.pole_positions else None,
            fastest_laps=team.fastest_laps if team.fastest_laps else None,
            image=team.image if team.image else None,
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