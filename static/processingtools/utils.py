import itertools
import cv2
import time
import numpy as np
import os


# https://stackoverflow.com/questions/11721818/django-get-the-static-files-url-in-view/59355195#59355195
from django.templatetags.static import static ##production
from django.contrib.staticfiles.finders import find ##debug




def readfromfile():
    filename = find("hello.txt")
    with open(filename) as f:
        content = f.read()
    print("*"*30)
    print(content)





def decode_byte_frame(framebytes: bytes) -> np.ndarray:
    '''function that convert binary image(bytes) to numpy array'''
    arr =  np.frombuffer(framebytes, dtype=np.int8) # convert bytes into array of int8
    imgarr =  cv2.imdecode(arr, cv2.IMREAD_COLOR)
    return imgarr



################################################################################
class TimeTracker:
    def __init__(self) -> None:
        ''' set a banch of time marker to use '''
        self.startProgram = time.time()
        self.primetime = time.time()
        self.ptime2 = time.time()
        self.ptime3 = time.time()
    
    def current_time(self) -> float:
        return time.time()

    def fps_calculate(self) -> float:
        fps = 1 / (self.current_time() - self.primetime)
        self.primetime = self.current_time()
        return fps
    
    def format_time(self, format: str="%y_%m_%d_%H_%M_%S") -> str:
        return time.strftime(format, time.localtime(self.current_time()))

    def time_pass(self, time_pass_ms: int) -> bool:
        if (self.current_time() - self.ptime2)*1000.0 > time_pass_ms:
            self.ptime2 = self.current_time()
            return True

    def time_pass_s(self, time_pass: int) -> bool:
        if (self.current_time() - self.ptime3) > time_pass:
            self.ptime3 = self.current_time()
            return True





################################################################# Generic DeepLearing Class
class DiNet:
    def __init__(self, modelpath: str, modelconfig:str =None, framework="Caffe", computebackend:str =None):
        
        self.net = cv2.dnn.readNet(model=modelpath,config=modelconfig,
            framework=framework)
        if computebackend == 'cuda': self.useComputeBackenCuda()


    def useComputeBackenCuda(self): 
        self.net.setPreferableBackend(cv2.dnn.DNN_BACKEND_CUDA)
        self.net.setPreferableTarget(cv2.dnn.DNN_TARGET_CUDA) 


    def passInput(self ,netInput):
        self.net.setInput(netInput)
        return self.net.forward()

###############################################################################
class FaceDetector:
    def __init__(self, compute_backend=None):
        # print(os.getcwd())
        modelweights = find("mlmodels/res10_300x300_ssd_iter_140000_fp16.caffemodel") # model paramters
        modelconfig= find("mlmodels/res10_structure_paramters.prototxt") # model layers configs

        self.facenetModel = DiNet(modelconfig, modelweights, computebackend=compute_backend)
        self.detectedfaces = []
        self.AppendFace = self.detectedfaces.append

    
    def detect(self, frame, threshold=0.6, Width=640, Height=480):
        self.detectedfaces.clear()
        imBlob = cv2.dnn.blobFromImage(cv2.resize(frame,(300,300)), 1.0,
            size=(300,300),
            mean=(104.0, 177.0, 123.0))
        predictedfaces = self.facenetModel.passInput(imBlob)
        for i in range(predictedfaces.shape[2]):
            preds_confdence = predictedfaces[0,0,i,2]
            if preds_confdence >= threshold:
                boundingBox = predictedfaces[0,0,i,3:7] * np.array([Width,Height,Width,Height])
                (x, y, boxwidth, boxheight) = boundingBox.astype('int')
                self.AppendFace([x,y,boxwidth,boxheight])
        return self.detectedfaces





def peektoGenerator(iterable):
    try: firstobj = next(iterable)
    except StopIteration:
        return None
    return firstobj, itertools.chain([firstobj], iterable) ##### chain list of iterable



#################################################################################
class MotionDetection:
    def __init__(self, history=100, mthreshold=40, drawOnImage=None) -> None:
        self.motiondetector = cv2.createBackgroundSubtractorMOG2(history=history, varThreshold=mthreshold)
        self.mincntArea = 3000
        self.drawOnImage = drawOnImage
        self.fontStyle = cv2.FONT_HERSHEY_SIMPLEX
        self.color =  (0,0,255)

    def detect(self, frame):
        mask = self.motiondetector.apply(frame)
        contours, _ = cv2.findContours(mask, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)
        contours = (c for c in contours if cv2.contourArea(c) > self.mincntArea)      
        
        cntsIterObj = peektoGenerator(contours)
        if cntsIterObj is None: return False
        if self.drawOnImage:
            for c in contours:
                x, y, w, h = cv2.boundingRect(c)
                cv2.rectangle(frame, (x, y), (x+w, y+h), (0, 0, 255), 2)
                text = "Status: Movement"            
                cv2.putText(frame, text,(10, 20), self.fontStyle, 1, self.color, 2)
        return True




################################################################## face emedder
class FaceEmbedder:
    def __init__(self, compute_backend=None):
        openfacepath = find("mlmodels/nn4.small2.v1.t7")
        self.embedder = DiNet(modelpath=openfacepath, framework="PyTorch", computebackend=compute_backend)


    def embedFace(self, faceRoI):
        ''':faceRoI: RGBimage'''
        imBlob = cv2.dnn.blobFromImage(faceRoI, 1.0/255,
            (96, 96), (0,0,0),swapRB=True, crop=False)
        return self.embedder.passInput(imBlob)




######################################################## DAY & NIGHT DETECTION
def IsItNightImage(frame, threshhold, width , height):
    hsvImage = cv2.cvtColor(frame, cv2.COLOR_RGB2HSV)
    Brightness = hsvImage[:,:,2]
    averageBrightness = np.sum(Brightness) / (width * height)
    # print(averageBrightness)
    if averageBrightness < threshhold:
        return True
    return False