from addNewRegion import *
from textDetection import findText


def insideRect(x1, y1, x2, y2, x, y):
    if x > x1 and x < x2 and y > y1 and y < y2:
        return True
    else:
        return False


def checkNewText(fileName, game, template):
    regionName = 'Text'
    textBoxes = findText(fileName)
    for box in textBoxes:
        x1 = int(box[0][0])
        y1 = int(box[0][1])
        x2 = int(box[1][0])
        y2 = int(box[1][1])
        f = open(game + "/regions.txt", "r")
        f1 = f.readlines()
        for x in f1:
            line = re.split('\s', x)
            for name in line[1:]:
                name = re.sub(':', ' ', name)
                labelName = re.split('\s', name)
                if regionName in labelName[0] and line[0] == template:
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

        if x1 >= regionX1 and y1 >= regionY1:
            if x2 <= regionX2 and y2 <= regionY2:
                continue
            else:
                addNewRegion(game, template, fileName, textBoxes)
                break
        else:
            addNewRegion(game, template, fileName, textBoxes)
            break
