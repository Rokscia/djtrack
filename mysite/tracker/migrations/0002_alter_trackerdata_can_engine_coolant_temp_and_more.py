# Generated by Django 4.2 on 2023-04-13 16:50

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('tracker', '0001_initial'),
    ]

    operations = [
        migrations.AlterField(
            model_name='trackerdata',
            name='can_engine_coolant_temp',
            field=models.IntegerField(),
        ),
        migrations.AlterField(
            model_name='trackerdata',
            name='can_engine_intake_air_temp',
            field=models.IntegerField(),
        ),
        migrations.AlterField(
            model_name='trackerdata',
            name='can_engine_load_level',
            field=models.IntegerField(),
        ),
        migrations.AlterField(
            model_name='trackerdata',
            name='can_vehicle_speed',
            field=models.IntegerField(),
        ),
    ]
