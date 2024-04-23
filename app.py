from tkinter import *
from clientUDP import send_message, connexion

def send_input():
    pseudo = message.get()
    send_message(pseudo)

def send_pseudo():
    pseudo = message.get()
    connexion(pseudo)

gui = Tk()
gui.geometry("330x330")

label = Label(gui, text="Pseudo")
label.pack(side=TOP)

message = StringVar()
input = Entry(gui, textvariable=message)
input.pack()
# ipInLabel.set("Z3PH7R")

# scanButton = Button(gui, text="Rejoindre une partie", command=send_input)
# scanButton.config(width=20, height=2)
# scanButton.pack()

scanButton = Button(gui, text="Connexion", command=send_pseudo)
scanButton.config(width=20, height=2)
scanButton.pack()

gui.mainloop()