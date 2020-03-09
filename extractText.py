import cv2
import pytesseract
from printLabel import *
# from getRegions import getRegionInfo
from selectTemplate import *


def extractText():
    index = 1
    regions = []
    for filename in os.listdir('processCards/'):
        cardLabel = ''
        path = "processCards/"
        cardFile = path + filename
        card = cv2.imread(cardFile)
        name = selectTemplate(tk.Tk(), "selectTemplate", cardFile)
        templateName = selectTemplate.getFileName(name)
        # regions = getRegionInfo(templateName)
        regionSize = len(regions)
        for coordinate in regions:
            while index < regionSize:
                x = int(coordinate[0])
                w = int(coordinate[2]) - int(coordinate[0])
                y = int(coordinate[1])
                h = int(coordinate[3]) - int(coordinate[1])
                croppedImage = card[y:y + h, x:x + w]
                cv2.imwrite('extractedRegion.jpg', croppedImage)

                text = pytesseract.image_to_string(Image.open('extractedRegion.jpg'))
                # text = text.replace("_", " blank ")
                cardLabel = text + "\n"
                index = index + 1
        printLabel(tk.Tk(), "Print Label", cardLabel, cardFile)
