'''
from PIL import Image

im = Image.open('static/finalBoard.png')

resizeIm = im.resize((6000, 6000))

resizeIm.save('finalBoardTest.png')
'''
import cv2
import re
from collections import OrderedDict

finalText = ''
templateName = 'Action.png'
theImage = cv2.imread('static/newCards/0.png')
allRegionCoors = {}
f = open("static/userData/regions.txt", "r")
f1 = f.readlines()

for x in f1:
    line = re.split('\s', x)
    for name in line[1:]:
        regionNames = []
        name = re.sub(':', ' ', name)
        labelName = re.split('\s', name)
        if line[0] == templateName and len(labelName) > 1:
            labelName[1] = re.sub('\(', '', labelName[1])
            labelName[1] = re.sub('\)', '', labelName[1])
            labelName[1] = re.sub(',', ' ', labelName[1])
            regionNames.append(labelName[1])
            regionNames = list(filter(lambda a: a != '', regionNames))
            regionCoors = re.split('\s', regionNames[0])
            x, y, w, h = regionCoors
            regionCoors.append(labelName[0])
            midpoint = (int(x) + int(w)) / 2, (int(y) + int(h)) / 2
            allRegionCoors[midpoint] = regionCoors

allRegionCoors = OrderedDict(sorted(allRegionCoors.items(), key=lambda k: [k[1], k[0]]))

for regionName, regionCoors in allRegionCoors.items():
    tempX = 0
    tempW = 0
    tempY = 0
    tempH = 0
    x, y, w, h, _ = regionCoors
    if int(h) < int(y):
        tempX = x
        tempW = w
        w = x
        x = tempW
        tempY = y
        tempH = h
        h = y
        y = tempH
    elif int(x) > int(w):
        tempX = x
        tempW = w
        w = x
        x = tempW
        tempY = y
        tempH = h
        h = y
        y = tempH
    elif int(x) == int(w):
        continue
    elif int(y) == int(h):
        continue
    croppedImage = theImage[int(y):int(h), int(x):int(w)]