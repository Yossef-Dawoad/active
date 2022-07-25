from django.db import models

# Create your models here.
class RecordedVideos(models.Model):
    title = models.CharField(max_length=200)
    url = models.TextField()
    created_in = models.DateTimeField(auto_now=True)
    # lenght = function calc the lenght of the video

    def get_url(self):
        pass

    def __str__(self) -> str:
        return self.title