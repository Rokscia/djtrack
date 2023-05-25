# Generated by Django 4.2 on 2023-04-13 20:24

import datetime
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('tracker', '0003_alter_trackerdata_can_engine_rpm'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='trackerdata',
            options={'ordering': ['timestamp']},
        ),
        migrations.RemoveField(
            model_name='trackerdata',
            name='id',
        ),
        migrations.AddField(
            model_name='trackerdata',
            name='date_time',
            field=models.DateTimeField(default=datetime.datetime.now),
            preserve_default=False,
        ),
        migrations.AlterField(
            model_name='trackerdata',
            name='timestamp',
            field=models.BigIntegerField(primary_key=True, serialize=False),
        ),
    ]
