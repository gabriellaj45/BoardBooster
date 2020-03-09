import tkinter as tk
from labelCards import *
from playsound import playsound


class addNewSymbol:
    def __init__(self, game, file):
        playsound('labelGenSoundAlert.mp3')
        self.game = game
        self.file = file
        self.subRoot = tk.Toplevel()
        self.subRoot.title("New Symbol Found")

        # Create a canvas that can fit the above video source size
        self.canvas = tk.Canvas(self.subRoot, width=600, height=600)
        system('say -v Samantha New symbol found')
        tk.Label(self.subRoot, text='New symbol found. Would you like to add the new symbol?').pack()

        self.img = ImageTk.PhotoImage(Image.open('findSymbols.jpg'))
        self.panel = tk.Label(self.subRoot, image=self.img)
        self.panel.pack()

        self.yesButton = tk.Button(self.subRoot, text="Yes", width=15, command=self.yesSymbol)
        self.yesButton.pack()

        self.noButton = tk.Button(self.subRoot, text="No", width=15, command=self.noNewSymbol)
        self.noButton.pack()

        self.subRoot.mainloop()

    def noNewSymbol(self):
        self.subRoot.quit()
        self.subRoot.destroy()

    def yesSymbol(self):
        self.subRoot.quit()
        self.subRoot.destroy()
        labelCards(tk.Toplevel(), "Label Cards", self.file, self.file, self.game)

