import os
import re
from labelCards import *
import tkinter as tk


def getRegions(game):
    regionFile = open(game + "/regions.txt", "a")
    for filename in os.listdir(game + '/cardTemplates/'):
        path = game + "/cardTemplates/"
        labelCards(tk.Tk(), "Label Cards", filename, path + filename, game)
        regionFile.write('\n')


def getRegionInfo(filename):
    f = open("regions.txt", "r")

    f1 = f.readlines()
    regions = []
    for x in f1:
        line = re.split('\s', x)
        if line[0] == filename:
            for coor in line[1:]:
                coor = coor.strip('(')
                coor = coor.strip(')')
                coordinates = re.split(',', coor)
                regions.append(coordinates)
    return regions
