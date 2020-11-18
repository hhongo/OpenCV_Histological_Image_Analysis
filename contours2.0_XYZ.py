import numpy as np
import cv2
import math
import sys

def empty(a):
    pass

#create trackbar
cv2.namedWindow('Parameters', cv2.WINDOW_NORMAL)
cv2.createTrackbar('Threshold', 'Parameters', 200, 255, empty) # 210 increase if not sensing, decrease if sensing too much
cv2.createTrackbar('B1', 'Parameters', 180, 255, empty) # 180 
cv2.createTrackbar('G1', 'Parameters', 180, 255, empty) # 180 
cv2.createTrackbar('R1', 'Parameters', 180, 255, empty) # 180 
cv2.createTrackbar('B2', 'Parameters', 200, 255, empty) # 200 
cv2.createTrackbar('G2', 'Parameters', 200, 255, empty) # 200 
cv2.createTrackbar('R2', 'Parameters', 205, 255, empty) # 205 

#coordinates for text
boundX = 250
boundY = 4700

#find and draw the contours of the lumen
#scale is in micrometers/pixel
def innerContour(img, imgContour, scale):
    contours, hierarchy = cv2.findContours(img, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)
    contours = sorted(contours, key=cv2.contourArea, reverse = True)
    index = 0
    untrimmed = True

    while untrimmed:
        area = cv2.contourArea(contours[index]) * scale * scale
        areaMin = 200000
        if area<areaMin:
            del contours[index:]
            break
        index += 1

    lastIndex = len(contours)-1
    area = cv2.contourArea(contours[lastIndex]) * scale * scale
    diameter = 2 * math.sqrt(area/math.pi)
        
    cv2.drawContours(imgContour, contours[lastIndex], -1, (245, 130, 65), 25)
    cv2.putText(imgContour, "Luminal Area: " + str(int(area)), (boundX, boundY), cv2.FONT_HERSHEY_COMPLEX, 5, (0, 0, 0), 10) 
    return diameter

#find and draw the contours of the outer wall
#scale is in micrometers/pixel
def outerContour(img, imgContour, scale):  
    contours, hierarchy = cv2.findContours(img, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)  
    contours = sorted(contours, key=cv2.contourArea, reverse = True)

    for cnt in contours:
        area = cv2.contourArea(cnt) * scale * scale
        diameter = 2 * math.sqrt(area/math.pi)
        if area>300000:
            cv2.drawContours(imgContour, cnt, -1, (245, 140, 65), 25)
            return diameter
            break

while True:
    img = cv2.imread('68.png')
    imgContour = img.copy()
    
    #set trackbar variables
    threshold = cv2.getTrackbarPos("Threshold", "Parameters")
    thresholdB1 = cv2.getTrackbarPos('B1', 'Parameters')
    thresholdG1 = cv2.getTrackbarPos('G1', 'Parameters')
    thresholdR1 = cv2.getTrackbarPos('R1', 'Parameters')
    thresholdB2 = cv2.getTrackbarPos('B2', 'Parameters')
    thresholdG2 = cv2.getTrackbarPos('G2', 'Parameters')
    thresholdR2 = cv2.getTrackbarPos('R2', 'Parameters')

    #filters for inner contour
    imgBlurI = cv2.bilateralFilter(img, 10, 100, 100)
    retval, imgColorI = cv2.threshold(imgBlurI, 150, 255, cv2.THRESH_BINARY)
    imgGrayI = cv2.cvtColor(imgBlurI, cv2.COLOR_BGR2GRAY)
    retval2, imgBWI = cv2.threshold(imgGrayI, threshold, 255, cv2.THRESH_BINARY)
    imgCannyI = cv2.Canny(imgBWI, 40, 110)
    kernelI = np.ones((2,2))
    imgDilI = cv2.dilate(imgCannyI, kernelI, iterations = 1)

    innerDiameter = innerContour(imgDilI, imgContour, 0.49)
    
    #filters for outer contour
    imgXYZ = cv2.cvtColor(img, cv2.COLOR_BGR2XYZ)
    lowerThreshold = np.array([thresholdB1, thresholdG1, thresholdR1])
    higherThreshold = np.array([thresholdB2, thresholdG2, thresholdR2])
    imgThreshO = cv2.inRange(imgXYZ, lowerThreshold, higherThreshold)
    kernelO = np.ones((50,50)) #40,40
    imgClosingO = cv2.morphologyEx(imgThreshO, cv2.MORPH_CLOSE, kernelO)
    imgBlurO = cv2.GaussianBlur(imgClosingO,(9,9),0)
    imgInvertO = cv2.bitwise_not(imgBlurO)
    imgCannyO = cv2.Canny(imgInvertO, 100, 200)
    kernelO = np.ones((5,5)) #3,3
    imgDilO = cv2.dilate(imgCannyO, kernelO)
    
    outerDiameter = outerContour(imgDilO, imgContour, 0.49)

    #calculate wall thickness
    thickness = (outerDiameter - innerDiameter)/2
    cv2.putText(imgContour, "Wall Thickness: " + str(int(thickness)), (boundX, boundY + 200), cv2.FONT_HERSHEY_COMPLEX, 5, (0, 0, 0), 10) 

    #display main output with contours
    cv2.namedWindow('Contours', cv2.WINDOW_NORMAL)
    cv2.imshow('Contours', imgContour)
    cv2.namedWindow('XYZ', cv2.WINDOW_NORMAL)
    cv2.imshow('XYZ', imgXYZ)
   
    if cv2.waitKey(1) & 0xFF == ord('q'):
        break