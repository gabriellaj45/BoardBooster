import os
import tkinter as tk
from PIL import ImageTk, Image


class selectTemplate:
    def __init__(self, window, window_title, cardFile):
        self.window = window
        self.window.title(window_title)
        self.cardFile = cardFile

        # Create a canvas that can fit the above video source size
        self.L = tk.Listbox(selectmode=tk.SINGLE)
        self.L.pack()

        self.selectButton = tk.Button(window, text="Select", width=15, command=self.getFileName)
        self.selectButton.pack(side=tk.TOP)

        self.doneButton = tk.Button(window, text="Done", width=15, command=window.destroy)
        self.doneButton.pack(side=tk.TOP)

        img = ImageTk.PhotoImage(Image.open(self.cardFile))
        self.panel = tk.Label(window, compound=tk.BOTTOM, text='Card', image=img)
        self.panel.pack(side=tk.LEFT)

        self.image = tk.Label(window, compound=tk.BOTTOM, text='Template for Card')
        self.image.pack(side=tk.RIGHT)

        self.imageName = ''

        self.L.bind('<ButtonRelease-1>', self.list_entry_clicked)

        # After it is called once, the update method will be automatically called every delay milliseconds
        self.delay = 15
        self.fileDict = {}
        self.update()

        self.window.mainloop()

    def update(self):
        dirpath = 'cardTemplates/'
        for fileName in os.listdir(dirpath):
            if not fileName[0].isdigit():
                continue
            filePath = os.path.join(dirpath, fileName)
            file = ImageTk.PhotoImage(Image.open(filePath))
            self.fileDict[fileName] = file
            self.L.insert(tk.END, fileName)

    def getFileName(self):
        return self.imageName

    def setFileName(self, image):
        self.imageName = image

    def list_entry_clicked(self, *ignore):
        self.imageName = self.L.get(self.L.curselection()[0])
        self.image.config(image=self.fileDict[self.imageName])
        self.setFileName(self.imageName)
        return self.imageName
