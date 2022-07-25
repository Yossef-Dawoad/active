import json
from pathlib import Path
from channels.generic.websocket import AsyncWebsocketConsumer
import numpy as np
from static.processingtools.utils import TimeTracker, IsItNightImage
import cv2
from .models import RecordedVideos
from .serializers import RecordedVideosObjSerializer
from .tasks import saveimagefordayandnight, process_frame_Task
from asgiref.sync import sync_to_async
import ffmpeg

# videofoldername = 0
# imagesavefolder = f"./static/recordings/images/{videofoldername}"
# Path(imagesavefolder).mkdir(exist_ok=True)


############ night Light Folder
dayandnightfolder = f"./static/recordings/images/dayNightDataSet"
Path(dayandnightfolder).mkdir(parents=True, exist_ok=True)
############


class VideoHandlerConsumer(AsyncWebsocketConsumer):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        ######################################## recording config


        self.MinuteTime = 60
        self.fps = 17
        self.process_write = None
        self.tt = TimeTracker()
        self.videosavefolder = Path("./static/recordings/videos/")
        self.outputvideo = self.videosavefolder.joinpath(self.tt.format_time() + ".mp4")
        print(self.outputvideo)
        ########################################### Night ,Day Detection
        self.DayNightTresh = 100
        ########################################### process config
        self.skipframetoprocess = 5
        self.framenumbertoskip = 0
        ########################################### camera channel id
        self.camera_channel_name = None



    async def connect(self):
        self.roomName = "video_channel"
        await self.channel_layer.group_add( #create video_pool group
            self.roomName,
            self.channel_name
        )
        await self.accept()


    async def disconnect(self, close_code):
        await self.channel_layer.group_discard(
            self.roomName,
            self.channel_name
        )
        # if camera disconncted make suresave the video 
        if self.channel_name == self.camera_channel_name:
            print("[Warnning] the camera has been disconnected")
            self.process_write.stdin.close()
            self.process_write.wait()



    async def receive(self, text_data=None, bytes_data=None):
        self.camera_channel_name = self.channel_name
        await self.channel_layer.group_send(
            self.roomName,{
                'type':'videoStream',
                'data':bytes_data,
                'sender_channel_name':self.channel_name}
        )


        ######################## setup recoding folder
        self.fps += self.tt.fps_calculate()
        self.fps /= 2.0
        if self.process_write is None:await self.initializenewwriter()
        await self.savebytestovideo(bytes_data)

        print(self.fps, end='\r')



    async def videoStream(self, event):
        if self.channel_name != event['sender_channel_name']:
            image_bytes = event['data']
            await self.send(bytes_data=image_bytes)


    ########## expermental
    async def savebytestovideo(self, imagebytes):
        if self.tt.time_pass_s(0.5 * self.MinuteTime) and self.process_write is not None:
            print("encoding the current video >>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>")
            self.process_write.stdin.close()
            self.process_write.wait()
            
            await self.savevideotodb()
            await self.initializenewwriter()

        imgbuffer = np.frombuffer(imagebytes, dtype = np.uint8)
        img =  cv2.imdecode(imgbuffer, cv2.IMREAD_UNCHANGED)
        self.process_write.stdin.write(
           (cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
            .tobytes())
        )

        self.ImageWIDTH, self.ImageHEIGHT = img.shape[:2]

        ###############################################
        self.framenumbertoskip += 1
        if self.skipframetoprocess <= self.framenumbertoskip:
            # if self.tt.time_pass(60):
            process_frame_Task.delay(img)
            ######################### Night & Day Detection
            # isNIGHT_TIME = IsItNightImage(img, self.DayNightTresh, self.ImageWIDTH, self.ImageHEIGHT)
            # print("\nis the image NightTime: " , isNIGHT_TIME, end='\r')
            await self.IsItNightImage_async_process(img)
            self.framenumbertoskip = 0
        
        if self.tt.time_pass_s(self.MinuteTime * 10):
            saveimagefordayandnight.delay(img)

    @sync_to_async  
    def IsItNightImage_async_process(self, image):
        isNIGHT_TIME = IsItNightImage(image, self.DayNightTresh, self.ImageWIDTH, self.ImageHEIGHT)
        # in not __init__ start of the file iniate the connection to the server esp
        # client send post to the server
        # print("\nis the image NightTime: " , isNIGHT_TIME, end='\r')



    @sync_to_async      
    def initializenewwriter(self):

        w, h = 640, 480 
        self.outputvideo = self.videosavefolder.joinpath(self.tt.format_time() + ".mp4")
        print(f"initalize the writer with  {self.outputvideo}")
        self.process_write = (
            ffmpeg
                .input('pipe:',format='rawvideo', pix_fmt='rgb24', s=f'{w}x{h}')
                .output(str(self.outputvideo), pix_fmt='yuv420p', vcodec='libx264', r=self.fps, crf=31)
                .overwrite_output()
                .run_async(pipe_stdin=True)
        )
        

    @sync_to_async
    def savevideotodb(self):
        print("saving the video to the database >>>>>>>>>>>>>>>>")
        newvideorecord = RecordedVideosObjSerializer(
            data={
                "title" : str(self.outputvideo), 
                "url" : str(self.videosavefolder)
            }
        )
        print("<-"*20)
        if newvideorecord.is_valid():
            print("->"*20)
            newvideorecord.save()



    async def task_recognize(self, event):
        facename  = event["data"]
        # Send message to WebSocket
        await self.send(
            text_data=json.dumps({
                'facename': facename
        }))

