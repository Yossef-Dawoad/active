# Generated by Django 4.0.6 on 2022-08-12 09:39

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('pages', '0003_initial'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='recordedvideos',
            name='url',
        ),
        migrations.AddField(
            model_name='recordedvideos',
            name='video',
            field=models.FileField(null=True, upload_to='events'),
        ),
    ]