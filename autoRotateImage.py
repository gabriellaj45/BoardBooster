import cv2

import numpy as np

img = cv2.imread("Cards Against Humanity/cardTemplates/Black2.jpg")
gray_img=cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
gray_img=cv2.bitwise_not(gray_img)
coordinates = np.column_stack(np.where(gray_img > 0))
ang=cv2.minAreaRect(coordinates)[-1]

if ang < -45:
    ang = -(90 + ang)
else:
    ang = -ang

height, width = img.shape[:2]

center = (width / 2, height / 2)

rotationMatrix = cv2.getRotationMatrix2D(center, ang, 1.0)

rotated_img = cv2.warpAffine(img, rotationMatrix, (width, height), borderMode=cv2.BORDER_REFLECT)
cv2.imshow("Rotated Image", rotated_img)

cv2.waitKey(0)