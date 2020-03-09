from PIL import Image, ImageTk
import tkinter as tk
import PIL.Image
import PIL.ImageTk
import cv2
import re
from os import system


class labelCards:
    def __init__(self, window, window_title, filename, image, game):
        self.window = window
        self.game = game
        self.window.title(window_title)
        self.x = self.y = 0
        self.cropImage = image
        self.file = image
        self.canvas = tk.Canvas(self.window, width=400, height=400)

        self.regionFile = open(self.game + "/regions.txt", "a+")
        self.regionFile.write(filename + ' ')

        tk.Label(self.window, text='Step 3: Click and drag on the card to select region or symbol '
                                   '(Top left to bottom right)', fg='darkgreen').grid(row=0, column=1)
        self.canvas.grid(row=1, column=1, columnspan=4, rowspan=4)
        self.canvas.bind("<ButtonPress-1>", self.buttonPress)
        self.canvas.bind("<B1-Motion>", self.movePress)
        self.canvas.bind("<ButtonRelease-1>", self.buttonRelease)

        tk.Label(self.window, text='Step 1: Select what should be found in region', fg='blue').grid(row=0, column=0)
        self.var = tk.IntVar()
        self.text = 'Text'
        self.chk = tk.Checkbutton(self.window, text=self.text, variable=self.var)
        self.chk.grid(row=1, column=0)
        self.var1 = tk.IntVar()
        self.symbols = 'Symbols'
        self.chk1 = tk.Checkbutton(self.window, text=self.symbols, variable=self.var1)
        self.chk1.grid(row=2, column=0)
        self.var2 = tk.IntVar()
        self.color = 'Color'
        self.chk2 = tk.Checkbutton(self.window, text=self.color, variable=self.var2)
        self.chk2.grid(row=3, column=0)

        tk.Label(self.window, text='Step 2: Adding region or symbol?', fg='red').grid(row=4, column=0, sticky=tk.S)
        self.radioVar = tk.IntVar()
        self.symbolRadio = tk.Radiobutton(self.window, text="Add Symbol", variable=self.radioVar, value=1)
        self.symbolRadio.grid(row=5, column=0, sticky=tk.E)
        self.regionRadio = tk.Radiobutton(self.window, text="Add Region", variable=self.radioVar, value=2)
        self.regionRadio.grid(row=5, column=0, sticky=tk.W)

        self.nextButton = tk.Button(self.window, text="Next Card", width=10, command=self.nextCard)
        self.nextButton.grid(row=5, column=1, sticky=tk.E)

        self.rect = None
        self.regionName = None

        self.startX = None
        self.startY = None

        self.image = PIL.Image.open(self.file)
        self.tk_im = ImageTk.PhotoImage(self.image)
        self.canvas.create_image(0, 0, anchor="nw", image=self.tk_im)

        self.window.mainloop()

    def nextCard(self):
        self.regionFile.write('\n')
        self.regionFile.close()
        self.window.destroy()

    def buttonPress(self, event):
        # save mouse drag start position
        self.startX = self.canvas.canvasx(event.x)
        self.startY = self.canvas.canvasy(event.y)

        # create rectangle if not yet exist
        if not self.rect:
            self.rect = self.canvas.create_rectangle(self.x, self.y, 1, 1, outline='red')

    def movePress(self, event):
        currX = self.canvas.canvasx(event.x)
        currY = self.canvas.canvasy(event.y)

        # expand rectangle as you drag the mouse
        self.canvas.coords(self.rect, self.startX, self.startY, currX, currY)

    def buttonRelease(self, event):
        strName = ''
        if self.var.get():
            strName = strName + self.text
        if self.var1.get():
            strName = strName + self.symbols
        if self.var2.get():
            strName = strName + self.color

        strCoor = int(self.startX), int(self.startY), event.x, event.y
        x = int(strCoor[0])
        w = int(strCoor[2]) - int(strCoor[0])
        y = int(strCoor[1])
        h = int(strCoor[3]) - int(strCoor[1])
        strCoor = str(strCoor)
        strCoor = strCoor.replace(" ", "")

        img = cv2.imread(self.cropImage)
        cropImage = img[y:y + h, x:x + w]
        check = cv2.imwrite('cropped.jpg', cropImage)
        if check:
            if self.radioVar.get() == 1:
                croppedSymbolImage(self.game)
            elif self.radioVar.get() == 2:
                croppedRegionImage(self.regionFile, strCoor, strName)
            else:
                system('say -v Samantha Follow steps')
        else:
            system('say -v Samantha Draw rectangle from top left to bottom right')


class croppedRegionImage:
    def __init__(self, file, coordinates, nameSuffix):
        self.file = file
        self.coordinates = coordinates
        self.value = None
        self.nameSuffix = nameSuffix
        self.subRoot = tk.Toplevel()
        self.subRoot.title("Verify Region")

        self.showImage()

        tk.Label(self.subRoot, text='Region Name').pack()
        self.regionName = tk.Entry(self.subRoot)
        self.regionName.pack()

        self.nextButton = tk.Button(self.subRoot, text="Confirm", width=15, command=self.saveInfo)
        self.nextButton.pack()

        self.nextButton = tk.Button(self.subRoot, text="Try Again", width=15, command=self.retryRegion)
        self.nextButton.pack()

    def showImage(self):
        '''
        photo = Image.open('cardImage.jpg')
        render = ImageTk.PhotoImage(photo)
        label = tk.Label(self.subRoot, image=render)
        label.image = render
        label.pack()
        self.regionName.delete(0, tk.END)
        '''

        photo = Image.open('cropped.jpg')
        render = ImageTk.PhotoImage(photo)
        label = tk.Label(self.subRoot, image=render)
        label.image = render
        label.pack()

    def saveInfo(self):
        name = self.regionName.get()
        name = name + self.nameSuffix
        name = re.sub(" ", "", name)
        self.file.write(name + ':' + self.coordinates + ' ')
        self.subRoot.destroy()

    def retryRegion(self):
        self.subRoot.destroy()


class croppedSymbolImage:
    def __init__(self, game):
        self.value = None
        self.photo = None
        self.label = None
        self.render = None
        self.game = game
        self.subRoot = tk.Toplevel()
        self.subRoot.title("Verify Symbol")

        self.showImage()

        tk.Label(self.subRoot, text='Symbol Name').pack()
        self.symbolName = tk.Entry(self.subRoot)
        self.symbolName.pack()

        self.nextButton = tk.Button(self.subRoot, text="Confirm", width=15, command=self.saveInfo)
        self.nextButton.pack()

        self.nextButton = tk.Button(self.subRoot, text="Try Again", width=15, command=self.retryRegion)
        self.nextButton.pack()

    def showImage(self):

        self.photo = Image.open('cropped.jpg')
        self.render = ImageTk.PhotoImage(self.photo)
        self.label = tk.Label(self.subRoot, image=self.render)
        self.label.image = self.render
        self.label.pack()

    def saveInfo(self):
        image = cv2.imread('cropped.jpg')
        name = self.symbolName.get()
        path = self.game + '/cardSymbols/'
        # improve the quality of this image before saving
        cv2.imwrite(path + name + '.jpg', image)
        self.subRoot.destroy()

    def retryRegion(self):
        self.subRoot.destroy()

