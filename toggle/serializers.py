from .models import ActiveLock
from rest_framework import serializers



class ActiveLockObjSerializer(serializers.ModelSerializer):

    
    class Meta:
        model = ActiveLock
        fields = '__all__'
        read_only_fields = ['id', 'timestamp', 'user']