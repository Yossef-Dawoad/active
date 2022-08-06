from django.urls import path
from .views import *
from django.conf import settings
from django.conf.urls.static import static



urlpatterns = [
    path('', indexview, name='index'),
    path('videos_api/videos/', listall_videos, name='videos'),
    path('api/videos/records/', listall_videos, name='videos'),
    path('videos_api/last-video/', last_recordedvideo, name='last-video'),
    path('api/videos/last-record/', last_recordedvideo, name='last-video'),
    path('videos_api/create-video/', last_recordedvideo, name='create-video'),
] 

