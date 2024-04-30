# PAS UTILISER CET APP
import tkinter as tk
from clientUDP import send_message, connexion, envoi_mes
import time

def afficher_page_suivante():
    # Cette fonction masque le contenu actuel et affiche la page suivante
    page1.pack_forget()  # Masquer le cadre actuel
    page2.pack()  # Afficher le cadre suivant

def retour():
    page2.pack_forget()
    page1.pack()
    
# def send_input():
#     pseudo = message.get()
#     send_message(pseudo)

def send_pseudo():
    # print(message.get())
    if len(message.get()) > 2:
        # print("Dans if send_pseudo")
        pseudo = message.get()
        if connexion(pseudo):
            afficher_page_suivante()

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
page1 = tk.Frame(gui)
page1.pack()

# Contenu du premier cadre
label_1 = tk.Label(page1, text="Page 1")
label_1.pack()

label_2 = tk.Label(page1, text="Pseudo")
label_2.pack()

message = tk.StringVar()
input = tk.Entry(page1, textvariable=message)
input.pack()

scan_button1 = tk.Button(page1, text="Connexion", command=lambda:[send_pseudo(), planifier_envoi_mes(), afficher_page_suivante()])
scan_button1.config(width=20, height=2)
scan_button1.pack()

scan_button2 = tk.Button(page1, text="Quitter", command=quitter)
scan_button2.config(width=20, height=2)
scan_button2.pack()


#-----------PAGE 2--------------
# Création du deuxième cadre (page)
page2 = tk.Frame(gui)
# Contenu du deuxième cadre (page)
label_2 = tk.Label(page2, text="Page 2")
# bouton_retour = tk.Button(page2, text="Déconnexion", command=lambda: page2.pack_forget() or page1.pack())  # Masquer le cadre suivant et afficher le cadre actuel
bouton_retour = tk.Button(page2, text="Déconnexion", command=retour)  # Masquer le cadre suivant et afficher le cadre actuel
label_2.pack()
bouton_retour.pack()

# Bouton pour passer à la page suivante
# bouton_suivant = tk.Button(page1, text="Page suivante", command=afficher_page_suivante)
# bouton_suivant.pack()


gui.mainloop()