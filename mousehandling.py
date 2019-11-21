import cv2
import numpy as np

drawing = False
point1 = ()
point2 = ()

def mouse_drawing(event, x, y, flags, params):  # Draw rectangle on video feed
    global point1, point2, drawing
    if event == cv2.EVENT_LBUTTONDOWN:
        if drawing is False:
            drawing = True
            point1 = (x, y)
        else:
            drawing = False
    elif event == cv2.EVENT_MOUSEMOVE:
        if drawing is True:
            point2 = (x, y)

cap = cv2.VideoCapture(0)   # Initialize video capture

cv2.namedWindow("Frame")
cv2.setMouseCallback("Frame", mouse_drawing)    # Add event callback to video feed window


while True:
    _, frame = cap.read()   # Capture frames from camera

    if point1 and point2:
        #cv2.rectangle(frame, point1, point2, (255, 0, 0))

        # Draw Area of Interest 
        r = cv2.rectangle(frame, point1, point2, (255, 0, 0), 15)
        rect_img = frame[point1[1] : point2[1], point1[0] : point2[0]]  # Creates area of interest

    

    cv2.imshow("Frame", frame)
    if cv2.waitKey(1) == 13:
        break

cap.release()
cv2.destroyAllWindows()