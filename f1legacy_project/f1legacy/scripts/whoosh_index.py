import os
from whoosh.fields import Schema, TEXT, ID, NUMERIC
from whoosh.index import create_in, open_dir, EmptyIndexError
from whoosh.analysis import NgramWordAnalyzer

# Define el esquema del índice para Drivers
driver_schema = Schema(
    id=ID(stored=True, unique=True),
    name=TEXT(stored=True, analyzer=NgramWordAnalyzer(minsize=2)),
    number=NUMERIC(stored=True, numtype=int),
    team=TEXT(stored=True),
    championships=NUMERIC(stored=True, numtype=int),
    races=NUMERIC(stored=True, numtype=int),
    victories=NUMERIC(stored=True, numtype=int),
)

# Define el esquema del índice para Teams
team_schema = Schema(
    id=ID(stored=True, unique=True),
    name=TEXT(stored=True, analyzer=NgramWordAnalyzer(minsize=2)),
    championships=NUMERIC(stored=True, numtype=int),
    victories=NUMERIC(stored=True, numtype=int),
)

INDEX_DIR = "whoosh_indexes"

def create_indexes():
    if not os.path.exists(INDEX_DIR):
        os.makedirs(INDEX_DIR)
    
    team_index_path = os.path.join(INDEX_DIR, "teams")
    if not os.path.exists(team_index_path):
        os.mkdir(team_index_path)
        team_index = create_in(team_index_path, team_schema)
        add_team_data(team_index)
    
    driver_index_path = os.path.join(INDEX_DIR, "drivers")
    if not os.path.exists(driver_index_path):
        os.mkdir(driver_index_path)
        driver_index = create_in(driver_index_path, driver_schema)
        add_driver_data(driver_index)

def add_driver_data(index):
    """Indexa los datos de Driver en Whoosh."""
    from f1legacy.models import Driver
    writer = index.writer()
    for driver in Driver.objects.all():
        writer.add_document(
            id=str(driver.id),
            name=driver.name,
            number=driver.number if driver.number else 0,
            team=driver.team.name if driver.team else "No info",
            championships=driver.championships if driver.championships else 0,
            races=driver.races if driver.races else 0,
            victories=driver.victories if driver.victories else 0,
        )
    writer.commit()

def add_team_data(index):
    """Indexa los datos de Team en Whoosh."""
    from f1legacy.models import Team
    writer = index.writer()
    for team in Team.objects.all():
        writer.add_document(
            id=str(team.id),
            name=team.name,
            championships=team.championships if team.championships else 0,
            victories=team.victories if team.victories else 0,
        )
    writer.commit()

def get_driver_index():
    """Devuelve el índice de drivers o lo crea si no existe."""
    driver_index_path = os.path.join(INDEX_DIR, "drivers")
    try:
        return open_dir(driver_index_path)
    except EmptyIndexError:
        create_in(driver_index_path, driver_schema)
        return open_dir(driver_index_path)

def get_team_index():
    """Devuelve el índice de teams o lo crea si no existe."""
    team_index_path = os.path.join(INDEX_DIR, "teams")
    try:
        return open_dir(team_index_path)
    except EmptyIndexError:
        create_in(team_index_path, team_schema)
        return open_dir(team_index_path)
