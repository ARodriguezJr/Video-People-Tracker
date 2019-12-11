import cv2
import math
import numpy as np
import scipy as sp
from scipy import stats
import time
import queue

# Tracks if the mouse is currently drawing a rectangle
drawing = False 

# Top reft point of rectangle
point1 = () 

# Bottom right point of rectangle
point2 = () 

# Initializes background 
static_back = None

# Variables to hold directional values of moving objects
vertical = "Up"
horizontal = "Right"

# Counters of how many people that left or entered a room
entered = 0
left = 0

# List to hold previous points of objects
#centerPoints = []

# Next int for unique object in frame
nextID = 0

# List of objects in motion
movingPersons = []

# Initiailizes lsit of items in motion
#inMotion = [None, None]

# Boolean value for if the tempPerson object was cleared and needs to be made again
needNewTemp = True

def mouse_drawing(event, x, y, flags, params):  # Collect coordinate data from mouse event to draw rectangle
    global point1, point2, drawing
    if event == cv2.EVENT_LBUTTONDOWN:
        if drawing is False:
            drawing = True
            point1 = (x, y)
        else:
            time.sleep(3)   # Gives 3 seconds for user to move before detection starts
            drawing = False
    elif event == cv2.EVENT_MOUSEMOVE:
        if drawing is True:
            point2 = (x, y)

class Person:
    centerPoints = []
    id = 0
    def __init__(self, nextID):
        self.id = nextID
    #def __init__(self, nextID, centroid):
        #self.id = nextID
        #self.centerPoints.append(centroid)
    
    def pushCentroid(self, centroid):
        self.centerPoints.append(centroid)
    
    def clear(self):
        self.centerPoints = []
        self.id = 0

cap = cv2.VideoCapture(0)   # Initialize video capture

#cv2.namedWindow("Frame")
#cv2.setMouseCallback("Frame", mouse_drawing)    # Add event callback to video feed window

cv2.namedWindow("Color Frame")
cv2.setMouseCallback("Color Frame", mouse_drawing)    # Add event callback to video feed window

while True:
    _, frame = cap.read()   # Capture frames from camera

    # Draw ROI then wait seconds
    if point1 and point2:
        ROIRect = cv2.rectangle(frame, point1, point2, (255, 0, 0), 5)
        ROI = frame[point1[1] : point2[1], point1[0] : point2[0]]  # Creates region of interest


    if point1 and point2 and not drawing:
        #cv2.rectangle(frame, point1, point2, (255, 0, 0))

        # Draw Region of Interest 
        ROIRect = cv2.rectangle(frame, point1, point2, (255, 0, 0), 5)
        ROI = frame[point1[1] : point2[1], point1[0] : point2[0]]  # Creates region of interest

        ########################################################
                           #MOTION PROCESSING#
        ########################################################

        #Set motion to 0
        motion = 0

        # Convert video to grayscale 
        gray = cv2.cvtColor(ROI, cv2.COLOR_BGR2GRAY)

        # Apply gaussian blur to see motion easier
        gray = cv2.GaussianBlur(gray, (21, 21), 0) 

        # Redraw ROI problem might be here
        # Set static frame
        if static_back is None: 
            static_back = gray 
            continue

        # Difference betwee static frame above and Gaussian blur frame
        # Will be displayed as the difference frame 
        diff_frame = cv2.absdiff(static_back, gray) 

        # Show white if the difference above is greater than 30
        # WIll be displayed as the threshold frame
        thresh_frame = cv2.threshold(diff_frame, 10, 255, cv2.THRESH_BINARY)[1] # Was 35 for second paramenter. 20 works well too
        thresh_frame = cv2.dilate(thresh_frame, None, iterations = 2)
    
        # Maybe implement adaptive thresholding

        # Get countouring data of image
        (cnts, _) = cv2.findContours(thresh_frame.copy(), cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE) 

        for contour in cnts: 
            if cv2.contourArea(contour) < 10000: # Was at 10000
                continue        # Skips over contour if not at threshold
            motion = 1

            # If centroid doesnt match a previous centroid in list of movingPersons, iterate nextID and make new person
            #check if moving person array was made or of the next idex in list was made
            #print("Before length: ", "")
            #print(len(movingPerson))
            #if len(movingPerson) <= nextID:
             #   movingPerson.append(Person(nextID))
              #  print('1st')
            #elif len(movingPerson[nextID].centerPoints) == 0:
             #   movingPerson.append(Person(nextID))
              #  print("2nd")
            ##print("After: ", "")
            #print(len(movingPerson))

            # Finds contour bounding rectangle and centroid of object
            (x, y, w, h) = cv2.boundingRect(contour)        # Coordinates of found contour
            # Draw green rectangle around moving object
            cv2.rectangle(ROI, (x, y), (x + w, y + h), (200, 200, 0), 3) 
            # Draw center of moving object
            centerXCoord = int(x + (1/2) * w)
            centerYCoord = int(y + (1/2) * h)
            centerPoint = (centerXCoord, centerYCoord)
            cv2.circle(ROI, centerPoint, 5, (200, 200, 0), -1, 8, 0)

            # tempPerson known as movingPersons[nextID] or [NextID - 1]
            # mkae new temp person if already values in centroid list
            if needNewTemp == True:
                tempPerson = Person(nextID)
                needNewTemp = False

            tempPerson.pushCentroid(centerPoint)

            # If first Person found, append person to MovingPerson list
            if len(movingPersons) == 0:
                movingPersons.append(tempPerson)
                nextID = nextID + 1
                tempPerson.clear()
                needNewTemp = True
                print('1st')

            # Try to assign IDs after two center points have been found
            # May need to be > 2 or another number
            # may have to do a for loop for each moving person in movingPersons
            if len(tempPerson.centerPoints) == 2:
                centroidMatch = False
                print("Checking")
                for newCentroid in tempPerson.centerPoints:
                    for movingPerson in movingPersons:
                        for currentCentroid in movingPerson.centerPoints:
                            if newCentroid == currentCentroid:
                                # Centroid Match found, no new ID will be made
                                centroidMatch = True
                                # maybe clear out centroid list or MATCH TO current ID'd person
                
                # Create new person if no match was found
                if centroidMatch == False:
                    print("CREATING NEW ID!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!")
                    movingPersons.append(tempPerson)
                    tempPerson.clear()
                    nextID = nextID + 1


            

            # If centroid doesnt match a previous centroid in list of movingPersons, iterate nextID and make new person

            if len(tempPerson.centerPoints) > 10:
                tempPerson.centerPoints.pop(0)
            tempPerson.centerPoints.append(centerPoint)

            # Calcualtes change of coordinates between first and last coords in list
            dX = centerPoint[0] - tempPerson.centerPoints[0][0]
            dY = centerPoint[1] - tempPerson.centerPoints[0][1]
            
            
            if dX > 15 or dX < -15:
                if dX >= 0:
                    horizontal = "Right"
                    #print("Right", end='')
                else:
                    horizontal = "Left"
                    #print("Left", end='')
            if dY > 15 or dY < -15:
                if dY >= 0:
                    vertical = "Down"
                    #print("Down")
                else:
                    vertical = "Up"
                    #print("Up")
            if (dX > 15 or dX < -15) or (dY > 15 or dY < -15):
                cv2.putText(ROI, vertical + "-" + horizontal, (x, y + 20), cv2.FONT_HERSHEY_SIMPLEX, 1, (255, 0, 255), 4)

            # Display previous 10 points 
            for point in tempPerson.centerPoints:
                cv2.circle(ROI, point, 5, (200, 200, 0), -1, 8, 0)
            #print(movingPerson[nextID].id)
            cv2.putText(ROI, "tempPerson.id", (x, y - 40), cv2.FONT_HERSHEY_SIMPLEX, 1, (255, 0, 255), 4)

            # Incrememnt to next ID if object is different
            #if len(movingPersons[nextID].centerPoints) == 1:
            #    nextID = nextID + 1

            # Bounces between 1 and 2
            print("End: ", "")
            print(len(movingPersons))                 
            #(angle, _, _, _, _) = stats.linregress(centerPoints)
            #print(angle)

            #lineLength = 300
            #print(centerPoint[0])
            #print(centerPoint[1])
            #print(math.cos(angle * np.pi / 180.0))

            # Need to error check in case angle is undefined or NaN
            #if not math.isnan(angle):
                # maybe check if angle is negative or positive
                # Seems to be inverted based on camera view
                #if angle >= 0:
                    #lineEndX = int(centerPoint[0] + lineLength * math.cos(angle * np.pi / 180.0))
                    #lineEndY = int(centerPoint[1] - lineLength * math.sin(angle * np.pi / 180.0))
                #else:
                    #lineEndX = int(centerPoint[0] - lineLength * math.cos(angle * np.pi / 180.0))
                    #lineEndY = int(centerPoint[1] - lineLength * math.sin(angle * np.pi / 180.0))
                # Draws directional line
                #cv2.line(ROI, centerPoint, (lineEndX, lineEndY), (0, 150, 215), 5)

        # Might need to change this ROI to frame

        # Displaying image in gray_scale 
        cv2.imshow("Gray Frame", gray) 

        # Displaying the difference in currentframe to 
        # the staticframe(very first_frame) 
        cv2.imshow("Difference Frame", diff_frame) 

        # Displaying the black and white image in which if 
        # intencity difference greater than 30 it will appear white 
        cv2.imshow("Threshold Frame", thresh_frame) 

        cv2.imshow("Region of Interest", ROI)

    # Displaying color frame with contour of motion of object 
    cv2.imshow("Color Frame", frame) 

    #might need to show ROI in imshow
    #cv2.imshow("Frame", ROI)
    if cv2.waitKey(1) == 13:
        break

cap.release()
cv2.destroyAllWindows()