from printLabel import *
from matchTemplate import *
from createPDF import *


def genLabels(game):
    for filename in os.listdir(game + '/processCards/'):
        path = game + "/processCards/"
        cardFile = path + filename
        templateMatch = matchTemplate(cardFile, game)
        # name = selectTemplate(tk.Tk(), "selectTemplate", cardFile)
        # templateName = selectTemplate.getFileName(name)
        printLabel(tk.Tk(), "Print Label", cardFile, templateMatch, game)

    genPDF(game)
