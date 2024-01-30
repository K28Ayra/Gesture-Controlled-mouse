import cv2
from cvzone.HandTrackingModule import HandDetector
import mouse  ##to get the size of the screen
import numpy as np
import threading
import time


detector = HandDetector(detectionCon=0.9, maxHands=1)

cap = cv2.VideoCapture(0)
wcam, hcam = 640, 480
cap.set(3, wcam)
cap.set(4, hcam)


frameR = 50
l_delay = 0
r_delay = 0
dbl_delay = 0

def l_clk_delay():
    global l_delay
    global l_clk_thread
    time.sleep(1)
    l_delay=0
    l_clk_thread = threading.Thread(target=l_clk_delay)

def r_clk_delay():
    global r_delay
    global r_clk_thread
    time.sleep(1)
    r_delay = 0
    r_clk_thread = threading.Thread(target=r_clk_delay)

def dbl_clk_delay():
    global dbl_delay
    global dbl_clk_thread
    time.sleep(2)
    dbl_delay=0
    dbl_clk_thread= threading.Thread(target=dbl_clk_delay)

l_clk_thread = threading.Thread(target= l_clk_delay)
r_clk_thread = threading.Thread(target= r_clk_delay)
dbl_clk_thread = threading.Thread(target=dbl_clk_delay)




while True:
    success, img = cap.read()
    img = cv2.flip(img, 1)
    hands, img = detector.findHands(img, flipType= False)
    cv2.rectangle(img, (frameR,frameR), (wcam-frameR, hcam-frameR), (255,0,255) , 3)

    ##mouse movement: tip of index finger will be used to control the movement of mouse. Landmark for it is 8, check landmark file
    if hands and 'lmList' in hands[0]:
        lmlist = hands[0]['lmList']

        # Extract x and y co. of tip of the index finger, its finger lndmark is 8
        if len(lmlist) >= 9:
            x_ind, y_ind = lmlist[8][0], lmlist[8][1]
            x_mid, y_mid = lmlist[12][0], lmlist[12][1]

            cv2.circle(img, (x_ind, y_ind), 8, (200,0,240), cv2.FILLED)
            finger = detector.fingersUp(hands[0])        #return array of 0 if all fingers closed else 1. note: But since we have flipped te img horizontally, our thunb is 1 when closed and 0 when open
            #print(finger)

            ###########
            #Thers is a problem of jittering when we reach the end of screen both horzontally and vertically
            ###########solve'em:  reduce the framesize ie making a miniature version of the screen
            ##reduce it by 100, 640-100= 540, 840-100= 740
            ##introduced frameR


            #mouse movement
            if finger[1]==1 and finger[2]==0 and finger[0]==1:     #conv_x and y calculates position of tip of index finger in the web cam
                conv_x = int(np.interp(x_ind, (frameR, wcam - frameR), (0, 1536)))   ##interp: since the webcam feed and screen resolution differes, we use it to range the web cam to screen resolution
                conv_y = int(np.interp(y_ind, (frameR, hcam - frameR), (0, 864)))
                mouse.move(conv_x, conv_y)


            #mouse click
            if finger[1]==1 and finger[2]==1 and finger[0]==1:
                if abs(x_ind-x_mid) < 25:
                    ##when middle and ind fingers are up and distance between them is very less

                        ##left click
                        if finger[4]==0 and l_delay==0:
                            mouse.click(button="left")
                            l_delay = 1
                            l_clk_thread.start()

                            ##right click  : oinky finger up
                        if finger[4] == 1 and r_delay == 0:
                            mouse.click(button="right")
                            r_delay = 1
                            r_clk_thread.start()


            ##mouse scrolling
            if finger[1]==1 and finger[2]==1 and finger [0]==0 and finger[4]==0:
                #if (x_ind-x_mid) < 25:
                    mouse.wheel(delta=-1)  ##down scrolling

            if finger[1]==1 and finger[2]==1 and finger [0]==0 and finger[4]==1:  ##pinky up
                #if (x_ind-x_mid) < 25:
                    mouse.wheel(delta=1)  ##up scrolling


            ##double click
            if finger[1] ==1 and finger[2]==0 and finger[4]==0 and finger[0]==0 and dbl_delay ==0:
                dbl_delay=1
                mouse.double_click(button="left")
                dbl_clk_thread.start()


    cv2.imshow("Image", img)
    cv2.waitKey(1)





    ###########SUMMARYYYYYYY

    #left click: Index finger and middle finger touching each other
    #right click:  Index finger and middle finger touching each other with pinky finger up.
    #double click: index finfer and thumbs up
    #scroll: index,middle and thumbs up, with pinky up scrolls up and pinky downs scrolls down.