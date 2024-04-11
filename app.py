from tkinter import *
import tkinter
from clientUDP import hostScan

gui = Tk()
gui.geometry("330x330")
label = Label(gui, text="Pseudo ")

label.pack(side=TOP)

ipInLabel = StringVar()  ## sert à définir l'ip dans le label

input = Entry(gui, textvariable=ipInLabel)  ## sert à donner une zone de texte qui contient notre ip

input.pack()  ## permet d'organiser les widgets
ipInLabel.set("Z3PH7R") ## définit une variable par default




scanButton = tkinter.Button(gui, text ="Rejoindre une partie", command=hostScan) ## permet de lancer la commande scan quand on lance le label
scanButton.config(width=20, height=2)
 
scanButton.pack()

gui.mainloop()

