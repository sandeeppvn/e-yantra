import cv2
import numpy as np
import time
import serial
from math import sqrt
import general_functions as gf  
import color as col

# Connect to Xbee
ser = serial.Serial(port = 'COM3', baudrate = 9600, bytesize = serial.EIGHTBITS, parity = serial.PARITY_NONE, stopbits = serial.STOPBITS_ONE, timeout = 1)
##############SPECIAL BOT FUNCTIONS########################################


'''
*Function Name: move_among_obstacles
*Input: obstacle,end_point,
*Output: none
*Logic: Function to find position of closest obstacle and decide the course of action
*Example Call: move_among_obstacles(obstacles,bridge2_start,-1)
'''

#Function to find position of closest obstacle
def move_among_obstacles(obstacle,end_point,direction):
    #Go towards base station
    my_obstacles = []
    slope,center,front = track_bot()

    if(direction==1):
        for i in obstacle:
            if( i[1]>end_point[1]  and  i[1]<front[1] ):
                my_obstacles.append(i)
            my_obstacles.sort(key=lambda x: x[1],reverse=True)

    elif(direction==-1):
        for i in obstacle:
            if( i[1]>front[1]  and  i[1]<end_point[1] ):
                my_obstacles.append(i)
            my_obstacles.sort(key=lambda x: x[1])
       
    check = 0
    #start moving now

    for i in my_obstacles:
        pos = complement(i[0],i[1])
        l1 = sqrt((front[0]-end_point[0])**2,(front[1]-end_point[1])**2)
        l2 = sqrt((center[0]-pos[0])**2,(center[1]-pos[1])**2)
        if (l1<l2):   
            tim = l1
        else:
            tim = l2
        print "Move time",tim
        packet = '8'
        ser.write(packet)
        time.sleep(tim)
        packet = '5'
        ser.write(packet)

        _,center,front = track_bot()
        #if bot can reach the cavity, drop it and move
        if(sqrt((front[0]-end_point[0])**2,(front[1]-end_point[1])**2)<=threshold): #reached cavity, use radial distance if doesnt work
            orient(end_point[0],end_point[1])
            return

        elif(sqrt((center[0]-pos[0])**2,(center[1]-pos[1])**2)>threshold):

            tim =  sqrt( (center[0]-x)**2 + (center[1]-y)**2)*0.0143
            print "Move time",tim
            packet = '8'
            ser.write(packet)
            time.sleep(tim)
            packet = '5'
            ser.write(packet)
            #if front has reached complement position, then move the center to that position
            # while( ) < threshold ) : #rather get the radial distance
            #     #send 8 to the bot
            #     packet = '8'
            #     ser.write(packet)
            #     _,center,front = track_bot()

    #if cavity is further, move closer            
    move_bot(end_point[0],end_point[1])




'''
*Function Name: complement
*Input: x,y
*Output: Complemented position from obstacle 
*Logic: Function to return the complementary opposite position wrt to the obstacle on bridge 2
*Example Call: complement(x,y)

''' 
#Function to return the complementary opposite position wrt to the obstacle on bridge 2
def complement(x,y):
    x = int(x)
    y = int(y)
    if( x > (int(bridge2_left) - int(bridge2_right))/2 ):
        x = x - (int(bridge2_left) - int(bridge2_right))/2
    else:
        x = x + (int(bridge2_left) - int(bridge2_right))/2

    return [x,y]




'''
*Function Name: orient
*Input: x,y
*Output: It writes the required packet values for movement of bot
*Logic: Function to orient in the right direction, by minimizing difference between slopes
*Example Call: orient(cavity[0],cavity[1])
'''
#Function to orient in the right direction, by minimizing defferent between slopes
def orient(x,y):

    print "             Enter orient"
    #try to minimize the slope
    slope1,center,front = track_bot()

    # slope2 = degrees(atan(float(center[0]-x)/(center[1]-y)))
    slope2 = degrees(atan2(float(center[0]-x),(center[1]-y)))
    tim = abs(slope1-slope2)*0.0075
    print "orient time",tim
    packet = '6'
    ser.write(packet)
    time.sleep(tim)

    
    
    packet = '5'
    ser.write(packet)
    time.sleep(2)
    print "             Exit orient"





'''
*Function Name: bot_position
*Output: Returns 0,1,2,3 depending on the position of the bot on the arena
*Logic: Threshold for various parts on the arena are fixed to determine the current bot location .
        It detects if bot is on bridge 1, bridge 2, crator region or base station
*Example Call: bot_position()
'''
def bot_position():
    slope,center,front = track_bot()

    #Threshold for crator region
    if( front[1]>bridge1_start[1] and front[1]>bridge2_start[1]  ):
        return 0

    #Threshold for bridge 1
    if( front[0]>bridge1_start[0] and front[0]<bridge1_end[0]  and  front[1]>bridge1_start[1] and front[1]<bridge1_end[1] ):
        return 1

    #Threshold for bridge 2
    if( front[0]>bridge2_start[0] and front[0]<bridge2_end[0]  and  front[1]>bridge2_start[1] and front[1]<bridge2_end[1] ):
        return 2

    #Threshold for base station
    if(  front[1]<bridge1_end[1] and front[1]<bridge2_end[1] ):
        return 3





'''
*Function Name: track_bot
*Input: none
*Output: Returns value of slope,center
*Logic: Function to get position and orientation of bot
       We generate hsv from rgb, generate mask for the bot, generate the isolated image with only cavities and obstacles for testing.
       We get the contour of bot and current position of red circles.  We then calculate the Slope mathematically.
*Example Call: track_bot()
'''
def track_bot():
    # print "                         Enter track bot"
    im = get_crop()

    #generate hsv from rgb
    hsv = cv2.cvtColor(im, cv2.COLOR_BGR2HSV)

    #generate mask for the bot, red
    mask_bo1,mask_bo2 = mask_bot(light,hsv)

    #generate the isolated image with only cavities and obstacles for testing
    res1 = cv2.bitwise_and(im,im, mask= mask_bo1)
    res2 = cv2.bitwise_and(im,im, mask= mask_bo2)
    res = cv2.bitwise_or(res1,res2)
    #obtain contour of bot, red
    contours_bot1 = get_contour(mask_bo1)
    contours_bot2 = get_contour(mask_bo2)

    #Get current position of circles of bot
    yum = get_bot( contours_bot1,contours_bot2, res )
    if(len(yum)!=2): #output of get_bot : [center_circle,small_circle]
        return track_bot()
    else:
        center = yum[0]
        front = yum[1]

        #calculate slope
        if(center[1]-front[1] !=0):
            slope = float(center[0]-front[0])/(center[1]-front[1])
        else:
            slope=400
        # print "                         Exit track bot"
        return slope,center,front    # print "                         Enter track bot"
    im = gf.get_crop()

    #generate hsv from rgb
    hsv = cv2.cvtColor(im, cv2.COLOR_BGR2HSV)

    #generate mask for the bot, red
    mask_bo = col.mask_bot(light,hsv)

    #generate the isolated image with only cavities and obstacles for testing
    res = cv2.bitwise_and(im,im, mask= mask_bo)

    #obtain contour of bot, red
    contours_bot = gf.get_contour(mask_bo)

    #Get current position of circles of bot
    yum = col.get_bot( contours_bot, res )
    if(len(yum) != 2): #output of get_bot : [center_circle,small_circle]
        return track_bot()
    else:
        center,front  = yum
        print "                 Current Bot positon"
        print "                 ",center,":center"
        print "                 ",front,":front"
        #calculate slope
        if(center[1]-front[1] !=0):
            slope = float(center[0]-front[0])/(center[1]-front[1])
        else:
            slope=400
        # print "                         Exit track bot"
        return slope,center,front





'''
*Function Name: pick_up
*Input: none
*Output: Serially writes the packet value for picking up the boulder
*Logic: Function to make the bot pick up the boulder by writing Packet value.
*Example Call: pick_up()
'''
def pick_up():
   #pick up
    packet = '1'
    ser.write(packet)





'''
*Function Name: drop_down
*Input: none
*Output: Serially writes the packet value for dropping up the boulder
*Logic: Function to make the bot drop up the boulder by writing Packet value.
*Example Call: drop_down()
''' 
def drop_down():
    #drop the arm
    packet = '0'
    ser.write(packet)




  
'''
*Function Name: move_bot
*Input: x,y
*Output: Serially writes appropriate packet values
*Logic: Function to move to (x,y) units while avoiding obstacles by writing the packet values
*Example Call: move_bot(center_point[0],center_point[1])
'''
def move_bot(x,y):
    
    time.sleep(1)
    print "         Entered move bot"
    #orient towards object
    orient(x,y)



    _,center,front = track_bot()  #track_bot returns [slope,center]

    if(bot_position()==0 or bot_position()==3):
        print "On a bridge"
        #Check where the center of the bot is, and move accordingly on crator or base region
        tim = sqrt( (center[0]-x)**2 + (center[1]-y)**2 )*0.0143
        print "Move time:",tim
        packet = '8'
        ser.write(packet)
        time.sleep(tim)
        # while( sqrt( (center[0]-x)**2 + (center[1]-y)**2 ) < threshold ) : #rather get the radial distance
        #     #send 8 to the bot
        #     packet = '8'
        #     ser.write(packet)
        #     _,center,front = track_bot()
    else:
        print "On a crator"
        #Check where the front of the bot is, and move accordingly on bridges
        tim = sqrt( (front[0]-x)**2 + (front[1]-y)**2 )*0.0143
        print "Move time",tim
        packet = '8'
        ser.write(packet)
        time.sleep(tim)
        # while( sqrt( (front[0]-x)**2 + (front[1]-y)**2 ) < threshold ) : #rather get the radial distance
        #     #send 8 to the bot
        #     packet = '8'
        #     ser.write(packet)
        #     _,center,front = track_bot()

    packet = '5'
    ser.write(packet)
    print "         Exited move bot"

    #orient towars the position if redundancy
    orient(x,y)






###############################################################################

######################## Navigation Functions #############################  
'''
*Function Name: bridge1
*Input: b1,b2,b3,b4,cavity,obstacle
*Output: none
*Logic: Obtain the cropped area and sort the cavities in reverse. 
        Now orient the bot at start of bridge 1 and call the required functions to navigate the path,pick up and drop the boulders. 
*Example Call: bridge1(b1_pos,b2_pos,b3_pos,b4_pos,cavity1,obstacle)
'''
def bridge1(b1,b2,b3,b4,cavity,obstacle):
    # print bould
    # print cavity
    print "bridge 1"
    print "check-sum"
    print "+++++++++++++++++++++++++++++++++++++++++++++++++++++++++++"

    bould = []
    temp = [b1,b2,b3,b4]
    for b in temp:
        if(b!=-1):
            bould.append(b)
    

    frame = gf.get_crop()
    cavity.sort(reverse=True)
    i=0
   

    print "check-start movement"

    ##### FOR EVERY BOULDER Bi and cavity Ci ########
    for Bi in bould:
        #If bot is on bridge 1
        if(bot_position()==1):
            #orient to the start of the bridge 1
            #Move to the start of the bridge 1, (straight)
            move_bot(bridge1_start[0],bridge1_start[1])

        #move to center
        move_bot(center_point[0],center_point[1])
        #orient and move towards Boulder Bi
        move_bot(Bi[0],Bi[1])

        #pick up boulder Bi
        pick_up()

        #move to center
        move_bot(center_point[0],center_point[1])
        #orient and move towards start of the bridge 1
        move_bot(bridge1_start[0],bridge1_start[1])

        #get the nearest cavity position
        pres_cavity = cavity[i]
        i+=1    #increment cavity position

        #Orient and move towards cavity
        move_bot(pres_cavity[0],pres_cavity[1])

        #drop the boulder Bi
        drop_down()

    ##################################################

    #Orient and move towards end of bridge 1
    move_bot(bridge1_end[0],bridge1_end[1])


    #Orient and move towards endpoint
    move_bot(endpoint[0],endpoint[1])

    
    #Buzzer for 5 sec 
    buzzer()

    #close the Xbee
    ser.close()

    cap.release()




    
''' 
*Function Name: bridge2
*Input: b1,b2,b3,b4,cavity,obstacle
*Output: none
*Logic: Obtain the cropped area and sort the cavities in reverse. 
        Now move among obstacles, till the last obstacle while navigating the path, picking up and dropping the boulders. 
*Example Call: bridge2(b1_pos,b2_pos,b3_pos,b4_pos,cavity2,obstacle)
'''
def bridge2(b1,b2,b3,b4,cavity,obstacle):
    # print bould
    # print cavity
    print "bridge 2"
    print "check-sum"
    print "+++++++++++++++++++++++++++++++++++++++++++++++++++++++++++"

    bould = []
    temp = [b1,b2,b3,b4]
    for b in temp:
        if(b!=-1):
            bould.append(b)

    print "---------------------GOT BOULDERS------------------"
    frame = get_crop()
    cavity.sort(reverse=True)
    i=0
   
    print "check-start movement for every boulder"

    ##### FOR EVERY BOULDER Bi and cavity Ci ########
    for i,Bi in enumerate(bould):
        print
        print
        print "Boulder Position:(",Bi[0],",",Bi[1],")---",i,"th boulder"
        print
        print
        #If bot is on bridge 2
        if(bot_position()==2):
            #move among obstacles, till the last obstacle and then to bridge2 start
            move_among_obstacles(obstacles,bridge2_start,-1)

        print "     About to move to center ",center_point
        #move to center
        move_bot(center_point[0],center_point[1])

        print
        print "     About to move to ",i,"th boulder (",Bi[0],",",Bi[1],")"
        #orient and move towards Boulder Bi
        move_bot(Bi[0],Bi[1])

        print "     About to pick up the boulder"
        #pick up boulder Bi
        pick_up()


        #move to center
        move_bot(center_point[0],center_point[1])
        #orient and move towards start of the bridge 1
        move_bot(bridge1_start[0],bridge1_start[1])

        #get the nearest cavity position
        pres_cavity = cavity[i]
        i+=1    #increment cavity position

        #move among obstacles, till the last obstacle and then to cavity
        move_among_obstacles(obstacles,pres_cavity,1)


        #drop the boulder Bi
        drop_down()

    ##################################################

    #move among obstacles, till the last obstacle and then to end of bridge1
    move_among_obstacles(obstacles,pres_cavity,1)


    #Orient and move towards endpoint
    move_bot(endpoint[0],endpoint[1])

    
    #Buzzer for 5 sec 
    buzzer()

    #close the Xbee
    ser.close()

    cap.release()