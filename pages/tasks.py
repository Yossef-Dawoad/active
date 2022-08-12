from __future__ import absolute_import, unicode_literals
import csv

import os
import pickle
from pathlib import Path
from random import randint
import numpy as np
from celery import shared_task
import cv2


from static.processingtools.utils import FaceDetector, FaceEmbedder
from django.contrib.staticfiles.finders import find ##debug

from static.processingtools.utils import TimeTracker
import uuid

################# accesing the channel layer
from channels.layers import get_channel_layer
from asgiref.sync import async_to_sync








####################################### initializing detectors and recognizer 
facedetecotor = FaceDetector()
facedembedder = FaceEmbedder()
########################### Recognizer Model
with open(find("./mlmodels/trained_reconizer&embeddings.pickle"),"rb") as pf:
    data = pickle.load(pf)
faceRecognizer = data["recognizer"]
labelEncoder = data["labelencoder"]
print("[COMPLETED] models has been Loaded.")
##############################################################################
nightfolder = Path("./static/recordings/images/dayNightDataSet/Nighttime")
nightfolder.mkdir(exist_ok=True)

dayfolder = Path("./static/recordings/images/dayNightDataSet/Daytime")
dayfolder.mkdir(exist_ok=True)

dayimagecounter = 0
nightimagecounter = 0


tt = TimeTracker()
############################################ image day and night setup
#######FEATURE SCHUDLE task every three days to change the value 
def saveimagefordayandnight(img):

    fileName = None
    TIME_NOW = int(tt.format_time("%H"))

    if TIME_NOW > 7 and TIME_NOW < 16: #### Day Time
        fileName = f"./static/recordings/images/dayNightDataSet/Nighttime/{uuid.uuid4()}.jpg"
        cv2.imwrite(fileName, img)
        imageLabel = 1

    elif TIME_NOW > 20 and TIME_NOW < 5: #### Day Time
        fileName = f"./static/recordings/images/dayNightDataSet/Nighttime/{uuid.uuid4()}.jpg"
        cv2.imwrite(fileName, img) ######! chaeck RGB OR BGR
        imageLabel = 0

    if fileName is not None:
        record = [fileName, imageLabel]
        with open("./static/recordings/images/dayNightDataSet/dayandNightLookup.csv", 'a+') as csvf:
            fwriter = csv.writer(csvf, delimiter=',')
            fwriter.writerow(record)


#####################################################


@shared_task
def makeimagetovideo_Task(foldername, fps):
    print("[ENCODE] encoding images...... ")
    os.system(f"""ffmpeg -r {fps} -i ./static/recordings/images/{foldername}/tempimage_%d.jpeg \
                -vcodec libvpx-vp9 ./static/recordings/videos/outputvideo_{foldername}.webm 
                """)
    os.system(f"rm --force --recursive ./static/recordings/images/{foldername}")
    ############################ save to the database
    # from models import Videos
    # Videos.objects.create(title=f"outputvideo_{foldername}.webm", 
    #                         url='/static/recordings/videos/').save()







@shared_task
def process_frame_Task(frame):
    facedetected = facedetecotor.detect(frame)
    ###################################face-recognitions
    facesreconized = []
    if facedetected:
        # print("face has been detected")
        for (x, y, facewidth, faceheight) in facedetected:
            faceROI = frame[y:faceheight, x:facewidth]
            faceVecId = facedembedder.embedFace(faceROI)
            predictedsvmnames = faceRecognizer.predict_proba(faceVecId)[0] # svm prediction of the embeds
            nameId_index = np.argmax(predictedsvmnames)
            faceName = labelEncoder.classes_[nameId_index]
            facesreconized.append(faceName)
        
        #################### save the event
        
        

        #################### send the data to the clients browser
        channel_layer = get_channel_layer()
        async_to_sync(channel_layer.group_send)(
            'video_channel', {
                    'type': 'task_recognize',
                    'data': facesreconized
                },    
            )
        # return facesreconized

#############################################################################################
#############################################################################################
#############################################################################################
@shared_task
def process_frame_faceRecogTask(frame):
    facedetected = facedetecotor.detect(frame)
    ###################################face-recognitions
    facesreconized = []
    if facedetected:
        # print("face has been detected")
        for (x, y, facewidth, faceheight) in facedetected:
            faceROI = frame[y:faceheight, x:facewidth]
            faceVecId = facedembedder.embedFace(faceROI)
            predictedsvmnames = faceRecognizer.predict_proba(faceVecId)[0] # svm prediction of the embeds
            nameId_index = np.argmax(predictedsvmnames)
            faceName = labelEncoder.classes_[nameId_index]
            facesreconized.append(faceName)

        #################### send the data to the clients browser
        # channel_layer = get_channel_layer()
        # async_to_sync(channel_layer.group_send)(
        #     'video_channel', {
        #             'type': 'task_recognize',
        #             'data': facesreconized
        #         },    
        #     )
        return facesreconized

    return None


from static.processingtools.utils import ObjectDetection

objdetector = ObjectDetection()
cococlasses = objdetector.cocoClasses
randint(0,255)
classColors = [(randint(0,255), randint(0,255), randint(0,255)) for _ in range(91)]

@shared_task
def process_frame_objectDetectTask(frame) -> (list | None):
    objs_Iter = objdetector.findObj(frame,confidance= 0.7)
    ###################################face-recognitions

    objects_in_frame = [cococlasses[labelIdx] for labelIdx, _, _ in objs_Iter]
    print(f"object is not none {objects_in_frame}")
    return objects_in_frame




#############################################################################################
#############################################################################################
#############################################################################################


###################################################### send email

from django.core.mail import send_mail, EmailMultiAlternatives
from django.template.loader import render_to_string
from django.utils.html import strip_tags
from project.settings import EMAIL_HOST_USER

@shared_task
def sendemail_task(subject:str , message:str, recipient:list= ['yousef36293@engmet.edu.eg']):
    print("sending email.....")
    send_mail(
        subject=subject,
        message=message,
        from_email= EMAIL_HOST_USER,
        recipient_list=[*recipient],
        fail_silently=False
    )
    print("email has been send.")
    return True




@shared_task
def sendemail_template(context_data, recipient:list= ['yousef36293@engmet.edu.eg']):

    context = {'data':context_data}
    emailbody = strip_tags(render_to_string("pages/email_template.html", context))

    (EmailMultiAlternatives(
        subject="Face Detected in your Nigborhood",
        message=emailbody,
        from_email= EMAIL_HOST_USER,
        recipient_list=[*recipient],
        fail_silently=False
    ).attach_alternative(emailbody, "text/html")
    .send() )
