'''
*Function Name: task5-main
*Logic: Contains the logic used to implement the theme depending on the number of boulders, position of obstacles,Sum etc by image processing using contours
''' 
import cv2
import numpy as np
import time
import serial
from math import sqrt
import general_functions as gf
import color as col
import boulders as gb
import navigation_functions as nf

# Connect to Xbee
ser = serial.Serial(port = 'COM3', baudrate = 9600, bytesize = serial.EIGHTBITS, parity = serial.PARITY_NONE, stopbits = serial.STOPBITS_ONE, timeout = 1)

#############GLOBAL VARIABLE##############################################
light = 1

#0 - Day light, all covered
#1 - Artificial light, all covered, only CFL


shape = []
endpoint= []
center_point=[]
bridge1_start=[]
bridge1_end=[]
bridge2_start=[]
bridge2_end=[]
img_left = []
img_right = []
bridge1_left = 0
bridge1_right = 0
bridge2_left = 0
bridge2_right = 0


threshold=5

# template_threshold=0.85
template_threshold = 0.82
thresh = 3


##########################################################################
'''
*Function Name: main
*Input: none
*Output: none
*Logic: It defines the flow of the entire program and is the start of the program
*Example Call: main()
'''
def main():

    #Get one frame for preprocessing
    #crop the image to border
    frame = get_crop()  
    cv2.imwrite("check.jpg",frame)
    cv2.waitKey(0)
    print "check crop"
    print "+++++++++++++++++++++++++++++++++++++++++++++++++++++++++++"

    global center_point 
    global endpoint 
    global bridge1_start
    global bridge1_end
    global bridge2_start
    global bridge2_end
    global bridge1_left 
    global bridge1_right
    global bridge2_left 
    global bridge2_right


    center_point = [ 0.4375*frame.shape[0],0.85714*frame.shape[1] ]
    endpoint = [ 0.4375*frame.shape[0],0.09286*frame.shape[1] ]
    bridge1_start = [ 0.1875*frame.shape[0],0.60714*frame.shape[1] ]
    bridge1_end = [ 0.1875*frame.shape[0],0.17857*frame.shape[1] ]
    bridge2_start = [ 0.75*frame.shape[0],0.60714*frame.shape[1] ]
    bridge2_end = [ 0.75*frame.shape[0],0.1607*frame.shape[1] ]
    bridge1_left =  0.3210*frame.shape[0]
    bridge1_right =  0
    bridge2_left =  frame.shape[0]
    bridge2_right = 0.5432*frame.shape[0]





    #remove noise
    #frame=cv2.fastNlMeansDenoisingColored(frame)

    
    
    #Get the boulder number and position using template matching
    boulder = get_boulders(frame)
    print boulder

    b1 = boulder[0][0]
    b1_pos = (boulder[0][1],boulder[0][2])
    b2 = boulder[1][0]
    b2_pos = (boulder[1][1],boulder[1][2])
    b3 = boulder[2][0]
    b3_pos = (boulder[2][1],boulder[2][2])
    b4 = boulder[3][0]
    b4_pos = (boulder[3][1],boulder[3][2])
    print boulder
    print "check-boulders"
    print "+++++++++++++++++++++++++++++++++++++++++++++++++++++++++++"

    #start image processing using contours
    #get position of cavities,boulders and bot
    cv2.imwrite("test.jpg",frame)
    colors = get_colors(frame,light)
    #Cavities present on both bridges
    cavity = colors[0]
    #Obstacles position on bridge 2    
    obstacle = colors[1]
    print cavity
    print obstacle
    print "check-cavity and obstacles"
    print "+++++++++++++++++++++++++++++++++++++++++++++++++++++++++++"
    

    #count
    br1_cav = 0     #no of cavities on bridge 1
    br2_cav = 0     #no of cavities on bridge 2
    cavity1 = []    #Array with bridge 1 cavitites
    cavity2 = []    #Array with bridge 2 cavities
    
    for cav in cavity:
        if (cav[0] > 200 ):
            br1_cav+=1
            cavity1.append(cav)
        else:
            br2_cav+=1
            cavity2.append(cav)

    print "!!!"
    print br1_cav
    print br2_cav
    print "!!!"


    print "check-no of cavities on each bridge"
    print "+++++++++++++++++++++++++++++++++++++++++++++++++++++++++++"

    cv2.destroyAllWindows()


    #input Sum
    numb = input("Enter the Sum:")
    print numb

    #numb for testing
    #numb=15
    
    ######### 4 Boulders ############
    # if( (b1+b2+b3+b4) == numb and br1_cav == 4):
    #     print "b1+b2+b3+b4"
    #     bridge1(b1_pos,b2_pos,b3_pos,b4_pos,cavity1,obstacle)

    ######### 3 Boulders ############
    
    # elif( (b1+b2+b3) == numb ):
    if( (b1+b2+b3) == numb ):
        print "b1+b2+b3"
        b4_pos = -1
        print br1_cav
        if(br1_cav ==3):
            bridge1(b1_pos,b2_pos,b3_pos,b4_pos,cavity1,obstacle)
        # elif(br2_cav ==3):
            bridge2(b1_pos,b2_pos,b3_pos,b4_pos,cavity2,obstacle)

    elif( (b1+b2+b4) == numb ):
        print "b1+b2+b4"
        b3_pos = -1
        if(br1_cav ==3):
            bridge1(b1_pos,b2_pos,b3_pos,b4_pos,cavity1,obstacle)
        elif(br2_cav ==3):
            bridge2(b1_pos,b2_pos,b3_pos,b4_pos,cavity2,obstacle)

    # elif( (b1+b3+b4) == numb ):
    #     print "b1+b3+b4"
    #     b2_pos = -1
    #     if(br1_cav ==3):
    #         bridge1(b1_pos,b2_pos,b3_pos,b4_pos,cavity1,obstacle)
    #     elif(br2_cav ==3):
    #         bridge2(b1_pos,b2_pos,b3_pos,b4_pos,cavity2,obstacle)

    # elif( (b2+b3+b4) == numb ):
    #     print "b2+b3+b4"
    #     b1_pos = -1
    #     if(br1_cav ==3):
    #         bridge1(b1_pos,b2_pos,b3_pos,b4_pos,cavity1,obstacle)
    #     elif(br2_cav ==3):
    #         bridge2(b1_pos,b2_pos,b3_pos,b4_pos,cavity2,obstacle)

    ######### 2 Boulders ############
    
    elif ( (b1+b2) == numb ):
        print "b1+b2"
        b3_pos=b4_pos = -1
        if(br1_cav ==2):
            bridge1(b1_pos,b2_pos,b3_pos,b4_pos,cavity1,obstacle)
        elif(br2_cav ==2):
            bridge2(b1_pos,b2_pos,b3_pos,b4_pos,cavity2,obstacle)

    elif( (b1+b3) == numb ):
        print "b1+b3"
        b2_pos=b4_pos = -1
        if(br1_cav ==2):
            bridge1(b1_pos,b2_pos,b3_pos,b4_pos,cavity1,obstacle)
        elif(br2_cav ==2):
            bridge2(b1_pos,b2_pos,b3_pos,b4_pos,cavity2,obstacle)

    elif( (b1+b4) == numb ):
        print "b1+b4"
        b2_pos=b3_pos = -1
        if(br1_cav ==2):
            bridge1(b1_pos,b2_pos,b3_pos,b4_pos,cavity1,obstacle)
        elif(br2_cav ==2):
            bridge2(b1_pos,b2_pos,b3_pos,b4_pos,cavity2,obstacle)

    elif( (b2+b3) == numb ):
        print "b2+b3"
        b1_pos=b4_pos = -1
        if(br1_cav ==2):
            bridge1(b1_pos,b2_pos,b3_pos,b4_pos,cavity1,obstacle)
        elif(br2_cav ==2):
            bridge2(b1_pos,b2_pos,b3_pos,b4_pos,cavity2,obstacle)

    elif( (b2+b4) == numb ):
        print "b2+b4"
        b1_pos=b3_pos = -1
        if(br1_cav ==2):
            bridge1(b1_pos,b2_pos,b3_pos,b4_pos,cavity1,obstacle)
        elif(br2_cav ==2):
            bridge2(b1_pos,b2_pos,b3_pos,b4_pos,cavity2,obstacle)

    elif( (b3+b4) == numb ):
        print "b3+b4"
        b1_pos=b2_pos = -1
        if(br1_cav ==2):
            bridge1(b1_pos,b2_pos,b3_pos,b4_pos,cavity1,obstacle)
        elif(br2_cav ==2):
            bridge2(b1_pos,b2_pos,b3_pos,b4_pos,cavity2,obstacle)
        
    

main()
cv2.waitKey(0)