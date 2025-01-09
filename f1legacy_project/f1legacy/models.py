from django.db import models

class Team(models.Model):
    name = models.CharField(max_length=100)
    base = models.CharField(max_length=100, blank=True, null=True)
    team_principal = models.CharField(max_length=100, blank=True, null=True)
    chassis = models.CharField(max_length=100, blank=True, null=True)
    power_unit = models.CharField(max_length=100, blank=True, null=True)
    championships = models.PositiveIntegerField(blank=True, null=True)
    victories = models.PositiveIntegerField(blank=True, null=True)
    pole_positions = models.PositiveIntegerField(blank=True, null=True)
    fastest_laps = models.PositiveIntegerField(blank=True, null=True)
    image = models.URLField(blank=True, null=True)

    def __str__(self):
        return self.name
    
class Driver(models.Model):
    name = models.CharField(max_length=100)
    number = models.PositiveIntegerField(blank=True, null=True)
    country = models.CharField(max_length=100, blank=True, null=True)
    country_flag = models.URLField(blank=True, null=True)
    team = models.ForeignKey(Team, on_delete=models.CASCADE, related_name='drivers', blank=True, null=True)
    birth_date = models.DateField(blank=True, null=True)
    points = models.FloatField(blank=True, null=True)
    podiums = models.PositiveIntegerField(blank=True, null=True)
    victories = models.PositiveIntegerField(blank=True, null=True)
    races = models.PositiveIntegerField(blank=True, null=True)
    championships = models.PositiveIntegerField(blank=True, null=True)
    image = models.URLField(blank=True, null=True)

    def __str__(self):
        return self.name

class TeamStanding(models.Model):
    name = models.CharField(max_length=100)
    year = models.IntegerField()
    position = models.PositiveIntegerField()
    points = models.FloatField()

    def __str__(self):
        return f'{self.team.name} - {self.year}'
    
class DriverStanding(models.Model):
    name = models.CharField(max_length=100)
    car = models.CharField(max_length=100)
    year = models.IntegerField()
    position = models.PositiveIntegerField()
    points = models.FloatField()

    def __str__(self):
        return f'{self.driver.name} - {self.year}'
    
class GrandPrix(models.Model):
    name = models.CharField(max_length=100)
    location = models.CharField(max_length=100)
    start_date = models.DateField()
    end_date = models.DateField()

    def __str__(self):
        return self.name
    
class StartingGrid(models.Model):
    grand_prix = models.ForeignKey(GrandPrix, on_delete=models.CASCADE, related_name='starting_grids')
    driver = models.CharField(max_length=100)
    car = models.CharField(max_length=100)
    position = models.PositiveIntegerField(blank=True, null=True)
    lap_time = models.CharField(max_length=100, blank=True, null=True)

    def __str__(self):
        return f'{self.grand_prix.name} - {self.driver} - {self.position}'

class RaceResult(models.Model):
    starting_grid = models.ForeignKey(StartingGrid, on_delete=models.CASCADE, related_name='race_results')
    position = models.PositiveIntegerField(blank=True, null=True)
    laps_completed = models.IntegerField(blank=True, null=True)
    total_time = models.CharField(max_length=100, blank=True, null=True)
    points = models.FloatField(blank=True, null=True)

    def __str__(self):
        return f'{self.starting_grid.grand_prix.name} - {self.starting_grid.driver} - {self.position}'
