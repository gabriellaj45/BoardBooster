import os
import tkinter as tk
from PIL import ImageTk, Image
import re
import cv2
from labelCards import *


class editTemplate:
    def __init__(self, window, window_title, game):
        self.window = window
        self.window.title(window_title)
        self.game = game
        self.directoryPath = None
        self.fileName = None
        self.newImage = None
        self.croppedImage = None
        self.destroyNow = False
        self.destroyLater = False

        tk.Label(self.window, text='Select template you wish to edit', fg='blue').pack(side=tk.TOP)
        self.L = tk.Listbox(selectmode=tk.SINGLE)
        self.delay = 15
        self.fileDict = {}
        self.update()
        self.L.pack()

        self.selectButton = tk.Button(self.window, text="Edit Template", width=15, command=self.verifyTemplate)
        self.selectButton.pack(side=tk.TOP)

        self.image = tk.Label(self.window, compound=tk.BOTTOM, text='Card Template')
        self.image.pack(side=tk.RIGHT)

        self.imageName = ''

        self.L.bind('<ButtonRelease-1>', self.list_entry_clicked)

        # After it is called once, the update method will be automatically called every delay milliseconds
        self.window.mainloop()

    def update(self):
        self.directoryPath = self.game + '/cardTemplates/'
        for fileName in os.listdir(self.directoryPath):
            filePath = os.path.join(self.directoryPath, fileName)
            file = ImageTk.PhotoImage(Image.open(filePath))
            self.fileDict[fileName] = file
            self.L.insert(tk.END, fileName)
        '''
        if self.destroyNow:
            self.window.destroy()
            labelCards(tk.Tk(), "Label Cards", self.fileName, self.imageName, self.game)
        '''

    def verifyTemplate(self):
        verifyEditingTemplate(self, self.imageName, self.game)
        if self.destroyNow:
            self.window.destroy()
            labelCards(tk.Tk(), "Label Cards", self.fileName, self.imageName, self.game)
        if self.destroyLater:
            self.window.destroy()

    def getFileName(self):
        return self.imageName

    def setFileName(self, image):
        self.imageName = self.directoryPath + image
        self.fileName = image

    def list_entry_clicked(self, *ignore):
        self.imageName = self.L.get(self.L.curselection()[0])
        self.image.config(image=self.fileDict[self.imageName])
        self.setFileName(self.imageName)
        return self.imageName


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

    def yesContinue(self):
        check = addDeleteTemplates(self.game, self.editTemplate.fileName)
        if check.both:
            self.editTemplate.destroyNow = True
        else:
            self.editTemplate.destroyLater = True
        self.subRoot.quit()
        self.subRoot.destroy()

    def goBack(self):
        self.editTemplate.destroyNow = False
        self.subRoot.quit()
        self.subRoot.destroy()


class addDeleteTemplates:
    def __init__(self, game, imageName):
        self.value = None
        self.game = game
        self.imageName = imageName
        self.templateName = None
        self.both = False
        self.subRoot = tk.Toplevel()
        self.subRoot.title("Edit Template")

        tk.Label(self.subRoot, text='Would you like to add or delete template?').pack()

        self.continueButton = tk.Button(self.subRoot, text="Add New Region(s)", width=15, command=self.addRegion)
        self.continueButton.pack()

        self.returnButton = tk.Button(self.subRoot, text="Delete & Add Region(s)", width=15, command=self.bothRegion)
        self.returnButton.pack()

        self.returnButton = tk.Button(self.subRoot, text="Delete Region(s)", width=15, command=self.deleteRegion)
        self.returnButton.pack()

        self.subRoot.mainloop()

    def addRegion(self):
        self.both = True
        self.subRoot.quit()
        self.subRoot.destroy()

    def bothRegion(self):
        deleteWhichRegion(self.game, self.imageName)
        self.both = True
        self.subRoot.quit()
        self.subRoot.destroy()

    def deleteRegion(self):
        deleteWhichRegion(self.game, self.imageName)
        self.subRoot.quit()
        self.subRoot.destroy()


class deleteWhichRegion:
    def __init__(self, game, file):
        self.game = game
        self.file = file
        self.regionNames = []
        self.regions = []
        self.regionValues = []
        self.subRoot = tk.Toplevel()
        self.subRoot.title("Remove Regions")

        tk.Label(self.subRoot, text='Select regions you would like to delete').pack()
        self.getLabelNames()

        for region in self.regionNames:
            var = tk.IntVar()
            chk = tk.Checkbutton(self.subRoot, text=region, variable=var)
            chk.pack(side=tk.TOP, anchor=tk.W)
            self.regions.append(region)
            self.regionValues.append(var)

        self.continueButton = tk.Button(self.subRoot, text="Delete Selected Regions", width=20,
                                        command=self.selectRegionsToDelete)
        self.continueButton.pack()

        self.returnButton = tk.Button(self.subRoot, text="Exit", width=20, command=self.goBack)
        self.returnButton.pack()

        self.subRoot.mainloop()

    def selectRegionsToDelete(self):
        for regionCoor, isChecked in zip(self.regions, self.regionValues):
            if isChecked.get():
                f = open(self.game + "/regions.txt", "r+")
                fileText = f.read()
                fileText = fileText.replace(regionCoor, "")
                f.close()

                f = open(self.game + "/regions.txt", "w+")
                f.write(fileText)
                f.close()
        self.subRoot.quit()
        self.subRoot.destroy()

    def goBack(self):
        self.subRoot.quit()
        self.subRoot.destroy()

    def getLabelNames(self):
        f = open(self.game + "/regions.txt", "r")
        f1 = f.readlines()
        for x in f1:
            line = re.split('\s', x)
            if line[0] == self.file:
                for name in line[1:]:
                    self.regionNames.append(name)
                    self.regionNames = list(filter(lambda a: a != '', self.regionNames))
