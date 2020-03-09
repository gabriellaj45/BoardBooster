from playsound import playsound
from newRegion import *
from os import system
from labelCards import *


class addNewRegion:
    def __init__(self, game, template, file, textLoc, ogCard):
        playsound('labelGenSoundAlert.mp3')
        self.game = game
        self.template = template
        self.file = file
        self.allRegionCoors = []
        self.newImage = None
        self.tempName = None
        self.textLoc = textLoc
        self.subRoot = tk.Toplevel()
        self.subRoot.title("New Information Found")

        self.canvas = tk.Canvas(self.subRoot, width=100, height=100)
        system('say -v Samantha New text found')
        tk.Label(self.subRoot, text='Information detected outside the established regions. Would you like to add new '
                                    'region or template?').pack()

        self.drawRegions()

        self.cardTemplate = cv2.imread(ogCard)

        self.img = ImageTk.PhotoImage(Image.open('extractedRegion.jpg'))
        self.panel = tk.Label(self.subRoot, compound=tk.BOTTOM, image=self.img)
        self.panel.pack()

        self.newRegionButton = tk.Button(self.subRoot, text="Add New Region", width=15, command=self.addRegionNew)
        self.newRegionButton.pack()

        self.newTemplateButton = tk.Button(self.subRoot, text="Add New Template", width=15, command=self.addNewTemplate)
        self.newTemplateButton.pack()

        self.newTemplateButton = tk.Button(self.subRoot, text="No Thanks", width=15, command=self.noAdding)
        self.newTemplateButton.pack()

        self.subRoot.mainloop()

    def noAdding(self):
        self.subRoot.quit()
        self.subRoot.destroy()

    def addRegionNew(self):
        self.subRoot.quit()
        self.subRoot.destroy()
        self.showRegions()
        labelCards(tk.Toplevel(), "Label Cards", self.template, 'labeledRegions.jpg', self.game)

    def addNewTemplate(self):
        self.subRoot.quit()
        self.subRoot.destroy()
        name = nameTemplate()
        self.fileName = self.game + "/cardTemplates/" + name.templateName + ".jpg"
        cv2.imwrite(self.fileName, cv2.cvtColor(self.cardTemplate))
        self.tempName = name.templateName + ".jpg"
        labelCards(tk.Toplevel(), "Label Cards", self.tempName, self.fileName, self.game)

    def checkPoint(self, x1, y1, x2, y2, x, y):
        if x >= x1 and x <= x2 and y >= y1 and y <= y2:
            return True
        else:
            return False

    def getRegionCoors(self):
        f = open(self.game + "/regions.txt", "r")
        f1 = f.readlines()
        for x in f1:
            line = re.split('\s', x)
            for name in line[1:]:
                name = re.sub(':', ' ', name)
                labelName = re.split('\s', name)
                if line[0] == self.template and 'Text' in labelName[0]:
                    if len(labelName) == 1:
                        continue
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
                    region = regionX1, regionY1, regionX2, regionY2
                    self.allRegionCoors.append(region)

    def drawRegions(self):
        inRegion = False
        self.newImage = cv2.imread(self.file)
        for box in self.textLoc:
            x1 = int(box[0][0])
            y1 = int(box[0][1])
            x2 = int(box[2][0])
            y2 = int(box[2][1])
            midpointX, midpointY = (x2 + x1) / 2, (y2 + y1) / 2
            self.getRegionCoors()
            for i in self.allRegionCoors:
                regionX1, regionY1, regionX2, regionY2 = i
                if self.checkPoint(regionX1, regionY1, regionX2, regionY2, midpointX, midpointY):
                    inRegion = True
                    break
                else:
                    inRegion = False
            if inRegion:
                cv2.rectangle(self.newImage, (x2, y2), (x1, y1), (0, 255, 0), 1)
            else:
                cv2.rectangle(self.newImage, (x2, y2), (x1, y1), (0, 0, 255), 1)

        '''
        
        if x1 >= regionX1 and x2 <= regionX2 and y1 >= regionY1 and y2 <= regionY2:
            inRegion = True
            break
        else:
            inRegion = False
        if self.checkPoint(regionX1, regionY1, regionX2, regionY2, x, y):
            cv2.rectangle(self.newImage, (x2, y2), (x1, y1), (0, 255, 0), 2)
        else:
            cv2.rectangle(self.newImage, (x2, y2), (x1, y1), (0, 0, 255), 2)
        '''

        '''
        if x1 >= regionX1 and y1 >= regionY1:
            if x2 <= regionX2 and y2 <= regionY2:
                cv2.rectangle(self.newImage, (x2, y2), (x1, y1), (0, 255, 0), 2)
            else:
                cv2.rectangle(self.newImage, (x2, y2), (x1, y1), (0, 0, 255), 2)
        else:
            cv2.rectangle(self.newImage, (x2, y2), (x1, y1), (0, 0, 255), 2)
        '''
        cv2.imwrite('extractedRegion.jpg', self.newImage)

    def showRegions(self):
        self.newImage = self.cardTemplate
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


class nameTemplate:
    def __init__(self):
        self.value = None
        self.templateName = None
        self.subRoot = tk.Toplevel()
        self.subRoot.title("Template Name")

        tk.Label(self.subRoot, text='Template Name').pack()
        self.regionName = tk.Entry(self.subRoot)
        self.regionName.pack()

        self.nextButton = tk.Button(self.subRoot, text="Ok", width=15, command=self.saveInfo)
        self.nextButton.pack()

        self.subRoot.mainloop()

    def saveInfo(self):
        name = self.regionName.get()
        self.templateName = name
        self.subRoot.quit()
        self.subRoot.destroy()