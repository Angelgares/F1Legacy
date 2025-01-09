# Generated by Django 5.1.4 on 2025-01-08 20:21

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('f1legacy', '0002_startinggrid_raceresult'),
    ]

    operations = [
        migrations.AlterField(
            model_name='team',
            name='base',
            field=models.CharField(blank=True, max_length=100, null=True),
        ),
        migrations.AlterField(
            model_name='team',
            name='championships',
            field=models.PositiveIntegerField(blank=True, null=True),
        ),
        migrations.AlterField(
            model_name='team',
            name='chassis',
            field=models.CharField(blank=True, max_length=100, null=True),
        ),
        migrations.AlterField(
            model_name='team',
            name='fastest_laps',
            field=models.PositiveIntegerField(blank=True, null=True),
        ),
        migrations.AlterField(
            model_name='team',
            name='pole_positions',
            field=models.PositiveIntegerField(blank=True, null=True),
        ),
        migrations.AlterField(
            model_name='team',
            name='power_unit',
            field=models.CharField(blank=True, max_length=100, null=True),
        ),
        migrations.AlterField(
            model_name='team',
            name='team_principal',
            field=models.CharField(blank=True, max_length=100, null=True),
        ),
        migrations.AlterField(
            model_name='team',
            name='victories',
            field=models.PositiveIntegerField(blank=True, null=True),
        ),
    ]
