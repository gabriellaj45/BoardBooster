import pytesseract
from PIL import Image
import cv2
import imutils
'''

picture = cv2.VideoCapture(0)

_, cardImage = picture.read()

cardImage = imutils.resize(cardImage, height=600)

cv2.imwrite('cardImage.jpg', cardImage)

cardImage = cv2.imread('testBlack.png')
cardImage = cv2.cvtColor(cardImage, cv2.COLOR_BGR2GRAY)
cardImage = cv2.threshold(cardImage, 0, 255, cv2.THRESH_BINARY | cv2.THRESH_OTSU)[1]
cv2.imwrite('cardImage.jpg', cardImage)
'''
# text = pytesseract.image_to_string(Image.open('Cards Against Humanity/cardTemplates/White.jpg'))
text = pytesseract.image_to_string(Image.open('extractedRegion.jpg'))
# text = text.replace("_", "(blank)")
print(text)
