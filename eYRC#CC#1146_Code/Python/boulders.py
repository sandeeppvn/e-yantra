import cv2
import numpy as np
import time
import serial
from math import sqrt

# Connect to Xbee
ser = serial.Serial(port = 'COM3', baudrate = 9600, bytesize = serial.EIGHTBITS, parity = serial.PARITY_NONE, stopbits = serial.STOPBITS_ONE, timeout = 1)

#Function to get the boulder values and positions

''' 
*Function Name: get_boulders
*Input: im -> the captured and cropped image
*Output: boul -> The list of number and position of the boulders identified in im
*Logic: We apply template mathcing with previoously defined templates to detect the best matched numbers and obtain the numbers on the boulders
*Example Call: get_boulders(im)
'''
def get_boulders(im):

    boulder = []

    #make sure template images are grayscale
    
    zero = cv2.imread('digits/0.jpg',0)
    one = cv2.imread('digits/1.jpg',0)
    two = cv2.imread('digits/2.jpg',0)
    three = cv2.imread('digits/3.jpg',0)
    four = cv2.imread('digits/4.jpg',0)
    five = cv2.imread('digits/5.jpg',0)
    six = cv2.imread('digits/6.jpg',0)
    seven = cv2.imread('digits/7.jpg',0)
    eight = cv2.imread('digits/8.jpg',0)
    nine = cv2.imread('digits/9.jpg',0)


    temp = [[zero,0],[one,1],[two,2],[three,3],[four,4],[five,5],[six,6],[seven,7],[eight,8],[nine,9]]
    # temp = [zero,one,seven,eight]

    #generate grayscale from rgb
    im = cv2.cvtColor(im, cv2.COLOR_BGR2GRAY)

    #remove noise from the image
    #im = cv2.fastNlMeansDenoising(im)
   
    #Iterate through all numbers and check which number is there using template matching    
    i=-1
    for templ in temp:
        
        template = templ[0]
        w, h = template.shape[::-1]
        res = cv2.matchTemplate(im,template,cv2.TM_CCOEFF_NORMED)
        loc = np.where( res >= template_threshold)
        for pt in zip(*loc[::-1]):
            
            min_val, max_val, min_loc, max_loc = cv2.minMaxLoc(res)
            t = [ templ[1] , pt[0]+w/2,pt[1]+h/2 ,max_val,w,h]
            boulder.append(t)
        # min_val, max_val, min_loc, max_loc = cv2.minMaxLoc(res)
        # top_left = max_loc
        # bottom_right = (top_left[0] + w, top_left[1] + h)

    bould = []
    for b in boulder:
        if(len(bould)==0):
            # print b,"start"
            bould.append(b)
        else:
            # print b,"main"
            sug=0
            for i in bould:
                if(sqrt(  (i[1]-b[1])**2 + (i[2]-b[2])**2  ) < thresh ):
                    # print b, i[2]-b[2]
                    sug=1
            if(sug==0):
                bould.append(b)


    for i in bould:
        print i,":num"
        cv2.rectangle(im, (i[1]-i[4]/2,i[2]-i[5]/2)  ,  (i[1]+i[4]/2,i[2]+i[5]/2)  ,  (0,255,255) , 2)

            
   
    
        
    cv2.imshow("img",im)
    cv2.waitKey(0)
        

   
        # print max_val,templ[1]
        # if(max_val > template_threshold):
        #     print max_val,templ[1],"!!!!!"
        #     cv2.line(im,top_left,bottom_right,(0,255,255),2)
        #     cv2.imshow("img",im)
        #     cv2.waitKey(0)
        #     t =[templ[1] , (top_left[0]+bottom_right[0])/2 , (top_left[1]+bottom_right[1])/2 ]
        #     boulder.append(t)        

    #return bould
    return boul