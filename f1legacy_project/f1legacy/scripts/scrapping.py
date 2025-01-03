import requests, re, os, django, sys
from bs4 import BeautifulSoup
from datetime import datetime, timedelta
from django.db.models import Q
from django.db import transaction
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry

sys.path.append(
    os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
)
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "f1legacy_project.settings")
django.setup()

from f1legacy.models import Driver, Team, DriverStanding, TeamStanding, GrandPrix, StartingGrid, RaceResult
from f1legacy.scripts.whoosh_index import add_driver_data, add_team_data, get_driver_index, get_team_index

def get_drivers():
    url = "https://www.formula1.com/en/drivers"

    try:
        response = get_retry_session().get(url)

        soup = BeautifulSoup(response.text, "html.parser")

        drivers = soup.find_all("a", class_="group focus-visible:outline-0")

        for driver in drivers:
            href = driver["href"]
            detail_url = f"https://www.formula1.com{href}"

            try:
                driver_response = get_retry_session().get(detail_url)

                driver_soup = BeautifulSoup(driver_response.text, "html.parser")

                try:
                    name = (
                        driver_soup.find(
                            "div",
                            class_="f1-driver-position flex flex-col gap-micro f1-utils-inner-padding",
                        )
                        .find("h1")
                        .text.strip()
                    )

                    number = (
                        driver_soup.find("div", class_="flex gap-normal items-center")
                        .find("p")
                        .text.strip()
                    )

                    country_driver = (
                        driver_soup.find("div", class_="f1-dl")
                        .find_all("dd")[1]
                        .text.strip()
                    )

                    try:
                        if country_driver == 'China':
                            flag_url = requests.get("https://restcountries.com/v3.1/name/" + 'Cn').json()
                        else:
                            flag_url = requests.get("https://restcountries.com/v3.1/name/" + country_driver).json()
                        country_flag = get_flag_png(flag_url)
                        
                    except requests.RequestException as e:
                        print(f"Error fetching flag for {country_driver}: {e}")
                        country_flag = None

                    team = (
                        driver_soup.find("div", class_="f1-dl")
                        .find_all("dd")[0]
                        .text.strip()
                    )
                    team = Team.objects.filter(Q(name__icontains=team)).first()

                    birth_date = (
                        driver_soup.find("div", class_="f1-dl")
                        .find_all("dd")[8]
                        .text.strip()
                    )
                    birth_date = datetime.strptime(birth_date, "%d/%m/%Y")

                    points = (
                        driver_soup.find("div", class_="f1-dl")
                        .find_all("dd")[3]
                        .text.strip()
                    )

                    podiums = (
                        driver_soup.find("div", class_="f1-dl")
                        .find_all("dd")[2]
                        .text.strip()
                    )

                    victories = (
                        driver_soup.find("div", class_="f1-dl")
                        .find_all("dd")[6]
                        .text.strip()
                    )
                    victories = get_victories(victories)

                    races = (
                        driver_soup.find("div", class_="f1-dl")
                        .find_all("dd")[4]
                        .text.strip()
                    )

                    championships = (
                        driver_soup.find("div", class_="f1-dl")
                        .find_all("dd")[5]
                        .text.strip()
                    )

                    image = driver_soup.find("div", class_="overflow-hidden").find(
                        "img"
                    )["src"]

                except (AttributeError, IndexError):
                    name = detail_url.split("/")[-1].replace("-", " ").title()
                    number = None
                    country_driver = None
                    country_flag = None
                    team = None
                    birth_date = None
                    points = None
                    podiums = None
                    victories = None
                    races = None
                    championships = None
                    image = None

                Driver.objects.update_or_create(
                    name=name,
                    number=number,
                    country=country_driver,
                    country_flag=country_flag,
                    team=team,
                    birth_date=birth_date,
                    points=points,
                    podiums=podiums,
                    victories=victories,
                    races=races,
                    championships=championships,
                    image=image,
                )
            
            except (requests.RequestException, AttributeError) as e:
                print(f"Error fetching driver data: {e}")
                continue
    except requests.RequestException as e:
        print(f"Error fetching driver list: {e}")

    add_driver_data(get_driver_index())

def get_teams():
    url = "https://www.formula1.com/en/teams"

    try:
        response = get_retry_session().get(url)

        soup = BeautifulSoup(response.text, "html.parser")

        teams = soup.find_all("a", class_="group focus-visible:outline-0")

        for team in teams:
            href = team["href"]
            detail_url = f"https://www.formula1.com{href}"

            try:
                team_response = get_retry_session().get(detail_url)

                team_soup = BeautifulSoup(team_response.text, "html.parser")

                try:
                    name = (
                        team_soup.find("div", class_="f1-dl")
                        .find_all("dd")[0]
                        .text.strip()
                    )

                    base = (
                        team_soup.find("div", class_="f1-dl")
                        .find_all("dd")[1]
                        .text.strip()
                    )

                    team_principal = (
                        team_soup.find("div", class_="f1-dl")
                        .find_all("dd")[2]
                        .text.strip()
                    )

                    chassis = (
                        team_soup.find("div", class_="f1-dl")
                        .find_all("dd")[4]
                        .text.strip()
                    )

                    power_unit = (
                        team_soup.find("div", class_="f1-dl")
                        .find_all("dd")[5]
                        .text.strip()
                    )

                    championships = (
                        team_soup.find("div", class_="f1-dl")
                        .find_all("dd")[7]
                        .text.strip()
                    )

                    victories = (
                        team_soup.find("div", class_="f1-dl")
                        .find_all("dd")[8]
                        .text.strip()
                    )
                    victories = get_victories(victories)

                    pole_positions = (
                        team_soup.find("div", class_="f1-dl")
                        .find_all("dd")[9]
                        .text.strip()
                    )

                    fastest_laps = (
                        team_soup.find("div", class_="f1-dl")
                        .find_all("dd")[10]
                        .text.strip()
                    )

                    image = team_soup.find(
                        "figure",
                        class_="f1-driver-helmet overflow-hidden max-mobile:max-w-1/2 max-mobile:mx-auto mobile:col-span-2",
                    ).find("img")["src"]
                    image = parse_url(image)

                except (AttributeError, IndexError):
                    name = None
                    base = None
                    team_principal = None
                    chassis = None
                    power_unit = None
                    championships = None
                    victories = None
                    pole_positions = None
                    fastest_laps = None
                    image = None

                Team.objects.update_or_create(
                    name=name,
                    base=base,
                    team_principal=team_principal,
                    chassis=chassis,
                    power_unit=power_unit,
                    championships=championships,
                    victories=victories,
                    pole_positions=pole_positions,
                    fastest_laps=fastest_laps,
                    image=image,
                )

            except (requests.RequestException, AttributeError) as e:
                print(f"Error fetching team data: {e}")
                continue

    except requests.RequestException as e:
        print(f"Error fetching team list: {e}")
    
    add_team_data(get_team_index())

def get_driver_standings(start_year, end_year):
    url = "https://www.formula1.com/en/results/{year}/drivers"

    for year in range(start_year, end_year + 1):
        year_url = url.format(year=year)

        try:
            response = get_retry_session().get(year_url, timeout=10)

            soup = BeautifulSoup(response.text, "html.parser")

            drivers = soup.find('table', class_='f1-table f1-table-with-data w-full').find_all('tr')[1:]

            for driver in drivers:
                driver_stats = driver.find_all("td")
                try:
                    position = driver_stats[0].text.strip()
                    name = driver_stats[1].text.strip()[:-3]
                    car = driver_stats[3].text.strip()
                    points = driver_stats[4].text.strip()
                
                except (AttributeError, IndexError):
                    name = None
                    car = None
                    year = year
                    position = None
                    points = None
                
                DriverStanding.objects.update_or_create(
                    name=name,
                    car=car,
                    year=year,
                    position=position,
                    points=points,
                )
            
        except requests.RequestException as e:
            print(f"Error fetching driver standings: {e}")


def get_team_standings(start_year, end_year):
    url = "https://www.formula1.com/en/results/{year}/team"

    for year in range(start_year, end_year + 1):
        year_url = url.format(year=year)

        try:
            response = get_retry_session().get(year_url, timeout=10)

            soup = BeautifulSoup(response.text, "html.parser")

            teams = soup.find('table', class_='f1-table f1-table-with-data w-full').find_all('tr')[1:]

            for team in teams:
                team_stats = team.find_all("td")
                try:
                    position = team_stats[0].text.strip()
                    if position == "EX":
                        position = 0
                    name = team_stats[1].text.strip()
                    points = team_stats[2].text.strip()
                
                except (AttributeError, IndexError):
                    name = None
                    year = year
                    position = None
                    points = None
                
                TeamStanding.objects.update_or_create(
                    name=name,
                    year=year,
                    position=position,
                    points=points,
                )
            
        except requests.RequestException as e:
            print(f"Error fetching team standings: {e}")

@transaction.atomic
def get_grand_prixes(start_year, end_year):
    url = "https://www.formula1.com/en/results/{year}/races"

    for year in range(start_year, end_year + 1):
        year_url = url.format(year=year)

        try:
            response = get_retry_session().get(year_url, timeout=5)

            soup = BeautifulSoup(response.text, "html.parser")

            grand_prixes = soup.find('table', class_='f1-table f1-table-with-data w-full').find_all('tr')[1:]

            for grand_prix in grand_prixes:
                grand_prix = grand_prix.find_all('td')[0]
                country = grand_prix.find('a').text.strip()
                href = grand_prix.find('a')['href']

                # Grand Prix scraping

                grand_prix_url = f"https://www.formula1.com/en/results/{year}/{href}"

                try:
                    grand_prix_response = requests.get(grand_prix_url)

                    grand_prix_soup = BeautifulSoup(grand_prix_response.text, "html.parser")

                    try:
                        gp_info = grand_prix_soup.find('div', class_='max-tablet:flex-col flex gap-xs').find_all('p')
                        gp_name = gp_info[1].text.strip().split(',')[0]
                        city = gp_info[1].text.strip().split(',')[1]
                        location = country + ', ' + city
                        start_date, end_date = parse_dates(gp_info[0].text.strip())
                    
                    except (AttributeError, IndexError):
                        gp_name = None
                        location = None
                        start_date = None
                        end_date = None
                    
                    GrandPrix.objects.update_or_create(
                        name=gp_name,
                        location=location,
                        start_date=start_date,
                        end_date=end_date,
                    )
                except requests.RequestException as e:
                    print(f"Error fetching grand prix data: {e}")
                    continue    

                # Starting Grid scraping

                starting_grid_url = grand_prix_url.replace('race-result', 'starting-grid')
                try:   
                    starting_grid_repsonse = get_retry_session().get(starting_grid_url)

                    starting_grid_soup = BeautifulSoup(starting_grid_repsonse.text, "html.parser")
                    starting_grid_info = starting_grid_soup.find('table', class_='f1-table f1-table-with-data w-full').find_all('tr')[1:]
                   
                    for sg_info in starting_grid_info:
                        try:
                            sg_info = sg_info.find_all('td')
                            sg_grand_prix = GrandPrix.objects.filter(Q(end_date=end_date)).first()
                            driver = sg_info[2].text.strip()[:-3]
                            car = sg_info[3].text.strip()
                            position = sg_info[0].text.strip()
                            lap_time = sg_info[4].text.strip()

                        except (AttributeError, IndexError):
                            grand_prix = None
                            driver = "Driver not found"
                            car = "Car not found"
                            position = None
                            lap_time = None

                        StartingGrid.objects.update_or_create(
                            grand_prix=sg_grand_prix,
                            driver=driver,
                            car=car,
                            position=position,
                            lap_time=lap_time,
                        )

                except requests.RequestException as e:
                    print(f"Error fetching starting grid data: {e}")

                # Race Result scraping

                try:
                    race_result_response = requests.get(grand_prix_url)

                    race_result_soup = BeautifulSoup(race_result_response.text, "html.parser")
                    race_result_info = race_result_soup.find('table', class_='f1-table f1-table-with-data w-full').find('tbody').find_all('tr')

                    for rr_info in race_result_info:
                        try:
                            rr_info = rr_info.find_all('td')
                            driver = rr_info[2].text.strip()[:-3]
                            car = rr_info[3].text.strip()
                            rr_starting_grid = StartingGrid.objects.filter(
                                Q(grand_prix__end_date=end_date) & 
                                Q(driver__icontains=driver)).first()
                            if not rr_starting_grid:
                                StartingGrid.objects.update_or_create(
                                    grand_prix=sg_grand_prix,
                                    driver=driver,
                                    car=car,
                                    position=0,
                                    lap_time=None,
                                )
                                rr_starting_grid = StartingGrid.objects.filter(
                                Q(grand_prix__end_date=end_date) & 
                                Q(driver__icontains=driver)).first()
                            position = rr_info[0].text.strip()
                            if position == "NC" or position == "EX" or position == "DQ":
                                position = 0
                            laps_completed = rr_info[4].text.strip()
                            if laps_completed == "":
                                laps_completed = 0
                            total_time = rr_info[5].text.strip()
                            points = rr_info[6].text.strip()

                        except (AttributeError, IndexError):
                            rr_starting_grid = rr_starting_grid
                            position = None
                            laps_completed = None
                            total_time = None
                            points = None

                        RaceResult.objects.update_or_create(
                            starting_grid=rr_starting_grid,
                            position=position,
                            laps_completed=laps_completed,
                            total_time=total_time,
                            points=points,
                        )
                
                except requests.RequestException as e:
                    print(f"Error fetching race result data: {e}")
                
        except requests.RequestException as e:
            print(f"Error fetching grand prix list: {e}")


def get_retry_session():
    retry_strategy = Retry(
        total=5, 
        backoff_factor=1,
        status_forcelist=[500, 502, 503, 504], 
        allowed_methods=["HEAD", "GET", "OPTIONS"]
    )
    adapter = HTTPAdapter(max_retries=retry_strategy)
    session = requests.Session()
    session.mount("https://", adapter)
    session.mount("http://", adapter)
    return session

def get_flag_png(data):
    """
    Filters the URI of the flag in .png format from the 'flags' section. Uses the restcountries.com API.

    :param data: JSON with the country data.
    :return: String with the URI of the flag in .png format, or None if not found.
    """
    try:
        if isinstance(data, list):
            data = data[0]

        return data.get("flags", {}).get("png", None)
    except AttributeError:
        return None


def get_victories(data_string):
    """
    Procesa un string y devuelve el número de veces que el piloto ha quedado en primer lugar.

    :param data_string: String con gp_información del piloto, en el formato "1 (xVeces)".
    :return: Número de veces que el piloto quedó en primer lugar, o 0 si no aplica.
    """
    match = re.search(r"1\s*\(x(\d+)\)", data_string)
    if match:
        return int(match.group(1))
    else:
        return 0


def calculate_age(birth_date_str):
    """
    Calculates the current age from a birth date in DD/MM/YYYY format.

    :param birth_date_str: Birth date as a string, in "DD/MM/YYYY" format.
    :return: Current age as an integer.
    """
    birth_date = datetime.strptime(birth_date_str, "%d/%m/%Y")

    today = datetime.today()

    age = today.year - birth_date.year

    if (today.month, today.day) < (birth_date.month, birth_date.day):
        age -= 1

    return age


def parse_url(url):
    """
    Parses a URL by replacing spaces with "%20".

    :param url: URL of the page to parse.
    :return: Parsed URL.
    """

    return url.replace(" ", "%20")

def parse_dates(date_string):
    """
    Function to process a date string and return start_date and end_date.
    
    Accepted formats:
    - "12 Mar 2000"
    - "25 - 27 Mar 2011"
    
    :param date_string: The input string with the date.
        
    :return: tuple: start_date (datetime), end_date (datetime)
    """
    if "-" in date_string:
        start_part, end_part = date_string.split("-")
        start_part = start_part.strip()  
        end_part = end_part.strip() 
        
        end_date = datetime.strptime(end_part, "%d %b %Y")
        start_date = end_date - timedelta(days=2)
    
    else:
        end_date = datetime.strptime(date_string, "%d %b %Y")
        start_date = end_date - timedelta(days=2)

    start_date = start_date.strftime("%Y-%m-%d")
    end_date = end_date.strftime("%Y-%m-%d")

    return start_date, end_date
