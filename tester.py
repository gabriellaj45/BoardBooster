import numpy as np
import cv2
import imutils


image = cv2.imread('cardsAgainstHumanity.jpeg')

ratio = image.shape[0] / 200.0
orig = image.copy()
image = imutils.resize(image, height=200)

hsv = cv2.cvtColor(image, cv2.COLOR_BGR2HSV)

# defining the range of black color
blackLowerBound = np.array([0, 0, 0], np.uint8)
blackUpperBound = np.array([180, 255, 30], np.uint8)

# defining the Range of white color
whiteLowerBound = np.array([0, 0, 200], np.uint8)
whiteUpperBound = np.array([180, 255, 255], np.uint8)


# finding the range of red,blue and yellow color in the image
black = cv2.inRange(hsv, blackLowerBound, blackUpperBound)
white = cv2.inRange(hsv, whiteLowerBound, whiteUpperBound)

# Morphological transformation, Dilation
kernal = np.ones((5, 5), "uint8")

black = cv2.dilate(black, kernal)
res = cv2.bitwise_and(image, image, mask=black)

white = cv2.dilate(white, kernal)
res1 = cv2.bitwise_and(image, image, mask=white)

(_, contours, hierarchy) = cv2.findContours(black, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)

for pic, contour in enumerate(contours):
    area = cv2.contourArea(contour)
    if area > 300:
        x, y, w, h = cv2.boundingRect(contour)
        image = cv2.rectangle(image, (x, y), (x + w, y + h), (52, 234, 61), 2)
        cv2.putText(image, "black color", (x, y), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (52, 234, 61))

(_, contours, hierarchy) = cv2.findContours(white, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)

for pic, contour in enumerate(contours):
    area = cv2.contourArea(contour)
    if area > 300:
        x, y, w, h = cv2.boundingRect(contour)

        image = cv2.rectangle(image, (x, y), (x + w, y + h), (52, 234, 61), 2)
        cv2.putText(image, "white color", (x, y), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (52, 234, 61))


cv2.imwrite("colorDetection.jpg", image)
