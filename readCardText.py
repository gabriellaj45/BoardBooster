import tkinter as tk
from PIL import ImageTk, Image
import re
import cv2
import pytesseract
from os import system
from imagePreProcessing import *
from getColor import *


class readCardText:
    def __init__(self, window, window_title, cardFile, templateFile, game):
        self.window = window
        self.window.title(window_title)
        self.label = ''
        self.cardFile = cardFile
        self.templateFile = templateFile
        self.newImage = None
        self.textOnScreen = None
        self.game = game

        self.regionNames = []
        self.regions = []
        self.regionValues = []
        self.getLabelNames()

        self.img = ImageTk.PhotoImage(Image.open(self.cardFile))

        self.panel = tk.Label(self.window, image=self.img)
        self.panel.pack(side=tk.LEFT, fill=tk.BOTH)

        tk.Label(self.window, text='Card Regions: ', fg='blue').pack(anchor=tk.N)

        for region in self.regionNames:
            var = tk.IntVar()
            chk = tk.Checkbutton(self.window, text=region, variable=var)
            chk.pack(side=tk.TOP, anchor=tk.W)
            self.regions.append(region)
            self.regionValues.append(var)
        '''
        self.text = tk.Text(self.window, height=10, width=50)
        self.text.insert(tk.INSERT, self.label)
        self.text.pack()
        '''

        self.readButton = tk.Button(self.window, text="Read Text", width=15, command=self.readText)
        self.readButton.pack()

        self.window.mainloop()

    def getText(self):
        text = self.text.get("1.0", tk.END)
        self.textOnScreen = text
        self.window.destroy()

    def readAllText(self):
        cardText = pytesseract.image_to_string(Image.open(self.cardFile))
        cardText = re.sub('\n', ' ', cardText)
        cardText = re.sub('[^A-Za-z0-9\s]+', '', cardText)
        print(cardText)
        system('say -v Samantha ' + cardText)

    def readText(self):
        color = 'Color'
        for regionName, isChecked in zip(self.regions, self.regionValues):
            if isChecked.get() and color in regionName:
                color = getDominantColor(self.cardFile)
                system('say -v Samantha ' + color)
                break
        self.getSelectedText()
        self.textOnScreen = re.sub('\n', ' ', self.textOnScreen)
        self.textOnScreen = re.sub('[^A-Za-z0-9\s]+', '', self.textOnScreen)
        system('say -v Samantha ' + self.textOnScreen)

    def getSelectedText(self):
        allRegionCoors = []
        for regionName, isChecked in zip(self.regions, self.regionValues):
            if isChecked.get():
                f = open(self.game + "/regions.txt", "r")
                f1 = f.readlines()
                for x in f1:
                    line = re.split('\s', x)
                    for name in line[1:]:
                        regionNames = []
                        name = re.sub(':', ' ', name)
                        labelName = re.split('\s', name)
                        if labelName[0] == regionName and line[0] == self.templateFile:
                            labelName[1] = re.sub('\(', '', labelName[1])
                            labelName[1] = re.sub('\)', '', labelName[1])
                            labelName[1] = re.sub(',', ' ', labelName[1])
                            regionNames.append(labelName[1])
                            regionNames = list(filter(lambda a: a != '', regionNames))
                            regionCoors = re.split('\s', regionNames[0])
                            allRegionCoors.append(regionCoors)
        self.newImage = cv2.imread(self.cardFile)
        for i in allRegionCoors:
            x, y, w, h = i
            cv2.rectangle(self.newImage, (int(x), int(y)), (int(w), int(h)), (0, 255, 0), 2)
            croppedImage = self.newImage[int(y):int(h), int(x):int(w)]
            cv2.imwrite('extractedRegion.jpg', croppedImage)

            # fileToProcess = 'extractedRegion.jpg'
            # imagePreProcessing(fileToProcess, fileToProcess)

            self.textOnScreen = pytesseract.image_to_string(Image.open('extractedRegion.jpg'))

        cv2.imwrite('updatedImage.jpg', self.newImage)
        if self.newImage is not None:
            img2 = ImageTk.PhotoImage(Image.open('updatedImage.jpg'))
            self.panel.configure(image=img2)
            self.panel.image = img2

    def getLabelNames(self):
        f = open(self.game + "/regions.txt", "r")
        f1 = f.readlines()
        for x in f1:
            line = re.split('\s', x)
            if line[0] == self.templateFile:
                for name in line[1:]:
                    name = re.sub(':', ' ', name)
                    labelName = re.split('\s', name)
                    self.regionNames.append(labelName[0])
                    self.regionNames = list(filter(lambda a: a != '', self.regionNames))
