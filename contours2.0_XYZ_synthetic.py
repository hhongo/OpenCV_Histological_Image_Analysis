import numpy as np
import cv2
import math
import sys

def empty(a):
    pass

#create trackbar
cv2.namedWindow('Parameters', cv2.WINDOW_NORMAL)
cv2.createTrackbar('B1', 'Parameters', 180, 255, empty) #XYZ: 180 XYZ: 130
cv2.createTrackbar('G1', 'Parameters', 180, 255, empty) #XYZ: 180 XYZ: 130
cv2.createTrackbar('R1', 'Parameters', 180, 255, empty) #XYZ: 180 XYZ: 130
cv2.createTrackbar('B2', 'Parameters', 200, 255, empty) #XYZ: 200 XYZ: 140
cv2.createTrackbar('G2', 'Parameters', 200, 255, empty) #XYZ: 200 XYZ: 140
cv2.createTrackbar('R2', 'Parameters', 205, 255, empty) #XYZ: 205 XYZ: 155

#coordinates for text
boundX = 250
boundY = 4700

#find and draw the contours of the outer wall
#scale is in micrometers/pixel
def findContours(img, imgContour, scale):  
    contours, hierarchy = cv2.findContours(img, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)  
    
    contours = sorted(contours, key=cv2.contourArea, reverse = True)
    index = 0
    untrimmed = True

    while untrimmed:
        area = cv2.contourArea(contours[index]) * scale * scale
        areaMin = 100000
        if area<areaMin:
            del contours[index:]
            untrimmed = False
        index += 1

    del contours[1:(len(contours)-1)]

    innerDiameter = 0
    outerDiameter = 0
    boundX = 250
    boundY = 4800

    for cnt in contours:
        area = cv2.contourArea(cnt) * scale * scale
        diameter = 2 * math.sqrt(area/math.pi)
        
        cv2.drawContours(imgContour, cnt, -1, (245, 130, 65), 20)
        
        if outerDiameter == 0:
            outerDiameter = diameter
        elif outerDiameter != 0 and innerDiameter == 0:
            innerDiameter = diameter  
    
    thickness = (outerDiameter - innerDiameter)/2
    cv2.putText(imgContour, "Wall Thickness: " + str(int(thickness)), (boundX, boundY), cv2.FONT_HERSHEY_COMPLEX, 5, (0, 0, 0), 10)
    cv2.putText(imgContour, "BGR: [" + str(thresholdB1) + ", " + str(thresholdG1) + ", " + str(thresholdR1) + "] [" + str(thresholdB2) + ", " + str(thresholdG2) + ", " + str(thresholdR2) + "]", 
        (boundX, boundY + 200), cv2.FONT_HERSHEY_COMPLEX, 5, (0, 0, 0), 10) 

while True:
    img = cv2.imread('3d 20.png')
    imgContour = img.copy()
    
    #set trackbar variables
    thresholdB1 = cv2.getTrackbarPos('B1', 'Parameters')
    thresholdG1 = cv2.getTrackbarPos('G1', 'Parameters')
    thresholdR1 = cv2.getTrackbarPos('R1', 'Parameters')
    thresholdB2 = cv2.getTrackbarPos('B2', 'Parameters')
    thresholdG2 = cv2.getTrackbarPos('G2', 'Parameters')
    thresholdR2 = cv2.getTrackbarPos('R2', 'Parameters')
    
    #filters for outer contour
    imgXYZ = cv2.cvtColor(img, cv2.COLOR_BGR2XYZ)
    lowerThreshold = np.array([thresholdB1, thresholdG1, thresholdR1])
    higherThreshold = np.array([thresholdB2, thresholdG2, thresholdR2])
    imgThresh = cv2.inRange(imgXYZ, lowerThreshold, higherThreshold)
    kernel = np.ones((50,50)) #40,40
    imgClosing = cv2.morphologyEx(imgThresh, cv2.MORPH_CLOSE, kernel)
    imgBlur = cv2.GaussianBlur(imgClosing,(9,9),0)
    imgInvert = cv2.bitwise_not(imgBlur)
    imgCanny = cv2.Canny(imgInvert, 100, 200)
    kernel2 = np.ones((5,5)) #3,3
    imgDil = cv2.dilate(imgCanny, kernel2)
    
    findContours(imgDil, imgContour, 0.49)

    #display main output with contours
    cv2.namedWindow('Contours', cv2.WINDOW_NORMAL)
    cv2.imshow('Contours', imgContour)
    cv2.namedWindow('Color', cv2.WINDOW_NORMAL)
    cv2.imshow('Color', imgDil)
   
    if cv2.waitKey(1) & 0xFF == ord('q'):
        break