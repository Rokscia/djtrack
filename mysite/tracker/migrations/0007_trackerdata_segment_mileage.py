# Generated by Django 4.2 on 2023-06-29 20:24

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('tracker', '0006_tripmetadata_trackerdata_trip'),
    ]

    operations = [
        migrations.AddField(
            model_name='trackerdata',
            name='segment_mileage',
            field=models.FloatField(null=True),
        ),
    ]
