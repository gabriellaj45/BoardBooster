from matchTemplate import *
from collections import OrderedDict
import re

finalText = ''
cardFile = '/Users/superhuman/PycharmProjects/BoardBooster/static/newCards/0.png'
templateName = matchTemplate(cardFile)
theImage = cv2.imread(cardFile)
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

# print(v for k, v in sorted(allRegionCoors.items(), key=lambda item: item[0][1]))
allRegionCoors = sorted(allRegionCoors.items(), key=lambda k: [k[0][1], k[0][0]])
[print(i[0]) for i in allRegionCoors]
    # print(allRegionCoors[i][0])