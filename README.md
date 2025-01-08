# F1Legacy

F1Legacy is a web application developed with Django that allows scraping historical Formula 1 data, processing the information, and presenting it in customized views. The project is designed to analyze historical data since 1958, the year the Constructors' Championship began (although Formula 1 started in 1950 with only the Drivers' Championship), including information on drivers, teams, and detailed race results.

## Main Features
- **Data Scraping**. Uses the BeautifulSoup library to extract public data from the main Formula 1 page by accessing various sections.
- **Database**. Uses SQLite 3 to store all extracted information in a structured and accessible manner.
- **Data Management**. Efficient indexing with Whoosh for fast queries.
- **Web Interface**. Developed with Django, it offers interactive views to explore the information intuitively.

## Prerequisites
Make sure you have the following components installed:

- **Python 3.12**
- **Git**
- **pip** (Python package manager)

## Installation

Follow these steps to set up the project on your local machine:

1. **Clone the repository**:
   ```bash
   git clone <repository-URL>
   cd F1Legacy
   ```

2. **Run the installation script**:
   This script will create a virtual environment, install dependencies, and set up a commit message hook.
   ```bash
   ./install.sh
   ```

3. **Activate the virtual environment**:
   ```bash
   source venv/bin/activate
   ```

## Initial Configuration

1. **Database Migrations**:
    Make sure to create and apply the necessary migrations:
    ```bash
    python manage.py makemigrations
    python manage.py migrate
    ```

## Running the Project

1. **Start the development server**:
   ```bash
   python manage.py runserver
   ```
   Access the application at [http://localhost:8000](http://localhost:8000).

## Project Structure

The project follows an organized structure that includes the following main folders and files:

```
F1Legacy/
├── f1legacy_project/              # Main Django project folder
│   ├── f1legacy/                  # Main application
│   │   ├── migrations/            # Database migrations
│   │   ├── scripts/               # Custom scripts for data management
│   │   │   ├── scraping.py        # Data scraping script
│   │   │   └── whoosh_index.py    # Data indexing script
│   │   ├── static/                # Static files (CSS, images)
│   │   ├── templates/             # HTML templates for views
│   │   ├── templatetags/          # Custom template tags
│   │   │   └── custom_filters.py  # Custom template filters
│   │   ├── models.py              # Application data models
│   │   ├── urls.py                # Application-specific routing
│   │   ├── views.py               # Application view logic
│   │   └── ...                    # Other related files
│   ├── f1legacy_project/          # Django project configuration
│   │   ├── settings.py            # Main project configuration
│   │   ├── urls.py                # Main project routing
│   │   └── ...                    # Other configuration files
│   ├── manage.py                  # Main Django script
├── venv/                          # Python virtual environment
├── requirements.txt               # Project dependencies list
├── install.sh                     # Automatic installation script
├── LICENSE                        # Project license
└── README.md                      # Project documentation
```

## Main Dependencies
The project uses the following Python libraries:

- `Django`. Main web framework.
- `BeautifulSoup4`. For data scraping.
- `Requests`. For making HTTP requests.
- `Urllib3`. For managing HTTP connections.
- `Whoosh`. For data indexing and fast queries.

## License
This project is under the MIT License. See the `LICENSE` file for more details.

---

With this README, developers and interested users can understand the purpose of the project, set it up, and run it on their local machine. Additionally, information about the main dependencies and the project license is provided.

