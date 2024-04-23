from tkinter import *
from clientUDP import send_message

def send_input():
    pseudo = message.get()
    send_message(pseudo)

gui = Tk()
gui.geometry("330x330")

label = Label(gui, text="Pseudo ")
label.pack(side=TOP)

message = StringVar()
input = Entry(gui, textvariable=message)
input.pack()
# ipInLabel.set("Z3PH7R")

scanButton = Button(gui, text="Rejoindre une partie", command=send_input)
scanButton.config(width=20, height=2)
scanButton.pack()

gui.mainloop()