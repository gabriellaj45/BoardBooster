import cv2
import numpy as np
import os
import re


def checkPoint(x1, y1, x2, y2, x, y):
    if x >= x1 and x <= x2 and y >= y1 and y <= y2:
        return True
    else:
        return False


def getSymbolName(cardFile, coors):
    symbolsFound = []
    cardSearching = cv2.imread(cardFile)
    cardSearchingGray = cv2.cvtColor(cardSearching, cv2.COLOR_BGR2GRAY)

    for filename in os.listdir('static/cardSymbols/'):
        path = "static/cardSymbols/"
        cardFile = path + filename
        symbolLookingFor = cv2.imread(cardFile, 0)
        w, h = symbolLookingFor.shape[::-1]

        res = cv2.matchTemplate(cardSearchingGray, symbolLookingFor, cv2.TM_CCOEFF_NORMED)

        threshold = 0.9
        loc = np.where(res >= threshold)
        '''
        filename = re.sub('.jpg', ' ', filename)
        for pt in zip(*loc[::-1]):
            symbolsFound.append(filename)
        symbolsFound = set(symbolsFound)
        for word in symbolsFound:
            symbolName = symbolName + ' ' + word
        '''
        # cv2.rectangle(cardSearching, pt, (pt[0] + w, pt[1] + h), (0, 0, 255), 1)
        filename = re.sub('.jpg', ' ', filename)
        for pt in zip(*loc[::-1]):
            if checkPoint(pt[0], pt[1], pt[0] + w, pt[1] + h, coors[0], coors[1]):
                symbolsFound.append(filename)

    return symbolsFound


def detectSymbols(file):
    symbolsFound = []
    cardSearching = cv2.imread(file)
    cardSearchingGray = cv2.cvtColor(cardSearching, cv2.COLOR_BGR2GRAY)

    for filename in os.listdir('static/cardSymbols/'):
        path = "static/cardSymbols/"
        cardFile = path + filename

        symbolLookingFor = cv2.imread(cardFile, 0)
        w, h = symbolLookingFor.shape[::-1]

        res = cv2.matchTemplate(cardSearchingGray, symbolLookingFor, cv2.TM_CCOEFF_NORMED)

        threshold = 0.9
        loc = np.where(res >= threshold)
        for pt in zip(*loc[::-1]):
            symbolsFound.append((pt, (pt[0] + w, pt[1] + h)))
            cv2.rectangle(cardSearchingGray, pt, (pt[0] + w, pt[1] + h), (0, 0, 255), 2)
    cv2.imwrite('symbolsTest.png', cardSearchingGray)

    return symbolsFound
