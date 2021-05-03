import cv2
import os
from histogramColorClassifier import HistogramColorClassifier


def matchTemplate(image):
    histClassifier = HistogramColorClassifier(channels=[0, 1, 2],
                                              hist_size=[128, 128, 128],
                                              hist_range=[0, 256, 0, 256, 0, 256],
                                              hist_type='BGR')
    index = 0
    for filename in os.listdir('static/cardTemplates/'):
        path = "static/cardTemplates/"
        varName = cv2.imread(path + filename)
        histClassifier.addModelHistogram(varName, filename)
        index = index + 1

    if index == 0:
        return
    image = cv2.imread(image)
    if image is not None:
        return histClassifier.returnBestMatchName(image)
    else:
        print('no image')


'''
import cv2
import os
import numpy as np


class matchTemplate:
    def __init__(self, image, game):
        self.game = game
        self.image = image
        self.templateMatch = None
        self.findBestMatch()

    def findBestMatch(self):
        bestTemplateMatch = 100000000000000000
        templateMatchName = None

        for filename in os.listdir(self.game + '/cardTemplates/'):
            path = self.game + "/cardTemplates/"
            template = cv2.imread(path + filename)
            card = cv2.imread(self.image)
            diff_img = cv2.absdiff(card, template)
            templateDiff = int(np.sum(diff_img) / 255)

            if templateDiff < bestTemplateMatch:
                bestTemplateMatch = templateDiff
                templateMatchName = filename
        self.templateMatch = templateMatchName
        return templateMatchName
'''
