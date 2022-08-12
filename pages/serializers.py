from .models import RecordedVideos
from rest_framework import serializers



class RecordedVideosObjSerializer(serializers.ModelSerializer):
   
    class Meta:
        model = RecordedVideos
        fields = '__all__'
        read_only_fields = ['id', 'created_in']


