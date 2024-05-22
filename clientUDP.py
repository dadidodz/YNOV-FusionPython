# UTILISER CE CLIENT

import socket
from tkinter import *
from tkinter import messagebox
from tkinter.ttk import *
import json
import time
import re
# from morpion import Morpion

# SERVER_IP = '10.34.0.248'  # Adresse IP du serveur #192.168.1.45
# Port sur lequel le serveur écoute

class UDPClient:
    def __init__(self, server_ip=None, server_port=None):
        self.server_ip = server_ip
        self.server_port = server_port
        self.client_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

        self.keep_alive_active = True
        self.keep_alive_id = None

        self.keep_partie_trouvee_active = False
        self.keep_partie_trouvee_id = None

        self.keep_update_chat_active = False
        self.keep_update_chat_id = None

        self.keep_maj_partie_active = False
        self.keep_maj_partie_id = None

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

            except Exception as e:
                print(f"Erreur lors de la connexion au serveur : {e}")
        else:
            self.entry_pseudo.delete(0, 'end')
            messagebox.showwarning("Erreur", "Le pseudo renseigné contient des caractères spéciaux ou n'est pas assez long.")
    
    def verification_pseudo(self):
        characters_interdis = r"[^\w\s]"
        if len(self.pseudo.get()) < 3 or re.search(characters_interdis, self.pseudo.get()):
            return True
        else:
            return False
    
    def stay_connected(self):
        try:
            # Envoyer un message au serveur pour indiquer que le client est toujours actif
            request = ["alive"]
            request_json = json.dumps(request)
            
            self.client_socket.sendto(request_json.encode(), (self.server_ip, self.server_port))
            print("Message anti-afk envoyé")
            response, _ = self.client_socket.recvfrom(1024)
            print("Réponse serveur :", response.decode())
        except Exception as e:
            print(f"Erreur lors de l'envoi du message de présence : {e}")
        
        if self.keep_alive_active:
            self.keep_alive_id = self.root.after(10000, self.stay_connected)
    
    def rejoindre_file_attente(self):
        try:
            request = ["recherche partie"]
            request_json = json.dumps(request)

            self.client_socket.sendto(request_json.encode(), (self.server_ip, self.server_port))
            response, _ = self.client_socket.recvfrom(1024)
            print("Dans rejoindre_file_attente, réponse du serveur :", response.decode())
            if response:
                self.keep_partie_trouvee_active = True
                self.partie_trouvee()

        except Exception as e:
            print(f"Erreur lors de la tentative d'entrée dans la file d'attente: {e}")
    
    def quitter_file_attente(self):
        try:
            self.keep_partie_trouvee_active = False
            self.root.after_cancel(self.keep_partie_trouvee_id)
            request = ["quitter file attente"]
            request_json = json.dumps(request)

            self.client_socket.sendto(request_json.encode(), (self.server_ip, self.server_port))
            response, _ = self.client_socket.recvfrom(1024)
            if response:
                # self.keep_partie_trouvee_active = False
                # self.root.after_cancel(self.keep_partie_trouvee_id)
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
                self.activer_btn_jouer()
                self.afficher_page_3()
                self.last_update_partie = time.time()

                self.keep_maj_partie_active = True
                self.maj_partie()

                self.keep_update_chat_active = True
                self.update_chat()

                self.keep_partie_trouvee_active = False
            else:
                print("Réponse serveur : Non")
                if self.keep_partie_trouvee_active:
                    self.keep_partie_trouvee_id = self.root.after(1000, self.partie_trouvee)

        except Exception as e:
            print(f"Erreur lors de la demande: {e}")
    
    def maj_partie(self):
        try:
            # Envoyer un message au serveur pour savoir si une action à été effectué dans la partie
            request = ["maj partie", self.last_update_partie]
            request_json = json.dumps(request)
            
            self.client_socket.sendto(request_json.encode(), (self.server_ip, self.server_port))
            response, _ = self.client_socket.recvfrom(1024)
            message_received = json.loads(response.decode())
            if response:
                if message_received[0] == "partie_lost":
                    self.quitter()
                if message_received[0] == "nouvelle action":
                    for actions in message_received[1]:
                        row, col, txt, etat_partie, gagnant, perdant = actions
                        self.buttons[row][col].config(text=txt)
                        if etat_partie:
                            if gagnant == None:
                                messagebox.showinfo("Fin de partie", "Match nul!")
                            else:
                                if gagnant == self.pseudo_client:
                                    text = f"Le joueur {gagnant} a gagné!\nVous avez gagné!"
                                else:
                                    text = f"Le joueur {gagnant} a gagné!\nVous avez perdu!"
                                messagebox.showinfo("Fin de partie", text)
                            
                            # self.keep_maj_partie_active = False
                        self.last_update_partie = time.time()
                
                if message_received[0] == "zero nouvelle action":
                    pass

        except Exception as e:
            print(f"Erreur lors de la mise à jour de la partie : {e}")
        
        if self.keep_maj_partie_active:
            self.keep_maj_partie_id = self.root.after(1000, self.maj_partie)
    
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
                            txt = (f"{msg[0]} (Vous) : {msg[1]}\n")
                        else:
                            txt = (f"{msg[0]} : {msg[1]}\n")
                        start_index = f"{END}-{len(txt)+1}c"
                        self.chat_display.insert(END, txt)
                        self.chat_display.tag_configure('default', foreground='black', font=('Helvetica', 10))
                        self.chat_display.tag_add('default', start_index, END)
                        self.chat_display.configure(state=DISABLED)
                        self.chat_display.see(END)  # Faire défiler vers le bas
                        self.last_update_msg = time.time()
                
                if message_received[0] == "ras":
                    pass

        except Exception as e:
            print(f"Erreur lors de la mise à jour du chat : {e}")
        if self.keep_update_chat_active:
            self.keep_update_chat_id = self.root.after(1000, self.update_chat)
    
    def send_msg(self):
        if not self.verification_msg():
            try:
                request = ["chat", self.message2.get()]
                request_json = json.dumps(request)

                self.client_socket.sendto(request_json.encode(), (self.server_ip, self.server_port))
                self.entry_msg.delete(0, 'end')

            except Exception as e:
                print(f"Erreur lors de la connexion au serveur : {e}")
        else:
            messagebox.showwarning("Erreur", "Le message contient des caractères interdits.")
    
    def verification_msg(self):
        characters_interdis = r"[:\\;{}]"
        if re.search(characters_interdis, self.message2.get()):
            return True
        else:
            return False
    
    def play(self, row, col):
        try:
            print(f"Je peux jouer ici {row}, {col}")
            # Envoyer un message au serveur pour indiquer que le client est toujours actif
            request = ["jouer ici", row, col]
            request_json = json.dumps(request)
            self.client_socket.sendto(request_json.encode(), (self.server_ip, self.server_port))

        except Exception as e:
            print(f"Erreur lors de la demande pour jouer à cette case: {e}")
        
    def quitter(self):
        self.keep_maj_partie_active = False
        self.root.after_cancel(self.keep_maj_partie_id)

        self.keep_update_chat_active = False
        self.root.after_cancel(self.keep_update_chat_id)

        self.retour_page_2()   
               
    def quitter_partie(self):
        try :
            # self.keep_maj_partie_active = False
            # self.root.after_cancel(self.keep_maj_partie_id)

            # self.keep_update_chat_active = False
            # self.root.after_cancel(self.keep_update_chat_id)

            message = ["quitter partie"]
            message_json = json.dumps(message)

            self.client_socket.sendto(message_json.encode(), (self.server_ip, self.server_port))
            response, _ = self.client_socket.recvfrom(1024)
            if response :
                self.keep_maj_partie_active = False
                self.root.after_cancel(self.keep_maj_partie_id)

                self.keep_update_chat_active = False
                self.root.after_cancel(self.keep_update_chat_id)
                print("Client quitte la partie", response.decode())
                self.retour_page_2()
                
        except Exception as e:
            print(f"Erreur lors de la tentative de quitter la partie : {e}")
    
    def deconnexion(self):
        try :
            message = ["deconnexion", self.pseudo.get()]
            message_json = json.dumps(message)

            self.client_socket.sendto(message_json.encode(), (self.server_ip, self.server_port))
            response, _ = self.client_socket.recvfrom(1024)
            print("Dans connexion, réponse du serveur :", response.decode())
            if response:
                self.keep_alive_active = False
                self.root.after_cancel(self.keep_alive_id)
                self.keep_partie_trouvee_active = False

                if self.keep_partie_trouvee_id:
                    self.root.after_cancel(self.keep_partie_trouvee_id)
                
                # self.stop_requesting()
                self.retour_page_1()
        
        except Exception as e:
            print(f"Erreur lors de la tentative de déconnexion : {e}")

    ######## Méthodes avec actions sur la fenetre tkinter
    def on_validate(self, P):
        return len(P) <= 25

    def retour_page_1(self):
        self.activer_btn_jouer()
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
        for i in range(3):
            for j in range(3):
                self.buttons[i][j].config(text="")
        
        self.chat_display.configure(state=NORMAL)
        self.chat_display.delete(1.0, END)
        self.chat_display.configure(state=DISABLED)
    
    def afficher_page_3(self):
        self.page2.pack_forget()
        self.page3.pack()
        self.root.geometry("600x600")
        self.initialiser_chat()
    
    def initialiser_chat(self):
        self.chat_display.configure(state=NORMAL)
        txt = "Espace chat, veuillez rester respectueux envers votre adversaire sous peine de sanction\n"
        self.chat_display.insert(END, txt)
        start_index = f"{END}-{len(txt)+1}c"
        self.chat_display.tag_configure('gris_italique', foreground='grey', font=('Helvetica', 10, 'italic'))
        self.chat_display.tag_add('gris_italique', start_index, END)
        
        self.chat_display.configure(state=DISABLED)
    
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
        self.btn_deconnexion = Button(self.page2, text="Déconnexion", command=lambda:[self.deconnexion()])
        
        #----------Pack widget
        Label(self.page2, text="Page 2").pack()
        self.label_pseudo = Label(self.page2, text="")
        self.label_pseudo.pack()
        self.btn_jouer.pack()
        self.btn_cancel_jouer.pack()
        self.btn_deconnexion.pack()


        #-----------PAGE 3--------------
        # Création variable
        self.message2 = StringVar()

        #----------Création et config widgets
        self.chat_display = Text(self.page3, height=8, width=25, state=DISABLED)
        self.validate_cmd = self.page3.register(self.on_validate)
        self.entry_msg = Entry(self.page3, textvariable=self.message2, validate="key", validatecommand=(self.validate_cmd, "%P"))
        self.btn_envoyer = Button(self.page3, text="Envoyer", command=lambda:[self.send_msg()])
        self.btn_quitter_partie = Button(self.page3, text="Quitter la partie", command=self.quitter_partie) #self.retour_page_2()
        # self.btn_rejouer = Button(self.page3, text="Rejouer", state="disabled", command=lambda:[])

        #----------Grid widget
        Label(self.page3, text="Page 3").grid(row=0, column=1)
        # self.label_pseudo = Label(self.page2, text="")
        # self.label_pseudo.pack()

        self.chat_display.grid(row=4, column=0, columnspan=3, sticky="ew")
        Label(self.page3, text="Connecté").grid(row=5, column=0, columnspan=3, sticky="ew")
        self.entry_msg.grid(row=6, column=0, columnspan=2, sticky="ew")
        self.btn_envoyer.grid(row=6, column=2, sticky="ew")
        self.btn_quitter_partie.grid(row=7, column=0, sticky="w")
        # self.btn_rejouer.grid(row=5, column=1, sticky="w")



        self.current_player = "X"
        self.board = [[" " for _ in range(3)] for _ in range(3)]

        self.buttons = [[None for _ in range(3)] for _ in range(3)]

        for i in range(3):
            for j in range(3):
                button = Button(self.page3, text="", style="Case.TButton", command=lambda row=i, col=j: self.play(row, col))
                button.grid(row=i+1, column=j, ipady=10, ipadx=10)
                self.buttons[i][j] = button


        self.root.mainloop()

udp_client = UDPClient()
udp_client.run()
