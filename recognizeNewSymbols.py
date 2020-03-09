from textDetection import *
from readSymbols import *
from checkNewSymbols import *
from addNewSymbol import *


# img = cv2.imread('Cards Against Humanity/cardTemplates/Black.jpg')
# img = cv2.imread('dominionSymbolTest.jpg')
# template = matchTemplate('Cards Against Humanity/processCards/0.jpg', 'Cards Against Humanity')
# template = 'Black.jpg'

def getSymbolRegions(game, template):
    allRegionCoors = []
    f = open(game + "/regions.txt", "r")
    f1 = f.readlines()
    for x in f1:
        line = re.split('\s', x)
        for name in line[1:]:
            name = re.sub(':', ' ', name)
            labelName = re.split('\s', name)
            if line[0] == template and ('Symbols' in labelName[0] or 'Text' in labelName[0]):
                if len(labelName) == 1:
                    continue
                labelName[1] = re.sub('\(', '', labelName[1])
                labelName[1] = re.sub('\)', '', labelName[1])
                labelName[1] = re.sub(',', ' ', labelName[1])
                region = str(labelName[1])
                region = re.split('\s', region)
                region = list(filter(lambda a: a != '', region))
                regionX1 = int(region[0])
                regionY1 = int(region[1])
                regionX2 = int(region[2])
                regionY2 = int(region[3])
                region = regionX1, regionY1, regionX2, regionY2
                allRegionCoors.append(region)
    return allRegionCoors


def checkForTextAndSymbols(image, game, cardImage):
    cv2.imwrite('cropped.jpg', image)
    cv2.imwrite('orig.jpg', cardImage)
    symbolsFound = detectSymbols('cropped.jpg', game)
    image = cv2.imread('cropped.jpg')
    for symbol in symbolsFound:
        x1 = symbol[0][0]
        y1 = symbol[0][1]
        x2 = symbol[1][0]
        y2 = symbol[1][1]
        cv2.rectangle(img=image, pt1=(x1, y1), pt2=(x2, y2), color=(255, 255, 255), thickness=-1)

    textFound = findText('cropped.jpg')

    for text in textFound:
        x1 = int(text[0][0])
        y1 = int(text[0][1])
        x2 = int(text[2][0])
        y2 = int(text[2][1])
        # Draw a white, filled rectangle on the mask image
        cv2.rectangle(img=image, pt1=(x1, y1), pt2=(x2, y2), color=(255, 255, 255), thickness=-1)

    cv2.imwrite('cropped.jpg', image)

    check = checkForNewSymbols(symbolsFound, textFound)

    if check:
        addNewSymbol(game, 'cropped.jpg')
    else:
        print('no new symbols')


def findNewSymbols(game, cardImage, template):
    print('checking new symbols')
    cardImage = cv2.imread(cardImage)
    symbolRegionCoors = getSymbolRegions(game, template)
    # checkForTextAndSymbols(cardImage, game, cardImage)

    if len(symbolRegionCoors) == 0:
        print('no symbol coordinates')
        checkForTextAndSymbols(cardImage, game, cardImage)

    for i in symbolRegionCoors:
        x, y, w, h = i
        cropImage = cardImage[y:h, x:w]
        checkForTextAndSymbols(cropImage, game, cardImage)

