import tkinter as tk
from clientUDP import send_message, connexion, envoi_mes
import time

def afficher_page_suivante():
    # Cette fonction masque le contenu actuel et affiche la page suivante
    cadre_actuel.pack_forget()  # Masquer le cadre actuel
    cadre_suivant.pack()  # Afficher le cadre suivant

# def send_input():
#     pseudo = message.get()
#     send_message(pseudo)

def send_pseudo():
    # print(message.get())
    if len(message.get()) > 2:
        print("Dans if send_pseudo")
        pseudo = message.get()
        connexion(pseudo)

def actions_combinees():
    send_pseudo()
    # time.sleep(100)
    afficher_page_suivante()
    

# def envoi():
#     envoi_mes()


def quitter():
    
    gui.quit()

def planifier_envoi_mes():
    # Planifie l'envoi du message au serveur toutes les 10 secondes
    envoi_mes()
    # Attendre 10 secondes avant d'envoyer le prochain message
    gui.after(10000, planifier_envoi_mes)

gui = tk.Tk()
gui.geometry("330x330")
gui.title("Fenêtre principale")

# -------------- PAGE 1 --------------------
# Création du premier cadre (page)
cadre_actuel = tk.Frame(gui)
cadre_actuel.pack()

# Contenu du premier cadre
label_1 = tk.Label(cadre_actuel, text="Page 1")
label_1.pack()

label_2 = tk.Label(cadre_actuel, text="Pseudo")
label_2.pack()

message = tk.StringVar()
input = tk.Entry(cadre_actuel, textvariable=message)
input.pack()

scan_button1 = tk.Button(cadre_actuel, text="Connexion", command=lambda:[send_pseudo(), afficher_page_suivante()])
scan_button1.config(width=20, height=2)
scan_button1.pack()

scan_button2 = tk.Button(cadre_actuel, text="Quitter", command=quitter)
scan_button2.config(width=20, height=2)
scan_button2.pack()


#-----------PAGE 2--------------
# Création du deuxième cadre (page)
cadre_suivant = tk.Frame(gui)
# Contenu du deuxième cadre (page)
label_2 = tk.Label(cadre_suivant, text="Page 2")
bouton_retour = tk.Button(cadre_suivant, text="Retour", command=lambda: cadre_suivant.pack_forget() or cadre_actuel.pack())  # Masquer le cadre suivant et afficher le cadre actuel
label_2.pack()
bouton_retour.pack()

# Bouton pour passer à la page suivante
bouton_suivant = tk.Button(cadre_actuel, text="Page suivante", command=afficher_page_suivante)
bouton_suivant.pack()



# while True:


planifier_envoi_mes()

gui.mainloop()
# envoi_mes()
#Attendre 10 secondes avant d'envoyer le prochain message




# Lancement de la boucle principale








# # ipInLabel.set("Z3PH7R")

# # scanButton = Button(gui, text="Rejoindre une partie", command=send_input)
# # scanButton.config(width=20, height=2)
# # scanButton.pack()






# gui.mainloop()











