from tkinter import *
from clientUDP import hostScan

def sendInput():
    pseudo = ipInLabel.get()
    hostScan(pseudo)

gui = Tk()
gui.geometry("330x330")
label = Label(gui, text="Pseudo ")
label.pack(side=TOP)
ipInLabel = StringVar()
input = Entry(gui, textvariable=ipInLabel)
input.pack()
ipInLabel.set("Z3PH7R")

scanButton = Button(gui, text="Rejoindre une partie", command=sendInput)
scanButton.config(width=20, height=2)
scanButton.pack()

gui.mainloop()