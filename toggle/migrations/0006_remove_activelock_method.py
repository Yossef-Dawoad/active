# Generated by Django 4.0.4 on 2022-07-03 12:03

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('toggle', '0005_activelock_method'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='activelock',
            name='method',
        ),
    ]