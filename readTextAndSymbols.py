import cv2
from textDetection import *
from readSymbols import *
from collections import OrderedDict
from getText import *


def textAndSymbols(game, file):
    textSymbolsDict = {}
    textSymbolsOGCoors = {}

    textFound = findText(file)
    symbolsFound = detectSymbols(file, game)
    index = 0

    for i in textFound:
        textId = 't' + str(index)
        textX1 = int(i[0][0])
        textY1 = int(i[0][1])
        textX2 = int(i[2][0])
        textY2 = int(i[2][1])

        midpoint = (textX2 + textX1) / 2, (textY2 + textY1) / 2
        textSymbolsDict[textId] = midpoint
        textSymbolsOGCoors[textId] = ((textX1, textY1), (textX2, textY2))
        index = index + 1
    index = 0
    for j in symbolsFound:
        symbolId = 's' + str(index)
        symbolX1 = j[0][0]
        symbolY1 = j[0][1]
        symbolX2 = j[1][0]
        symbolY2 = j[1][1]

        midpoint = (symbolX2 + symbolX1) / 2, (symbolY2 + symbolY1) / 2
        textSymbolsDict[symbolId] = midpoint
        textSymbolsOGCoors[symbolId] = ((symbolX1, symbolY1), (symbolX2, symbolY2))
        index = index + 1

    textSymbolsDict = OrderedDict(sorted(textSymbolsDict.items(), key=lambda k: [k[1], k[0]]))

    finalString = ''
    img = cv2.imread(file)
    if len(symbolsFound) == 0:
        print('no symbols found')
        finalString = pytesseract.image_to_string(Image.open(file))
    elif len(textFound) == 0:
        finalString = getSymbolName(game, file)
        print('no text found')
    else:
        print('both found')
        for x, y in textSymbolsDict.items():
            '''
            if 't' in x:
                textCoors = textSymbolsOGCoors[x]
                textX1 = int(textCoors[0][0])
                textY1 = int(textCoors[0][1])
                textX2 = int(textCoors[1][0])
                textY2 = int(textCoors[1][1])

                cropImage = img[textY1 - 5:textY2 + 5, textX1 - 5:textX2 + 5]
                cv2.imwrite('textCropped.jpg', cropImage)

                text = readText('textCropped.jpg')
                finalString = finalString + ' ' + text
                continue
        '''
            if 's' in x:
                '''
                symbolCoors = textSymbolsOGCoors[x]
                symbolX1 = int(symbolCoors[0][0])
                symbolY1 = int(symbolCoors[0][1])
                symbolX2 = int(symbolCoors[1][0])
                symbolY2 = int(symbolCoors[1][1])

                # cropImage = img[symbolY1:symbolY2, symbolX1:symbolX2]
                cv2.imwrite('symbolCropped.jpg', img)
                '''
                symbolsFound = getSymbolName(game, 'symbolCropped.jpg', y)
                symbolsFound = set(symbolsFound)
                for word in symbolsFound:
                    textSymbolsDict[x] = word
                    finalString = finalString + ' ' + word
    '''
    print(finalString)
    for x, y in textSymbolsDict.items():
        print(x,y)
    '''
    return finalString


'''
textFound = findText('Cards Against Humanity/cardTemplates/Black2.jpg')
symbolsFound = symbolDetection(tk.Tk(), "Symbols Found", 'Cards Against Humanity/cardTemplates/Black2.jpg', 'Cards Against Humanity')
'''
'''
coorList = [[1, 2],[0, 2],[2, 1],[1, 1],[2, 2],[2, 0],[0, 1],[1, 0],[0,0]]

coorList = sorted(coorList, key=lambda k: [k[1], k[0]])

print(coorList)
'''