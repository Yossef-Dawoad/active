# Generated by Django 4.0.6 on 2022-08-12 12:22

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('pages', '0004_remove_recordedvideos_url_recordedvideos_video'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='recordedvideos',
            name='video',
        ),
        migrations.AddField(
            model_name='recordedvideos',
            name='video_url',
            field=models.CharField(default='NULL', max_length=400),
            preserve_default=False,
        ),
    ]