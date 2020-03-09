import os
from labelSymbols import *


def extractSymbols(game):
    for filename in os.listdir(game + '/processSymbols/'):
        path = game + "/processSymbols/"
        cardFile = path + filename
        labelSymbols(tk.Tk(), "Label Symbols", cardFile, game)
