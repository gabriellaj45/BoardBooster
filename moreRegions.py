import tkinter as tk


class moreRegions:
    def __init__(self, window, window_title):
        self.window = window
        self.window.title(window_title)

        # Create a canvas that can fit the above video source size
        self.canvas = tk.Canvas(window, width=200, height=20)

        self.noButton = tk.Button(window, text="No", width=15, command=self.saidNo)
        self.noButton.pack(side=tk.LEFT)

        self.yesButton = tk.Button(window, text="Yes", width=15, command=self.saidYes)
        self.yesButton.pack(side=tk.RIGHT)

        self.canvas.pack()

        self.window.mainloop()

    def saidYes(self):
        self.text = 'yes'
        self.window.destroy()

    def saidNo(self):
        self.text = 'no'
        self.window.destroy()


