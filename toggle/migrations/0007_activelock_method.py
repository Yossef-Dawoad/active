# Generated by Django 4.0.6 on 2022-08-03 22:26

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('toggle', '0006_remove_activelock_method'),
    ]

    operations = [
        migrations.AddField(
            model_name='activelock',
            name='method',
            field=models.CharField(default='None', max_length=200),
        ),
    ]