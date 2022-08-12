import json
from pathlib import Path
from channels.generic.websocket import AsyncWebsocketConsumer
import numpy as np
from static.processingtools.utils import MotionDetection, TimeTracker, IsItNightImage
import cv2
from .models import RecordedVideos
from .serializers import RecordedVideosObjSerializer
from .tasks import process_frame_faceRecogTask, process_frame_objectDetectTask, saveimagefordayandnight, process_frame_Task, sendemail_task
from asgiref.sync import sync_to_async
import ffmpeg



# videofoldername = 0
imagesavefolder = f"./media/events"
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
        self.videosavefolder = Path("./media/events/") #"./static/recordings/videos/"
        self.outputvideo = self.videosavefolder.joinpath(self.tt.format_time() + ".mp4")
        print(self.outputvideo)
        ########################################### Night ,Day Detection
        self.DayNightTresh = 100
        ########################################### process config
        self.skipframetoprocess = 7
        self.framenumbertoskip = 0
        ########################################### camera channel id
        self.camera_channel_name = None

        self.objects_to_detectd = ['person',
                                    ["bicycle", "car", "motorcycle","airplane","bus","train","truck"],
                                    ["cat","dog","horse","sheep","cow","elephant","bear","zebra","giraffe"],]
        self.motion = MotionDetection()
        ####################### video recording flags
        self.RECORDING_EN = False
        self.STOPED_DETECTION = False
        self.STOP_TOLERANCE_IN_SECONDS = 10

        ####################### email sending flags
        self.SEND_EMAIL_ALREADY = False
        self.EMAIL_STOP_TOLERANCE_IN_SECONDS = 10 * 60

        

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
        
        ######################## send the stream to all clients except the stream client
        self.camera_channel_name = self.channel_name
        await self.channel_layer.group_send(
            self.roomName, {
                'type':'videoStream',
                'data':bytes_data,
                'sender_channel_name':self.channel_name}
        )

        await self.video_process(bytes_data)
        ######################## setup recoding folder
        self.fps += self.tt.fps_calculate()
        self.fps /= 2.0
        # if self.process_write is None: await self.initializenewwriter()
        # await self.savebytestovideo(bytes_data)
        # print(self.fps, end='\r')



    async def videoStream(self, event):
        if self.channel_name != event['sender_channel_name']:
            image_bytes = event['data']
            await self.send(bytes_data=image_bytes)

# ##################################################################################################################################
    async def savebytestovideoContinous(self, imagebytes):
        if self.tt.time_pass_s(0.5 * self.MinuteTime) and self.process_write is not None:
            print("encoding the current video >>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>")
            self.process_write.stdin.close()
            self.process_write.wait()
            ############################# save the video Event to the data base
            await self.savevideotodb()
            await self.initializenewwriter()

        imgbuffer = np.frombuffer(imagebytes, dtype = np.uint8)
        img =  cv2.imdecode(imgbuffer, cv2.IMREAD_UNCHANGED)
        self.process_write.stdin.write(
           (cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
            .tobytes())
        )
        return img
    
    


    async def video_process(self, imagebytes):
        imgbuffer = np.frombuffer(imagebytes, dtype = np.uint8)
        img =  cv2.imdecode(imgbuffer, cv2.IMREAD_UNCHANGED)

        ################################### if there is motion detection
        if self.motion.detect(img):

            if not self.RECORDING_EN:
                self.RECORDING_EN = True
                await self.initializenewwriter()
                print('[RECODEING STARTED] motion detected recording started..')

            else:
                self.STOPED_DETECTION = False

            ##################################### Run the Object Detection Every 5 frames 
            self.framenumbertoskip += 1
            if self.skipframetoprocess <= self.framenumbertoskip:
                self.framenumbertoskip = 0
                objects_inframe = process_frame_objectDetectTask.delay(img).get()
                if len(objects_inframe) > 0:

                    if 'person' in objects_inframe:
                        face_recognized =  process_frame_faceRecogTask.delay(img).get()
                        #################### send the data to the clients 
                        await self.channel_layer.group_send(
                            'video_channel', {
                                    'type': 'task_recognize',
                                    'data': face_recognized
                                },    
                            )

                    ############################################################# Sending an Email
                    if self.SEND_EMAIL_ALREADY:
                        if self.tt.current_time() - self.EMAIL_TIMER_START >= self.EMAIL_STOP_TOLERANCE_IN_SECONDS:
                            self.SEND_EMAIL_ALREADY = False
                    
                    else:
                        self.SEND_EMAIL_ALREADY = True
                        self.EMAIL_TIMER_START = self.tt.current_time()
                        print("[EMAIL SEND] Email has been Send to the Host.")
                        sendemail_task.delay(subject= f"Motion Event Alert by {objects_inframe}",
                                    message= f"check the video feed there was {objects_inframe} \nmoving in front of the camera")               
        
        else: ### No Motion Detection
            if not self.STOPED_DETECTION and self.RECORDING_EN:
                self.STOPED_DETECTION = True
                self.TIMER_START = self.tt.current_time()
            
            elif self.STOPED_DETECTION:
                if self.tt.current_time() - self.TIMER_START >= self.STOP_TOLERANCE_IN_SECONDS:
                    self.RECORDING_EN = False
                    self.STOPED_DETECTION = False
                    print("[Write Video Done] the video has been Wwriten to the Disk.")
                    self.process_write.stdin.close()
                    self.process_write.wait()
                    await self.savevideotodb()


        if self.RECORDING_EN:         
            self.process_write.stdin.write(
                    (cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
                        .tobytes())
                )


  

    async def eventHandeller_notify(self, event):
        await self.channel_layer.group_send(
            'video_channel', {
                    'type': 'task_recognize',
                    'data': {
                        "event-type":event,
                    }
                },    
            )


    @sync_to_async  
    def IsItNightImage_async_process(self, image):
        return IsItNightImage(image, self.DayNightTresh, self.ImageWIDTH, self.ImageHEIGHT)


    @sync_to_async      
    def initializenewwriter(self):

        w, h = 640, 480 
        self.outputvideo = self.videosavefolder.joinpath(self.tt.format_time() + ".mp4")
        print(f"[Strat Video Write] initalize the writer with  {self.outputvideo}")
        self.process_write = (
            ffmpeg
                .input('pipe:',format='rawvideo', pix_fmt='rgb24', s=f'{w}x{h}')
                .output(str(self.outputvideo), pix_fmt='yuv420p', vcodec='libx264', r=self.fps, crf=31)
                .overwrite_output()
                .run_async(pipe_stdin=True)
        )
        

    @sync_to_async
    def savevideotodb(self):
        print("[VIDEO TO DB]saving the video to the database.")
        newvideorecord = RecordedVideosObjSerializer(
            data={
                "title" : str(self.outputvideo.parts[-1]), 
                "video_url" : f"{self.scope['server'][0]}/" + str(self.outputvideo) #DEBUG
            }
        )
        
        print("**"*20)
        print("**"*20)
        print(newvideorecord)
        print(newvideorecord.is_valid())
        if newvideorecord.is_valid():
            newvideorecord.save()
            print("[VIDEO DONE SAVING] the video record now in the api")



    async def task_recognize(self, event):
        facename  = event["data"]
        # Send message to WebSocket
        await self.send(
            text_data=json.dumps({
                'facename': facename
        }))

