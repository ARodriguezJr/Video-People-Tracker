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

# Counters of how many people that left or entered a room
entered = 0
left = 0

# Next int for unique object in frame
nextID = 0

# List of objects in motion
movingPersons = []

# Threshold for determining nearby points
NEARTHRESH = 20

# Boolean variable for if a nearby centroid was found
matchFound = False


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

def isNear(newCentroid, oldCentroid):
    MaxX = oldCentroid[0] + NEARTHRESH
    MinX = oldCentroid[0] - NEARTHRESH

    MaxY = oldCentroid[1] + NEARTHRESH
    MinY = oldCentroid[1] - NEARTHRESH

    if newCentroid[0] > MinX and newCentroid[0] < MaxX:
        if newCentroid[1] > MinY and newCentroid[1] < MaxY:
            # If centerpoint is within threshold for being near
            return True
    else:
        return False

class Person:
    centerPoints = []
    id = 0
    center = None
    direction = None
    inFrame = None
    def __init__(self, nextID, centroid):
        self.id = nextID
        self.center = centroid
        self.centerPoints.append(centroid)
        self.inFrame = True
    
    def pushCentroid(self, centroid):
        self.center = centroid
        self.centerPoints.append(centroid)
    
    def clear(self):
        self.centerPoints = []
        self.id = 0
        self.center = None

    def checkCenterpointLength(self):
        if len(self.centerPoints) > 10:
            self.centerPoints.pop(0)

    def getDirection(self): 
        dX = self.center[0] - self.centerPoints[0][0]
        dY = self.center[1] - self.centerPoints[0][1]
        
        if dX > 15 or dX < -15:
            if dX >= 0:
                horizontal = "Right"
                #print("Right", end='')
            else:
                horizontal = "Left"
                #print("Left", end='')
        else:
            horizontal = "Calculating"
        if dY > 15 or dY < -15:
            if dY >= 0:
                vertical = "Down"
                #print("Down")
            else:
                vertical = "Up"
                #print("Up")
        else:
            vertical = "Calculating"
        
        if (dX > 15 or dX < -15) or (dY > 15 or dY < -15):
            cv2.putText(ROI, vertical + "-" + horizontal, (x, y + 20), cv2.FONT_HERSHEY_SIMPLEX, 1, (255, 0, 255), 4)

        # Display previous 10 points 
        for point in self.centerPoints:
            cv2.circle(ROI, point, 5, (200, 200, 0), -1, 8, 0)
        #print(movingPerson[nextID].id)
        cv2.putText(ROI, str(self.id), (x, y - 40), cv2.FONT_HERSHEY_SIMPLEX, 1, (255, 0, 255), 4)




cap = cv2.VideoCapture(0)   # Initialize video capture: 0 for front camera, 1 for rear camera

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

        # Get countouring data of image
        (cnts, _) = cv2.findContours(thresh_frame.copy(), cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE) 

        for contour in cnts: 
            if cv2.contourArea(contour) < 10000: # Was at 10000
                continue        # Skips over contour if not at threshold
            motion = 1

            # Finds contour bounding rectangle and centroid of object
            (x, y, w, h) = cv2.boundingRect(contour)        
            # Draw green rectangle around moving object
            cv2.rectangle(ROI, (x, y), (x + w, y + h), (200, 200, 0), 3) 
            # Draw center of moving object
            centerXCoord = int(x + (1/2) * w)
            centerYCoord = int(y + (1/2) * h)
            newCentroid = (centerXCoord, centerYCoord)
            cv2.circle(ROI, newCentroid, 5, (200, 200, 0), -1, 8, 0)

            # If first Person found, create first person in movingPerson
            if len(movingPersons) == 0:
                movingPersons.append(Person(nextID, newCentroid))
                nextID = nextID + 1
                print('1st')
            else:
                # Check if centroid is nearby a current centerpoint
                for movingPerson in movingPersons:
                    if isNear(newCentroid, movingPerson.center):
                        movingPerson.pushCentroid(newCentroid)
                        matchFound = True
                        movingPerson.inFrame = True
                        print("Centroid added")
                        break
                if matchFound == False:
                    movingPersons.append(Person(nextID, newCentroid))
                    nextID = nextID + 1
                    movingPerson.inFrame = True
                    #time.sleep(.100)
                    print("New Person Made")
                    break
                matchFound = False

            # Check length of each Person's centerpoint list and calculate direction
            for movingPerson in movingPersons:
                movingPerson.checkCenterpointLength()
                movingPerson.getDirection()

            # Bounces between 1 and 2
            print("End: ", "")
            print(len(movingPersons))  

        for index, movingPerson in enumerate(movingPersons):
            # Checks if the person was in frame - if not, pop it from list
            if movingPerson.inFrame == False:
                print(index)
                movingPersons.pop(index)
            # Resets inFrame to false
            movingPerson.inFrame = False           

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

    if cv2.waitKey(1) == 13:
        break

cap.release()
cv2.destroyAllWindows()