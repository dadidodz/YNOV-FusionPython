# UTILISER CE CLIENT

import socket
from tkinter import *
from tkinter import messagebox
from tkinter.ttk import *
import json
import time
import re
# from morpion import Morpion

# SERVER_IP = '10.34.0.248'  # Adresse IP du serveur
# Port sur lequel le serveur écoute

class UDPClient:
    def __init__(self, server_ip=None, server_port=None):
        self.server_ip = server_ip
        self.server_port = server_port
        self.client_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.keep_alive_active = True
        self.keep_alive_id = None
        self.last_update_msg = time.time()
        self.last_update_partie = None
        self.pseudo_client = ""
        self.mmr = 1000
    
    def read_server_info_from_file(self, filename='config.txt'):
        try:
            with open(filename, 'r') as file:
                lines = file.readlines()
                for line in lines:
                    if "Adresse IP du serveur" in line:
                        self.server_ip = line.split(":")[-1].strip()
                    elif "Port du serveur" in line:
                        self.server_port = int(line.split(":")[-1].strip())
        except Exception as e:
            print(f"Erreur lors de la lecture du fichier de configuration : {e}")
    
    def connexion(self):
        if not self.verification_pseudo():
            try:
                request = ["connexion", self.pseudo.get(), self.mmr]
                request_json = json.dumps(request)

                self.client_socket.sendto(request_json.encode(), (self.server_ip, self.server_port))
                response, _ = self.client_socket.recvfrom(1024)
                
                print("Dans connexion, réponse du serveur :", response.decode())
                if response:
                    self.keep_alive_active = True
                    self.afficher_page_2()
                    self.stay_connected()
                    # self.update_chat()

            except Exception as e:
                print(f"Erreur lors de la connexion au serveur : {e}")
        else:
            self.entry_pseudo.delete(0, 'end')
            messagebox.showwarning("Erreur", "Le pseudo renseigné contient des caractères spéciaux ou n'est pas assez long.")
    
    def verification_pseudo(self):
        characters_interdis = r"[^\w\s]"
        if len(self.pseudo.get()) < 3 or re.search(characters_interdis, self.pseudo.get()):
            # self.pseudo_client = self.pseudo.get()
            return True
        else:
            return False
    
    def stay_connected(self):
        try:
            # Envoyer un message au serveur pour indiquer que le client est toujours actif
            request = ["alive"]
            request_json = json.dumps(request)
            
            self.client_socket.sendto(request_json.encode(), (self.server_ip, self.server_port))
            print("Message de présence envoyé au serveur.")
            response, _ = self.client_socket.recvfrom(1024)
            print("Dans stay_connected, réponse du serveur :", response.decode())
        except Exception as e:
            print(f"Erreur lors de l'envoi du message de présence : {e}")
        
        if self.keep_alive_active:
            # Planifier l'appel à la fonction toutes les 10 secondes
            self.keep_alive_id = self.root.after(10000, self.stay_connected)
    
    def stop_requesting(self):
        # Arrêter la planification des appels récurrents
        self.keep_alive_active = False
        # Annuler l'appel planifié
        if self.keep_alive_id:
            self.root.after_cancel(self.keep_alive_id)
            self.root.after_cancel(self.update_msg_id)
            self.root.after_cancel(self.partie_trouvee_id)
            self.keep_alive_id = None
    
    def send_msg(self):
        try:
            request = ["chat", self.message2.get()]
            request_json = json.dumps(request)

            self.client_socket.sendto(request_json.encode(), (self.server_ip, self.server_port))
            self.entry_msg.delete(0, 'end')

        except Exception as e:
            print(f"Erreur lors de la connexion au serveur : {e}")
    
    def update_chat(self):
        try:
            # Envoyer un message au serveur pour indiquer que le client est toujours actif
            request = ["upd_chat", self.last_update_msg]
            request_json = json.dumps(request)
            
            self.client_socket.sendto(request_json.encode(), (self.server_ip, self.server_port))
            response, _ = self.client_socket.recvfrom(1024)
            message_received = json.loads(response.decode())
            if response:
                if message_received[0] == "new_msg":
                    for msg in message_received[1]:
                        self.chat_display.configure(state=NORMAL)
                        if self.pseudo.get() == msg[0]:
                            txt = (f"{msg[0]} (You) : {msg[1]}\n")
                        else:
                            txt = (f"{msg[0]} : {msg[1]}\n")
                        self.chat_display.insert(END, txt)
                        self.chat_display.configure(state=DISABLED)
                        self.chat_display.see(END)  # Faire défiler vers le bas
                        self.last_update_msg = time.time()
                
                if message_received[0] == "ras":
                    pass

        except Exception as e:
            print(f"Erreur lors de la mise à jour du chat : {e}")
        
        if self.keep_alive_active:
            self.update_msg_id = self.root.after(1000, self.update_chat)
    
    def deconnexion(self):
        message = ["deconnexion", self.pseudo.get()]
        message_json = json.dumps(message)

        self.client_socket.sendto(message_json.encode(), (self.server_ip, self.server_port))
        response, _ = self.client_socket.recvfrom(1024)
        print("Dans connexion, réponse du serveur :", response.decode())
        if response:
            self.stop_requesting()
            self.afficher_page_1()
            # self.client_socket.close()
    
    def rejoindre_file_attente(self):
        try:
            request = ["recherche partie"]
            request_json = json.dumps(request)

            self.client_socket.sendto(request_json.encode(), (self.server_ip, self.server_port))
            response, _ = self.client_socket.recvfrom(1024)
            print("Dans rejoindre_file_attente, réponse du serveur :", response.decode())
            if response:
                self.partie_trouvee()

        except Exception as e:
            print(f"Erreur lors de la tentative d'entrée dans la file d'attente: {e}")
    
    def quitter_file_attente(self):
        try:
            self.root.after_cancel(self.partie_trouvee_id)
            request = ["quitter file attente"]
            request_json = json.dumps(request)

            self.client_socket.sendto(request_json.encode(), (self.server_ip, self.server_port))
            response, _ = self.client_socket.recvfrom(1024)
            if response:
                self.activer_btn_jouer()

        except Exception as e:
            print(f"Erreur lors de la tentative de retrait de la file d'attente: {e}")
    
    def partie_trouvee(self):
        try:
            print("Partie trouvée ?")
            # Envoyer un message au serveur pour indiquer que le client est toujours actif
            request = ["partie trouvee"]
            request_json = json.dumps(request)
            self.client_socket.sendto(request_json.encode(), (self.server_ip, self.server_port))

            response, _ = self.client_socket.recvfrom(1024)
            message_received = json.loads(response.decode())

            if message_received[0] == "Oui":
                print("Réponse serveur : Oui")
                self.afficher_page_3()
                self.last_update_partie = time.time()
                self.maj_partie()
                self.update_chat() #############
            else:
                print("Réponse serveur : Non")
                if self.keep_alive_active:
                    # Planifier l'appel à la fonction toutes les 10 secondes
                    self.partie_trouvee_id = self.root.after(1000, self.partie_trouvee)
        except Exception as e:
            print(f"Erreur lors de la demande: {e}")
        
    def play(self, row, col):
        try:
            print(f"Je peux jouer ici {row}, {col}")
            # Envoyer un message au serveur pour indiquer que le client est toujours actif
            request = ["jouer ici", row, col]
            request_json = json.dumps(request)
            self.client_socket.sendto(request_json.encode(), (self.server_ip, self.server_port))

        except Exception as e:
            print(f"Erreur lors de la demande pour jouer à cette case: {e}")
    
    def maj_partie(self):
        try:
            # Envoyer un message au serveur pour savoir si une action à été effectué dans la partie
            request = ["maj partie", self.last_update_partie]
            request_json = json.dumps(request)
            
            self.client_socket.sendto(request_json.encode(), (self.server_ip, self.server_port))
            response, _ = self.client_socket.recvfrom(1024)
            message_received = json.loads(response.decode())
            if response:
                if message_received[0] == "nouvelle action":
                    for actions in message_received[1]:
                        row, col, txt, etat_partie, gagnant = actions
                        self.buttons[row][col].config(text=txt)
                        if etat_partie:
                            if gagnant == None:
                                messagebox.showinfo("Fin de partie", "Match nul!")
                            else:
                                messagebox.showinfo("Fin de partie", f"Le joueur {gagnant} a gagné!")
                            
                            self.btn_rejouer.config(state="enabled")

                        self.last_update_partie = time.time()
                
                if message_received[0] == "zero nouvelle action":
                    pass

        except Exception as e:
            print(f"Erreur lors de la mise à jour de la partie : {e}")
        
        if self.keep_alive_active:
            self.maj_partie_id = self.root.after(1000, self.maj_partie)
        

    
    
    ######## Méthodes avec actions sur la fenetre tkinter
    def on_validate(self, P):
        # Limiter à 10 caractères
        return len(P) <= 10

    def afficher_page_1(self):
        self.page2.pack_forget()
        self.page1.pack()
        self.root.geometry("400x200")

    def afficher_page_2(self):
        self.page1.pack_forget()
        self.page2.pack()
        self.root.geometry("400x300")
    
    def retour_page_2(self):
        self.page3.pack_forget()
        self.page2.pack()
        self.root.geometry("400x300")
    
    def afficher_page_3(self):
        self.page2.pack_forget()
        self.page3.pack()
        self.root.geometry("600x600")
    
    def modif_pseudo(self):
        self.pseudo_client = self.pseudo.get()
        self.label_pseudo.config(text=f"Connecté en tant que : {self.pseudo_client}")
    
    def desactiver_btn_jouer(self):
        self.btn_jouer.config(state="disabled")
        self.btn_cancel_jouer.config(state="enabled")
    
    def activer_btn_jouer(self):
        self.btn_cancel_jouer.config(state="disabled")
        self.btn_jouer.config(state="enable")

    def run(self):
        self.read_server_info_from_file()
        self.root = Tk()
        self.root.geometry("400x200")
        self.root.title("Client UDP")

        # Création des pages
        self.page1 = Frame(self.root)
        self.page2 = Frame(self.root)
        self.page3 = Frame(self.root)
        self.page1.pack()


        # -------------- PAGE 1 --------------------
        # Création variable
        self.pseudo = StringVar()

        #--------------------Création des Styles--------------------#
        #----------Boutons----------#
        # Créé un style appliqué automatiquement aux boutons grâce au nom "TButton"
        buttons_style = Style()
        buttons_style.configure("TButton",
                                foreground="black",  # Couleur du texte
                                font=("Arial", 10),  # Police et taille de caractères
                                bordercolor="black",  # Couleur de la bordure
                                padding=3,  # Espace entre le contenu et la bordure
                                width=20,  # Largeur du bouton
                                height=5,  # Hauteur du bouton
                                anchor="center",  # Alignement du contenu
                                justify="center"  # Alignement horizontal du texte
                                )
        
        btn_case_morpion = Style()
        btn_case_morpion.configure("Case.TButton",
                                    foreground="black",  # Couleur du texte
                                    font=("Arial", 10),  # Police et taille de caractères
                                    bordercolor="black",  # Couleur de la bordure
                                    paddingy=20,  # Espace entre le contenu et la bordure
                                    width=10,  # Largeur du bouton
                                    height=50,  # Hauteur du bouton
                                    anchor="center",  # Alignement du contenu
                                    justify="center"  # Alignement horizontal du texte
                                    )
        
        #----------Création et config widgets
        self.entry_pseudo = Entry(self.page1, textvariable=self.pseudo)

        btn_connexion = Button(self.page1, text="Se connecter", command=lambda:[self.modif_pseudo(), self.connexion()])
        # btn_connexion.config(width=20, height=2)

        btn_quitter = Button(self.page1, text="Quitter", command=lambda: self.root.destroy())
        # btn_quitter.config(width=20, height=2)

        #----------Pack widget
        Label(self.page1, text="Page 1").pack()
        Label(self.page1, text="Pseudo").pack()
        self.entry_pseudo.pack()
        btn_connexion.pack()
        btn_quitter.pack()


        #-----------PAGE 2--------------
        # Création variable
        

        #----------Création et config widgets
        self.btn_jouer = Button(self.page2, text="Trouver une partie", command=lambda:[self.rejoindre_file_attente(), self.desactiver_btn_jouer()])
        self.btn_cancel_jouer = Button(self.page2, text="Quitter la file d'attente", state="disabled", command=lambda:[self.quitter_file_attente()])
        self.btn_retour = Button(self.page2, text="Déconnexion", command=lambda:[self.deconnexion()])
        
        #----------Pack widget
        Label(self.page2, text="Page 2").pack()
        self.label_pseudo = Label(self.page2, text="")
        self.label_pseudo.pack()
        self.btn_jouer.pack()
        self.btn_cancel_jouer.pack()
        self.btn_retour.pack()


        #-----------PAGE 3--------------
        # Création variable
        self.message2 = StringVar()

        #----------Création et config widgets
        self.chat_display = Text(self.page3, height=8, width=25, state=DISABLED)
        self.validate_cmd = self.page3.register(self.on_validate)
        self.entry_msg = Entry(self.page3, textvariable=self.message2, validate="key", validatecommand=(self.validate_cmd, "%P"))
        self.btn_envoyer = Button(self.page3, text="Envoyer", command=lambda:[self.send_msg()])
        self.btn_retour = Button(self.page3, text="Retour", command=lambda:[]) #self.retour_page_2()
        self.btn_rejouer = Button(self.page3, text="Rejouer", state="disabled", command=lambda:[])

        #----------Pack widget
        self.chat_display.grid(row=3, column=0, columnspan=3, sticky="ew")
        self.entry_msg.grid(row=4, column=0, columnspan=2, sticky="ew")
        self.btn_envoyer.grid(row=4, column=2, sticky="ew")
        self.btn_retour.grid(row=5, column=0, sticky="w")
        self.btn_rejouer.grid(row=5, column=1, sticky="w")



        self.current_player = "X"
        self.board = [[" " for _ in range(3)] for _ in range(3)]

        self.buttons = [[None for _ in range(3)] for _ in range(3)]

        for i in range(3):
            for j in range(3):
                button = Button(self.page3, text="", style="Case.TButton", command=lambda row=i, col=j: self.play(row, col))
                button.grid(row=i, column=j, ipady=10, ipadx=10)
                self.buttons[i][j] = button


        self.root.mainloop()

udp_client = UDPClient()
udp_client.run()
