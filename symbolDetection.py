import cv2
import numpy as np
import os
import tkinter as tk
from PIL import ImageTk, Image
import re


class symbolDetection:
    def __init__(self, window, window_title, cardFile, game):
        self.window = window
        self.window.title(window_title)
        self.label = ''
        self.cardFile = cardFile
        self.symbolName = ''
        self.game = game
        self.numSymbols = 0
        self.symbolsFound = []

        self.img = ImageTk.PhotoImage(Image.open(self.cardFile))

        self.panel = tk.Label(self.window, image=self.img)
        self.panel.pack(side=tk.TOP, fill=tk.BOTH)

        self.quitButton = tk.Button(self.window, text="Done", width=15, command=self.window.destroy)
        self.quitButton.pack(side=tk.BOTTOM, anchor=tk.S)

        self.detectSymbols(self.cardFile, self.game)

        self.window.mainloop()

    def detectSymbols(self, file, game):
        cardSearching = cv2.imread(file)
        cardSearchingGray = cv2.cvtColor(cardSearching, cv2.COLOR_BGR2GRAY)

        for filename in os.listdir(game + '/cardSymbols/'):
            path = game + "/cardSymbols/"
            cardFile = path + filename
            symbolLookingFor = cv2.imread(cardFile, 0)
            w, h = symbolLookingFor.shape[::-1]

            res = cv2.matchTemplate(cardSearchingGray, symbolLookingFor, cv2.TM_CCOEFF_NORMED)

            threshold = 0.85
            loc = np.where(res >= threshold)
            filename = re.sub('.jpg', ' ', filename)
            for pt in zip(*loc[::-1]):
                self.numSymbols = self.numSymbols + 1
                self.symbolsFound.append((pt, (pt[0] + w, pt[1] + h)))
                cv2.rectangle(cardSearching, pt, (pt[0] + w, pt[1] + h), (0, 0, 255), 1)
                cv2.putText(cardSearching, filename, (pt[0], pt[1]), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 0), 1)
        self.symbolsFound = set(self.symbolsFound)
        # display in tkinter canvas
        cv2.imwrite('symbolsOnCard.jpg', cardSearching)
        img2 = ImageTk.PhotoImage(Image.open('symbolsOnCard.jpg'))
        self.panel.configure(image=img2)
        self.panel.image = img2

