import requests, re, os, django, sys
from bs4 import BeautifulSoup
from datetime import datetime
from django.db.models import Q

sys.path.append(
    os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
)
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "f1legacy_project.settings")
django.setup()

from f1legacy.models import Driver, Team


def get_drivers():
    url = "https://www.formula1.com/en/drivers"

    response = requests.get(url)

    if response.status_code == 200:
        soup = BeautifulSoup(response.text, "html.parser")

        drivers = soup.find_all("a", class_="group focus-visible:outline-0")

        for driver in drivers:
            href = driver["href"]
            detail_url = f"https://www.formula1.com{href}"

            driver_response = requests.get(detail_url)

            if driver_response.status_code == 200:
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
                    team=team,
                    birth_date=birth_date,
                    points=points,
                    podiums=podiums,
                    victories=victories,
                    races=races,
                    championships=championships,
                    image=image,
                )

    else:
        print(f"Error al acceder a la página: {response.status_code}")


def get_teams():
    url = "https://www.formula1.com/en/teams"

    response = requests.get(url)

    if response.status_code == 200:
        soup = BeautifulSoup(response.text, "html.parser")

        teams = soup.find_all("a", class_="group focus-visible:outline-0")

        for team in teams:
            href = team["href"]
            detail_url = f"https://www.formula1.com{href}"

            team_response = requests.get(detail_url)

            if team_response.status_code == 200:
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

            else:
                print(f"Error al acceder a la página: {response.status_code}")


def get_flag_png(data):
    """
    Filtra la URI de la bandera en formato .png desde la sección 'flags'. Utiliza la API de restcountries.com.

    :param data: Json con los datos del país.
    :return: String con la URI de la bandera en formato .png, o None si no se encuentra.
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

    :param data_string: String con información del piloto, en el formato "1 (xVeces)".
    :return: Número de veces que el piloto quedó en primer lugar, o 0 si no aplica.
    """
    match = re.search(r"1\s*\(x(\d+)\)", data_string)
    if match:
        return int(match.group(1))
    else:
        return 0


def calculate_age(birth_date_str):
    """
    Calcula la edad actual a partir de una fecha de nacimiento en formato DD/MM/YYYY.

    :param birth_date_str: Fecha de nacimiento como string, en formato "DD/MM/YYYY".
    :return: Edad actual como un número entero.
    """
    birth_date = datetime.strptime(birth_date_str, "%d/%m/%Y")

    today = datetime.today()

    age = today.year - birth_date.year

    if (today.month, today.day) < (birth_date.month, birth_date.day):
        age -= 1

    return age


def parse_url(url):
    """
    Parsea una URL sustituyendo los espacios por "%20".

    :param url: URL de la página a parsear.
    :return: URL parseada.
    """

    return url.replace(" ", "%20")
