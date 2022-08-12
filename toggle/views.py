from django.shortcuts import render
from rest_framework import response, decorators, status

from .models import ActiveLock
from .serializers import ActiveLockObjSerializer



def indexview(request):
    # print(ActiveLock().fetchlast(10, by="id"))
    return render(request, 'toggle/index.html')

@decorators.api_view(['GET', 'POST'])
def last_state(request):
    lock = ActiveLock.objects.last()
    serializer = ActiveLockObjSerializer(lock)
    return response.Response(serializer.data)


@decorators.api_view(['GET'])
def listall_states(request):


    ########################api_link/?param=value&param2=value2 
    serializeMany = True
    queries = request.query_params
    limit = queries.get('_limit')
    last = queries.get('laststate')

    if last == 'true':
        states = ActiveLock.objects.last()
        serializeMany = False
    elif limit is not None:
        states = ActiveLock.objects.all()[:int(limit)]
    else:
        states = ActiveLock.objects.all().order_by("-id")
        
    serializer = ActiveLockObjSerializer(states, many=serializeMany)
    return response.Response(serializer.data)  



@decorators.api_view(['POST'])
def create_state(request):
    '''
        "Method \"GET\" not allowed." if request.method == GET it
        returns HTTP 405 Method Not Allowed 
    '''
    print(request.data)
    newrecord = ActiveLockObjSerializer(data=request.data)
    print(newrecord)
    if not newrecord.is_valid():
        return response.Response(status=status.HTTP_400_BAD_REQUEST)
    newrecord.save()
    return response.Response({'succsess':True})

def open_the_lock(request):
    return render(request, 'toggle/index.html')
    
