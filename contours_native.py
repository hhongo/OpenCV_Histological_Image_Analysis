# import necessary libraries
import numpy as np
import cv2
import math


# create trackbar and specify ranges
def empty(a):
    pass

cv2.namedWindow('Parameters', cv2.WINDOW_NORMAL)
cv2.createTrackbar('Threshold', 'Parameters', 170, 255, empty)  # 150 for native artery
cv2.createTrackbar('Area', 'Parameters', 100000, 300000, empty)


# find and draw the contours of the lumen and outer surface
# scale is in micrometers/pixel
def getContours(img, imgContour, scale):

    contours, hierarchy = cv2.findContours(img, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)  
    contours = sorted(contours, key=cv2.contourArea, reverse=True)
    index = 0
    untrimmed = True

    while untrimmed: # delete all contours with area less than areaMin from contour list
        area = cv2.contourArea(contours[index]) * scale * scale
        areaMin = cv2.getTrackbarPos("Area", "Parameters")
        if area < areaMin:
            del contours[index:]
            break
        index += 1
    del contours[1:(len(contours)-1)] # delete all contours except the outermost and innermost contours

    # declare diameter variables
    innerDiameter = 0
    outerDiameter = 0
    
    # coordinates for text
    boundX = 150 
    boundY = 4800 

    # draw the outermost and innermost contours
    for cnt in contours:
        area = cv2.contourArea(cnt) * scale * scale
        diameter = 2 * math.sqrt(area/math.pi)
        
        cv2.drawContours(imgContour, cnt, -1, (245, 130, 65), 20)
        
        if outerDiameter == 0:
            outerDiameter = diameter
        elif outerDiameter != 0 and innerDiameter == 0:
            innerDiameter = diameter  
            cv2.putText(imgContour, "Luminal Area: " + str(int(area)), (boundX, boundY), cv2.FONT_HERSHEY_COMPLEX, 5, (0, 0, 0), 10) 
    
    #calculate wall thickness
    thickness = (outerDiameter - innerDiameter)/2
    cv2.putText(imgContour, "Wall Thickness: " + str(round(thickness, 2)), (boundX, boundY + 200), cv2.FONT_HERSHEY_COMPLEX, 5, (0, 0, 0), 10) 

# run through all filters and output image with contours drawn and luminal area and wall thickness values written in text
while True:
    img = cv2.imread('42.png') # add image to folder and input name
    imgContour = img.copy()
    
    imgBlur = cv2.bilateralFilter(img, 10, 100, 100)
    imgGray = cv2.cvtColor(imgBlur, cv2.COLOR_BGR2GRAY)
    threshold = cv2.getTrackbarPos("Threshold", "Parameters")
    retval, imgBW = cv2.threshold(imgGray, threshold, 255, cv2.THRESH_BINARY)
    imgCanny = cv2.Canny(imgBW, 40, 110)
    kernel = np.ones((2, 2))
    imgDil = cv2.dilate(imgCanny, kernel, iterations=1)

    getContours(imgDil, imgContour, 0.49) # call getContours method
   
    cv2.namedWindow('Contours', cv2.WINDOW_NORMAL)
    cv2.imshow('Contours', imgContour)
   
    if cv2.waitKey(1) & 0xFF == ord('q'):
        break
