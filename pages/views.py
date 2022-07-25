
from django.shortcuts import render
from django.core.paginator import Paginator

from .models import RecordedVideos
from rest_framework import response, decorators, status
from .serializers import RecordedVideosObjSerializer

# Create your views here.
def indexview(request):

    ######################## Pagination
    videos_list = RecordedVideos.objects.all()
    paginator = Paginator(videos_list, 6) # Show 6 videos per page.

    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    return render(request, 'pages/index.html', {'pageObj': page_obj, 'last_videos':videos_list.order_by('-id')[:2]})
    

@decorators.api_view(['GET'])
def listall_videos(request):
    records = RecordedVideos.objects.all()
    serializer = RecordedVideosObjSerializer(records, many=True)
    return response.Response({'videos_hist':serializer.data})

@decorators.api_view(['GET', 'POST'])
def last_recordedvideo(request):
    if request.method == "POST":
        print(request.data)
        print(type(request.data))
        newrecord = RecordedVideosObjSerializer(data=request.data)
        if not newrecord.is_valid():
            return response.Response(status=status.HTTP_400_BAD_REQUEST)
        newrecord.save()
    video = RecordedVideos.objects.last()
    serializer = RecordedVideosObjSerializer(video)
    return response.Response(serializer.data)


@decorators.api_view(['POST'])
def create_videorecord(request):
    '''
        "Method \"GET\" not allowed." if request.method == GET it
        returns HTTP 405 Method Not Allowed 
    '''
    print(request.data)
    newrecord = RecordedVideosObjSerializer(data=request.data)
    print(newrecord)
    if not newrecord.is_valid():
        return response.Response(status=status.HTTP_400_BAD_REQUEST)
    newrecord.save()
    return response.Response({'succsess':True})

