# Generated by Django 4.2 on 2023-04-13 16:50

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('tracker', '0002_alter_trackerdata_can_engine_coolant_temp_and_more'),
    ]

    operations = [
        migrations.AlterField(
            model_name='trackerdata',
            name='can_engine_rpm',
            field=models.IntegerField(),
        ),
    ]
