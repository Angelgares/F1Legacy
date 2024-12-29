from django.db import models

class Team(models.Model):
    name = models.CharField(max_length=100)
    base = models.CharField(max_length=100)
    team_principal = models.CharField(max_length=100)
    chassis = models.CharField(max_length=100)
    power_unit = models.CharField(max_length=100)
    championships = models.IntegerField()
    victories = models.IntegerField()
    pole_positions = models.IntegerField()
    fastest_laps = models.IntegerField()
    image = models.URLField(blank=True, null=True)

    def __str__(self):
        return self.name
    
class Driver(models.Model):
    name = models.CharField(max_length=100)
    number = models.IntegerField(blank=True, null=True)
    country = models.CharField(max_length=100, blank=True, null=True)
    country_flag = models.URLField(blank=True, null=True)
    team = models.ForeignKey(Team, on_delete=models.CASCADE, null=True, blank=True, related_name='drivers')
    birth_date = models.DateField(blank=True, null=True)
    points = models.FloatField(blank=True, null=True)
    podiums = models.IntegerField(blank=True, null=True)
    victories = models.IntegerField(blank=True, null=True)
    races = models.IntegerField(blank=True, null=True)
    championships = models.IntegerField(blank=True, null=True)
    image = models.URLField(blank=True, null=True)

    def __str__(self):
        return self.name
    


