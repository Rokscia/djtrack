# Generated by Django 4.2 on 2023-04-13 21:19

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('tracker', '0004_alter_trackerdata_options_remove_trackerdata_id_and_more'),
    ]

    operations = [
        migrations.AlterField(
            model_name='trackerdata',
            name='battery_voltage',
            field=models.FloatField(max_length=10, null=True),
        ),
        migrations.AlterField(
            model_name='trackerdata',
            name='ble_humidity_1',
            field=models.FloatField(max_length=8, null=True),
        ),
        migrations.AlterField(
            model_name='trackerdata',
            name='ble_humidity_2',
            field=models.FloatField(max_length=8, null=True),
        ),
        migrations.AlterField(
            model_name='trackerdata',
            name='ble_temperature_1',
            field=models.FloatField(max_length=8, null=True),
        ),
        migrations.AlterField(
            model_name='trackerdata',
            name='ble_temperature_2',
            field=models.FloatField(max_length=8, null=True),
        ),
        migrations.AlterField(
            model_name='trackerdata',
            name='can_engine_coolant_temp',
            field=models.IntegerField(null=True),
        ),
        migrations.AlterField(
            model_name='trackerdata',
            name='can_engine_intake_air_temp',
            field=models.IntegerField(null=True),
        ),
        migrations.AlterField(
            model_name='trackerdata',
            name='can_engine_load_level',
            field=models.IntegerField(null=True),
        ),
        migrations.AlterField(
            model_name='trackerdata',
            name='can_engine_rpm',
            field=models.IntegerField(null=True),
        ),
        migrations.AlterField(
            model_name='trackerdata',
            name='can_vehicle_speed',
            field=models.IntegerField(null=True),
        ),
        migrations.AlterField(
            model_name='trackerdata',
            name='ignition_status',
            field=models.BooleanField(null=True),
        ),
        migrations.AlterField(
            model_name='trackerdata',
            name='latitude',
            field=models.FloatField(max_length=10, null=True),
        ),
        migrations.AlterField(
            model_name='trackerdata',
            name='longitude',
            field=models.FloatField(max_length=10, null=True),
        ),
        migrations.AlterField(
            model_name='trackerdata',
            name='movement_status',
            field=models.BooleanField(null=True),
        ),
        migrations.AlterField(
            model_name='trackerdata',
            name='power_voltage',
            field=models.FloatField(max_length=10, null=True),
        ),
    ]
