import re
import tkinter as tk
import cv2
from PIL import ImageTk, Image


class newRegion:
    def __init__(self, window, window_title, game, currCard):
        self.window = window
        self.window.title(window_title)
        self.game = game
        self.directoryPath = None
        self.fileName = None
        self.newImage = None
        self.croppedImage = None
        self.destroyNow = False
        self.destroyLater = False
        self.newImage = currCard

        self.selectButton = tk.Button(self.window, text="Current Template", width=15, command=self.verifyTemplate)
        self.selectButton.pack(side=tk.TOP)

        self.showRegions()
        self.img = ImageTk.PhotoImage(Image.open('labeledRegions.jpg'))
        self.panel = tk.Label(self.window, compound=tk.BOTTOM, image=self.img)
        self.panel.pack()

        # After it is called once, the update method will be automatically called every delay milliseconds
        self.window.mainloop()

    def showRegions(self):
        self.newImage = cv2.imread(self.imageName)
        allRegionCoors = []
        f = open(self.game + "/regions.txt", "r")
        f1 = f.readlines()
        for x in f1:
            line = re.split('\s', x)
            for name in line[1:]:
                regionNames = []
                name = re.sub(':', ' ', name)
                labelName = re.split('\s', name)
                if line[0] == self.editTemplate.fileName:
                    if len(labelName) == 1:
                        continue
                    labelName[1] = re.sub('\(', '', labelName[1])
                    labelName[1] = re.sub('\)', '', labelName[1])
                    labelName[1] = re.sub(',', ' ', labelName[1])
                    regionNames.append(labelName[1])
                    regionNames = list(filter(lambda a: a != '', regionNames))
                    regionCoors = re.split('\s', regionNames[0])
                    allRegionCoors.append(regionCoors)

        for i in allRegionCoors:
            x, y, w, h = i
            cv2.rectangle(self.newImage, (int(x), int(y)), (int(w), int(h)), (0, 255, 0), 2)
            # self.croppedImage = self.newImage[int(y):int(y) + int(h), int(x):int(x) + int(w)]
            cv2.imwrite('labeledRegions.jpg', self.newImage)


class verifyEditingTemplate:
    def __init__(self, editTemplate, image, game):
        self.imageName = image
        self.game = game
        self.templateName = None
        self.newImage = None
        self.editTemplate = editTemplate
        self.subRoot = tk.Toplevel()
        self.subRoot.title("Edit this template?")

        self.showRegions()
        tk.Label(self.subRoot, text='Is this the template you want to edit?').pack()
        img = ImageTk.PhotoImage(Image.open('labeledRegions.jpg'))
        self.panel = tk.Label(self.subRoot, compound=tk.BOTTOM, image=img)
        self.panel.pack()

        self.yesButton = tk.Button(self.subRoot, text="Yes", width=15, command=self.yesContinue)
        self.yesButton.pack()

        self.noButton = tk.Button(self.subRoot, text="No", width=15, command=self.goBack)
        self.noButton.pack()

        self.subRoot.mainloop()


