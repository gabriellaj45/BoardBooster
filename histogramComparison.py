import cv2
import os
from histogramColorClassifier import HistogramColorClassifier


def findMatch(image, game):
    histClassifier = HistogramColorClassifier(channels=[0, 1, 2],
                                              hist_size=[128, 128, 128],
                                              hist_range=[0, 256, 0, 256, 0, 256],
                                              hist_type='BGR')
    index = 0
    for filename in os.listdir(game + '/cardTemplates/'):
        path = game + "/cardTemplates/"
        varName = cv2.imread(path + filename)
        histClassifier.addModelHistogram(varName, filename)
        index = index + 1

    image = cv2.imread(image)
    print(histClassifier.returnBestMatchName(image))
