# Generated by Django 4.0.4 on 2022-06-23 17:06

import datetime
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('attendance', '0007_alter_log_date_alter_log_time_in'),
    ]

    operations = [
        migrations.AlterField(
            model_name='log',
            name='date',
            field=models.DateField(default=datetime.datetime(2022, 6, 23, 17, 6, 33, 904994)),
        ),
        migrations.AlterField(
            model_name='log',
            name='time_in',
            field=models.TimeField(default=datetime.datetime(2022, 6, 23, 17, 6, 33, 905013)),
        ),
    ]
