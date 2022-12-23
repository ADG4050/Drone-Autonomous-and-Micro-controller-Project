#CPS-Group1
#code for handtracking found through:  https://www.section.io/engineering-education/creating-a-hand-tracking-module/
import cv2
import mediapipe as mp
import logging
import time 
import cflib.crtp
from cflib.crazyflie import Crazyflie
from cflib.crazyflie.syncCrazyflie import SyncCrazyflie
from cflib.utils import uri_helper 
from cflib.positioning.position_hl_commander import PositionHlCommander
from cflib.crazyflie.log import LogConfig
from cflib.crazyflie.syncLogger import SyncLogger

uri = uri_helper.uri_from_env(default = 'radio://0/80/2M/5C21CF0101')
DEFAULT_HEIGHT = 0
logging.basicConfig(level=logging.ERROR)

#Hand tracking class
class handTracker():
    def __init__(self, mode=False, maxHands=4, detectionCon=0.5,modelComplexity=1,trackCon=0.5):
        self.mode = mode
        self.maxHands = maxHands
        self.detectionCon = detectionCon
        self.modelComplex = modelComplexity
        self.trackCon = trackCon
        self.mpHands = mp.solutions.hands
        #Media pipe hand tracking AI-inference
        self.hands = self.mpHands.Hands(self.mode, self.maxHands,self.modelComplex,
                                        self.detectionCon, self.trackCon)
        self.mpDraw = mp.solutions.drawing_utils
    # finds hands through media pipe
    def handsFinder(self,image,draw=True):
        imageRGB = cv2.cvtColor(image,cv2.COLOR_BGR2RGB)
        self.results = self.hands.process(imageRGB)

        if self.results.multi_hand_landmarks:
            for handLms in self.results.multi_hand_landmarks:

                if draw:
                    self.mpDraw.draw_landmarks(image, handLms, self.mpHands.HAND_CONNECTIONS)
        return image
    #Extracts coordinates of index fingers
    def positionFinder(self,image, handNo=0, draw=True):
        lmlist = []
        if self.results.multi_hand_landmarks:
            Hand = self.results.multi_hand_landmarks[handNo]
            for id, lm in enumerate(Hand.landmark):
                h,w,c = image.shape
                cx,cy = int(lm.x*w), int(lm.y*h)
                lmlist.append([id,cx,cy])
                if(id%4==0):
                    if(id!=0):
                        if draw:
                            cv2.circle(image,(cx,cy), 15 , (255,0,255), cv2.FILLED)
        return lmlist

#Behaves like a 3-tap fir filter leading to a average like behavior
def average(a,list):
    if(abs(a-list)>2):
        return 0.8*list
    elif(abs(a-list)>1):
        return 0.9*list
    else:    
        return list



def main():

    #initialise
    cflib.crtp.init_drivers()
    cap = cv2.VideoCapture(0)
    tracker = handTracker()

    #initialise parameters
    a = [512//100,512//100]#middle value
    b = [512//100,512//100]
    avg = [512//100,512//100]
    avg2=[512//100,512//100]
    height = 0.1
    time_start = time.time()+10

    #connecting to drone
    try:
        #comment the below 2 lines for testing the tracking
        with SyncCrazyflie(uri, cf=Crazyflie(rw_cache='./cache')) as scf:
            with PositionHlCommander(scf, controller=PositionHlCommander.CONTROLLER_PID) as pc:

        #uncomment if the above 2 lines are commented
        # if(True):
        #     if(True):
                # scf.cf.commander.send_hover_setpoint(0,0,0,0)
                while True:
                    success,image = cap.read()
                    image = tracker.handsFinder(image)

                    try: # find 2 hands and set the parameters
                        lmList = tracker.positionFinder(image,0)
                        lmList2 = tracker.positionFinder(image,1)
                        
                        a = [average(a[0],lmList[8][1]//50),average(a[1],lmList[8][2]//50)]
                        b = [average(b[0],lmList2[8][1]//50),average(b[1],lmList2[8][2]//50)]
                        print("2 hands")

                    except: # test for 1 and no hands

                        try: # find 1 hand
                            lmList = tracker.positionFinder(image,0)
                            a = [average(a[0],lmList[8][1]//50),average(a[1],lmList[8][2]//50)]
                            b = [512//100,512//100]
                            print("1 hand")

                        except: # there are no hands
                            a=[512//100,512//100]
                            b=[512//100,512//100]
                            print("0 hands")
    
                    avg = [a[0]*100,1024-a[1]*100] #yaw and height rate
                    avg2 = [b[0]*100,1024-b[1]*100] #roll and pitch

                    #convertion from pixel to vectors
                    yaw = avg[0]
                    pitch = avg2[1]     #y axis
                    roll = avg2[0]  #x axis

                    height_rate = ((avg[1]-512)/725)
                    roll_rate =round( (roll-300)/(725*2), 3)
                    pitch_rate = round((pitch-575)/(725*2), 3)
                    yaw_rate = round(-(yaw-900)/(1024/100),3)

                    #display video with text for understanding where thrust, pitch, roll, and yaw axis is.
                    cv2.putText(image, text='+ve height', org=(350, 50), fontFace=cv2.FONT_HERSHEY_TRIPLEX, fontScale=1, color=(0, 0, 0),thickness=1)
                    cv2.putText(image, text='-ve height', org=(350, 450), fontFace=cv2.FONT_HERSHEY_TRIPLEX, fontScale=1, color=(0, 0, 0),thickness=1)
                    cv2.putText(image, text='yaw', org=(550, 250), fontFace=cv2.FONT_HERSHEY_TRIPLEX, fontScale=1, color=(0, 0, 0),thickness=1)
                    cv2.putText(image, text='pitch', org=(100, 50), fontFace=cv2.FONT_HERSHEY_TRIPLEX, fontScale=1, color=(0, 0, 0),thickness=1)
                    cv2.putText(image, text='roll', org=(1, 250), fontFace=cv2.FONT_HERSHEY_TRIPLEX, fontScale=1, color=(0, 0, 0),thickness=1)
                    cv2.imshow("Video",image)
                    cv2.waitKey(1)
                    time.sleep(0.01)

                    #create zone for relaxing fingers
                    if(height_rate<0.1 and height_rate>-0.1):
                        height_rate = 0 

                    if(pitch_rate<0.05 and pitch_rate>-0.05):
                        pitch_rate = 0

                    if(roll_rate<0.07 and roll_rate>-0.07):
                        roll_rate = 0

                    if(yaw_rate<10 and yaw_rate>-10):
                        yaw_rate = 0

                    #increase height based of height rate
                    height_rate = height_rate/50.0
                    height = round(height + height_rate,3)
                    if(height<0):
                        height = 0
                    
                    print("Height is: {} m, height_rate: {} m/s, pitch rate: {} m/s, roll rate: {} m/s, yaw: {} degree/s".format(height,round(height_rate,3), pitch_rate, roll_rate,yaw_rate))
                    
                    #send data to drone
                    if(height>0.05):
                        print("running\n")
                        try:
                            scf.cf.commander.send_hover_setpoint(pitch_rate,roll_rate,yaw_rate,height)
                        except:
                            x=1
                    else:
                        print("not running\n")
                        try:
                            scf.cf.commander.send_hover_setpoint(0,0,0,0)
                        except:
                            x=1
                    #end video feed
                    if(cv2.getWindowProperty("Video", cv2.WND_PROP_VISIBLE)<1):
                        break

                cv2.destroyAllWindows()
    except:
        print(" couldnt connect to drone.... try again ")
        time.sleep(1)
        

        

if __name__ == "__main__":
    main()
