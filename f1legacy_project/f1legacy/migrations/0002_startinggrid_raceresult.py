# Generated by Django 5.1.4 on 2025-01-01 13:00

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('f1legacy', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='StartingGrid',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('driver', models.CharField(max_length=100)),
                ('car', models.CharField(max_length=100)),
                ('position', models.PositiveIntegerField(blank=True, null=True)),
                ('lap_time', models.CharField(blank=True, max_length=100, null=True)),
                ('grand_prix', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='starting_grids', to='f1legacy.grandprix')),
            ],
        ),
        migrations.CreateModel(
            name='RaceResult',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('position', models.PositiveIntegerField(blank=True, null=True)),
                ('laps_completed', models.IntegerField(blank=True, null=True)),
                ('total_time', models.CharField(blank=True, max_length=100, null=True)),
                ('points', models.FloatField(blank=True, null=True)),
                ('starting_grid', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='race_results', to='f1legacy.startinggrid')),
            ],
        ),
    ]
