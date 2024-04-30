import tkinter as tk
from clientUDP import send_message, connexion, envoi_mes
import time

class ApplicationClient:
    def __init__(self):
        self.gui = tk.Tk()
        self.gui.geometry("330x330")
        self.gui.title("Fenêtre principale")

        self.page1 = tk.Frame(self.gui)
        self.page1.pack()

        label_1 = tk.Label(self.page1, text="Page 1")
        label_1.pack()

        label_2 = tk.Label(self.page1, text="Pseudo")
        label_2.pack()

        self.message = tk.StringVar()
        input = tk.Entry(self.page1, textvariable=self.message)
        input.pack()

        scan_button1 = tk.Button(self.page1, text="Connexion", command=self.send_pseudo)
        scan_button1.config(width=20, height=2)
        scan_button1.pack()

        scan_button2 = tk.Button(self.page1, text="Quitter", command=self.quitter)
        scan_button2.config(width=20, height=2)
        scan_button2.pack()

        self.page2 = tk.Frame(self.gui)
        label_2 = tk.Label(self.page2, text="Page 2")
        bouton_retour = tk.Button(self.page2, text="Déconnexion", command=self.retour)
        label_2.pack()
        bouton_retour.pack()

        self.gui.mainloop()

    def afficher_page_suivante(self):
        self.page1.pack_forget()
        self.page2.pack()

    def retour(self):
        self.page2.pack_forget()
        self.page1.pack()

    def send_pseudo(self):
        if len(self.message.get()) > 2:
            pseudo = self.message.get()
            if connexion(pseudo) == "Joueur connecté":
                self.afficher_page_suivante()

    def quitter(self):
        self.gui.quit()

    def planifier_envoi_mes(self):
        envoi_mes()
        self.gui.after(10000, self.planifier_envoi_mes)

if __name__ == "__main__":
    app = ApplicationClient()




# def afficher_page_suivante():
#     # Cette fonction masque le contenu actuel et affiche la page suivante
#     page1.pack_forget()  # Masquer le cadre actuel
#     page2.pack()  # Afficher le cadre suivant

# def retour():
#     page2.pack_forget()
#     page1.pack()
    
# # def send_input():
# #     pseudo = message.get()
# #     send_message(pseudo)

# def send_pseudo():
#     # print(message.get())
#     if len(message.get()) > 2:
#         # print("Dans if send_pseudo")
#         pseudo = message.get()
#         if connexion(pseudo) == "Joueur connecté":
#             afficher_page_suivante()

# def actions_combinees():
#     send_pseudo()
#     # time.sleep(100)
#     afficher_page_suivante()
    
# # def envoi():
# #     envoi_mes()

# def quitter():
    
#     gui.quit()

# def planifier_envoi_mes():
#     # Planifie l'envoi du message au serveur toutes les 10 secondes
#     envoi_mes()
#     # Attendre 10 secondes avant d'envoyer le prochain message
#     gui.after(10000, planifier_envoi_mes)

# gui = tk.Tk()





# #-----------PAGE 2--------------
# # Création du deuxième cadre (page)
# page2 = tk.Frame(gui)
# # Contenu du deuxième cadre (page)
# label_2 = tk.Label(page2, text="Page 2")
# # bouton_retour = tk.Button(page2, text="Déconnexion", command=lambda: page2.pack_forget() or page1.pack())  # Masquer le cadre suivant et afficher le cadre actuel
# bouton_retour = tk.Button(page2, text="Déconnexion", command=retour)  # Masquer le cadre suivant et afficher le cadre actuel
# label_2.pack()
# bouton_retour.pack()

# # Bouton pour passer à la page suivante
# # bouton_suivant = tk.Button(page1, text="Page suivante", command=afficher_page_suivante)
# # bouton_suivant.pack()


# gui.mainloop()