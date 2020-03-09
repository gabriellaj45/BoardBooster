import cv2
import numpy as np
import imutils


def getColor():
    '''
    # capturing video through webcam
    cap = cv2.VideoCapture(0)
    while True:
        _, image = cap.read()

    dominantColor = 'pink'
    '''
    image = cv2.imread('newImage.jpg')
    ratio = image.shape[0] / 300.0
    orig = image.copy()
    image = imutils.resize(image, height=300)

    hsv = cv2.cvtColor(image, cv2.COLOR_BGR2HSV)
    pieceList = []

    # defining the range of red color, this is one is finicky
    # alternative range lower:160,170,50 upper:179,250,220
    # other range: lower 136, 87, 11 upper 180, 255, 255
    redLowerBound = np.array([161, 155, 84], np.uint8)
    redUpperBound = np.array([179, 255, 255], np.uint8)

    # defining the Range of blue color
    blueLowerBound = np.array([94, 80, 2], np.uint8)
    blueUpperBound = np.array([126, 255, 255], np.uint8)

    # defining the Range of yellow color
    yellowLowerBound = np.array([20, 190, 20], np.uint8)
    yellowUpperBound = np.array([30, 255, 255], np.uint8)

    # defining the Range of green color
    greenLowerBound = np.array([33, 80, 40], np.uint8)
    greenUpperBound = np.array([102, 255, 255], np.uint8)

    orangeLowerBound = np.array([5, 50, 50], np.uint8)
    orangeUpperBound = np.array([15, 255, 255], np.uint8)

    # finding the range of red, blue and yellow color in the image
    red = cv2.inRange(hsv, redLowerBound, redUpperBound)
    blue = cv2.inRange(hsv, blueLowerBound, blueUpperBound)
    yellow = cv2.inRange(hsv, yellowLowerBound, yellowUpperBound)
    green = cv2.inRange(hsv, greenLowerBound, greenUpperBound)
    orange = cv2.inRange(hsv, orangeLowerBound, orangeUpperBound)

    # Morphological transformation, Dilation
    kernal = np.ones((5, 5), "uint8")

    cv2.erode(red, kernal, iterations=1)
    red = cv2.dilate(red, kernal)

    cv2.erode(blue, kernal, iterations=1)
    blue = cv2.dilate(blue, kernal)

    cv2.erode(yellow, kernal, iterations=1)
    yellow = cv2.dilate(yellow, kernal)

    cv2.erode(green, kernal, iterations=1)
    green = cv2.dilate(green, kernal)

    cv2.erode(orange, kernal, iterations=1)
    orange = cv2.dilate(orange, kernal)

    # Tracking the Red Color
    (_, contours, hierarchy) = cv2.findContours(red, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)
    numRed = len(contours)

    # Tracking the Blue Color
    (_, contours, hierarchy) = cv2.findContours(blue, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)
    numBlue = len(contours)

    # Tracking the yellow Color
    (_, contours, hierarchy) = cv2.findContours(yellow, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)
    numYellow = len(contours)

    # Tracking the green Color
    (_, contours, hierarchy) = cv2.findContours(green, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)
    numGreen = len(contours)

    # Tracking the orangle Color
    (_, contours, hierarchy) = cv2.findContours(orange, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)
    numOrange = len(contours)


