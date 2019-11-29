import cv2
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

centerPoints = []

# Initiailizes lsit of items in motion
#inMotion = [None, None]

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
        thresh_frame = cv2.threshold(diff_frame, 20, 255, cv2.THRESH_BINARY)[1] # Was 35 for second paramenter. 20 works well too
        thresh_frame = cv2.dilate(thresh_frame, None, iterations = 2)
    
        # Maybe implement adaptive thresholding

        # Get countouring data of image
        (cnts, _) = cv2.findContours(thresh_frame.copy(), cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE) 

        for contour in cnts: 
            if cv2.contourArea(contour) < 10000: 
                continue
            motion = 1
  
            (x, y, w, h) = cv2.boundingRect(contour) 
            # Draw green rectangle around moving object
            cv2.rectangle(ROI, (x, y), (x + w, y + h), (200, 200, 0), 3) 
            # Draw center of moving object
            centerXCoord = int(x + (1/2) * w)
            centerYCoord = int(y + (1/2) * h)
            centerPoint = (centerXCoord, centerYCoord)
            cv2.circle(ROI, centerPoint, 5, (200, 200, 0), -1, 8, 0)

            if len(centerPoints) > 10:
                centerPoints.pop(0)
            centerPoints.append(centerPoint)
            
            # Display previous 10 points 
            for point in centerPoints:
                cv2.circle(ROI, point, 5, (200, 200, 0), -1, 8, 0)
                    
            (angle, _, _, _, _) = stats.linregress(centerPoints)


            print(angle)

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