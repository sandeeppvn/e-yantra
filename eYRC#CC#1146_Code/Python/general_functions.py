import cv2
import numpy as np
import time
import serial
from math import sqrt

# Connect to Xbee
ser = serial.Serial(port = 'COM3', baudrate = 9600, bytesize = serial.EIGHTBITS, parity = serial.PARITY_NONE, stopbits = serial.STOPBITS_ONE, timeout = 1)

##########################################################################

############################ GENERAL FUNCTIONS ###########################

#### Color-Contour Functions ####
#Function to crop out only the arena


'''
*Function Name: get_perspective_image
*Input: frame -> image obtained from camera
*Output: img -> image obtained after cropping the rest of the noise
*Logic: It gives us the image after cropping out rest of the area except the arena
*Example Call: get_perspective_image(frame)
'''
#Helper function for get_crop()
def get_perspective_image(frame):
    #cv2.imshow("frame1",frame)

    
    gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
    lower = np.array([0, 0, 0]) #black color mask
    upper = np.array([50, 50, 50])
    mask = cv2.inRange(frame, lower, upper)


    ret,thresh1 = cv2.threshold(mask,127,255,cv2.THRESH_BINARY)
    contours, hierarchy = cv2.findContours(thresh1, cv2.RETR_LIST, cv2.CHAIN_APPROX_SIMPLE)
    contours.sort(key=len,reverse=True)
    

    if(len(contours)>1):
        # print len(contours),":len"
        print cv2.contourArea(contours[1])
        if( int(cv2.contourArea(contours[1])) > 100000 and int(cv2.contourArea(contours[1])) < 185000):
            biggest = 0
            max_area = 0
            min_size = thresh1.size/4
            index1 = 0
            for i in contours:
                area = cv2.contourArea(i)
                if area > 10000:
                    peri = cv2.arcLength(i,True)
                if area > max_area: 
                    biggest = index1
                    max_area = area
                index1 = index1 + 1

            approx = cv2.approxPolyDP(contours[1],0.05*peri,True)
            #drawing the biggest polyline
            # cv2.polylines(frame, [approx], True, (0,255,0), 3)
            x1 = approx[0][0][0]
            y1 = approx[0][0][1]
            x2 = approx[1][0][0]
            y2 = approx[1][0][1]
            x3 = approx[3][0][0]
            y3 = approx[3][0][1]
            x4 = approx[2][0][0]
            y4 = approx[2][0][1]
            '''
            print x1, y1
            print x2, y2
            print x3, y3
            print x4, y4
            '''
            
            
            #points remapped from source image from camera
            #to cropped image try to match x1, y1,.... to the respective near values
            #you may need to edit below code to your own need
            #for LM
            # pts1 = np.float32([[x2,y2],[x4,y4],[x1,y1],[x3,y3]]) 
            # pts2 = np.float32([[0,0],[0,480],[540,0],[540,480]])#remarking each four side of the cropped image
            # persM = cv2.getPerspectiveTransform(pts1,pts2)
            # dst = cv2.warpPerspective(frame,persM,(540,480))#setting output image resolution
            #for CC
            # pts1 = np.float32([[x3,x3],[x1,x1],[x4,x4],[x2,x2]]) 
            # pts2 = np.float32([[0,0],[0,480],[320,0],[320,480]])
            # persM = cv2.getPerspectiveTransform(pts1,pts2)
            # img = cv2.warpPerspective(frame,persM,(320,480))
            min_x = min(x1,x2,x3,x4)
            max_x = max(x1,x2,x3,x4)
            min_y = min(y1,y2,y3,y4)
            max_y = max(y1,y2,y3,y4)

            img = frame[min_y:max_y,min_x:max_x]
            return img
    return



'''
*Function Name: get_crop
*Input: none
*Output: img_src -> image obtained after cropping the rest of the noise away from the arena
*Logic: It gives us the image after cropping out rest of the area except the arena
*Example Call: get_crop()
'''
#Obtain a cropped off black part image
def get_crop():

    cap = cv2.VideoCapture(0)
    time.sleep(5)
    
    ret, src = cap.read()
  
    while(1):

        
        if(ret == True ):

                
            #getting the perspective image
            img_src= get_perspective_image(src)
            
            #cv2.imwrite("output_image.jpg", img_src)
            if(img_src == None):
                ret, src = cap.read()
                continue
            else:
                
                return img_src
                
            ## Close and exit

    ############################################




'''
*Function Name: get_contours
*Input: mask -> the masked matrix from inRange
*Output: contours -> The list of contours corresponding to the mask
*Logic: It gives us a list of contours based on the mask which is set to detect sertain colors, uses inbuilt opencv functions
*Example Call: get_colors(im,light)
'''
#Function to get the boundaries of mask
def get_contour(mask):
    ret,thresh = cv2.threshold(mask,127,255,cv2.THRESH_BINARY)
    contours,hierarchy = cv2.findContours(thresh, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)
    return contours;





'''
*Function Name: display
*Input: im,res,cavities,obstacles,bot ->the actual image, masked with contours image, list of cavities, obstacles and bot circles
*Output: cavities-> it is a list which contains the coordinates and radius of each cavity, obstacles-> it is a list which contains the coordinates and radius of each obstacle
*Logic: It is a display function for providing an interface
*Example Call: display(im,res,cavities,obstacles,bot)
'''
#Function to display values
def display(im,res,cavities,obstacles,bot):

    #Display image
    cv2.imshow('res',res)

    print "Cavities"
    for i in cavities:
        print i
    print
    print
    print
    print "Obstacles"
    for i in obstacles:
        print i
    print
    print
    print
    print "BOTs"
    for i in bot:
        print i
       

    cv2.waitKey(0)
