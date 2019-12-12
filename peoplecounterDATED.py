import cv2
import numpy as np
import time
import pandas
from datetime import datetime

# Initializes background 
static_back = None

# Initiailizes lsit of items in motion
inMotion = [None, None]

# Time of movement
time = []

# Initializing time frame/ dataframe
df = pandas.DataFrame(columns = ["Start", "End"]) 

capture = cv2.VideoCapture(0)

while(True):
    # Capture frame-by-frame
    ret, frame = capture.read()

    #Set motion to 0
    motion = 0

    # Convert video to grayscale 
    gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)

    # Apply gaussian blur to see motion easier
    gray = cv2.GaussianBlur(gray, (21, 21), 0) 

    # Set static frame
    if static_back is None: 
        static_back = gray 
        continue

    # Difference betwee static frame above and Gaussian blur frame
    # Will be displayed as the difference frame 
    diff_frame = cv2.absdiff(static_back, gray) 

    # Show white if the difference above is greater than 30
    # WIll be displayed as the threshold frame
    thresh_frame = cv2.threshold(diff_frame, 35, 255, cv2.THRESH_BINARY)[1] 
    thresh_frame = cv2.dilate(thresh_frame, None, iterations = 2)

    # Possible adaptive thresholding
    #thresh_frame = cv2.adaptiveThreshold(diff_frame, 255, cv2.ADAPTIVE_THRESH_MEAN_C, cv2.THRESH_BINARY, 11, 1) # may need [1]
    #thresh_frame = cv2.dilate(thresh_frame, None, iterations = 2)

     # Finding contour of moving object 
    (cnts, _) = cv2.findContours(thresh_frame.copy(), cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE) 
  
    for contour in cnts: 
        if cv2.contourArea(contour) < 10000: 
            continue
        motion = 1
  
        (x, y, w, h) = cv2.boundingRect(contour) 
        # Draw green rectangle around moving object
        cv2.rectangle(frame, (x, y), (x + w, y + h), (0, 255, 0), 3) 
  
    # Appending status of motion 
    inMotion.append(motion) 
  
    inMotion = inMotion[-2:] 
  
    # Appending Start time of motion 
    if inMotion[-1] == 1 and inMotion[-2] == 0: 
        time.append(datetime.now()) 
  
    # Appending End time of motion 
    if inMotion[-1] == 0 and inMotion[-2] == 1: 
        time.append(datetime.now()) 
  
    # Displaying image in gray_scale 
    cv2.imshow("Gray Frame", gray) 
  
    # Displaying the difference in currentframe to 
    # the staticframe(very first_frame) 
    cv2.imshow("Difference Frame", diff_frame) 
  
    # Displaying the black and white image in which if 
    # intencity difference greater than 30 it will appear white 
    cv2.imshow("Threshold Frame", thresh_frame) 
  
    # Displaying color frame with contour of motion of object 
    cv2.imshow("Color Frame", frame) 

    key = cv2.waitKey(1) 
    # if q entered whole process will stop 
    if key == ord('q'): 
        # if something is movingthen it append the end time of movement 
        if motion == 1: 
            time.append(datetime.now()) 
        break
  
# Appending time of motion in DataFrame 
for i in range(0, len(time), 2): 
    df = df.append({"Start":time[i], "End":time[i + 1]}, ignore_index = True) 
  
# Creating a csv file in which time of movements will be saved 
df.to_csv("Time_of_movements.csv") 
  
video.release() 
  
# Destroying all the windows 
cv2.destroyAllWindows() 

#img = cv2.imread('logo.png')

#px = img[190,10]
#print(px)


# accessing only blue pixel
#blue = img[0,0,0]
#print(blue)