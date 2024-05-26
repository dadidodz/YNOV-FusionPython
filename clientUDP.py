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

class UDPClient: # initialiser toutes les attributs de l'object udp client
    def __init__(self, server_ip=None, server_port=None): # permet d'avoir un serveur dynamique : on peut changer l'adresse ip et le port du serveur dans le fichier.txt
        self.server_ip = server_ip
        self.server_port = server_port
        self.client_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM) # spécification du protocole de communication

        self.keep_alive_active = True # Condition pour dire : continuetons à envoyer des messages au serveur pour dire que le client est toujours actif
        self.keep_alive_id = None # permet d'IDENTIFIER l'id de l'appel et plus tard d'annuler L'ACTION DE L'ENVOI DE MESSAGE AU SERVEUR

        self.keep_game_search_active = False # 
        self.keep_game_search_id = None # permet de cancel L'ACTION DE L'ENVOI DE MESSAGE AU SERVEUR

        self.keep_update_chat_active = False 
        self.keep_update_chat_id = None # PERMET DE d'identifier  L'ACTION UPDATE CHAT pour modifier cette action plus tard

        self.keep_update_game_active = False # met a jour les actions de la partie
        self.keep_update_game_id = None 

        self.keep_get_full_board_active = False
        self.keep_get_full_board_id = None

        self.last_update_msg = time.time() # permet de savoir le dernier message envoyé
        self.last_update_partie = None # permet de savoir la dernière action de la partie

        self.pseudo_client = ""
        self.currentPlayer = "" # permet de savoir qui doit jouer
        
    
    def read_server_info_from_file(self, filename='config.txt'): # modifier dynamiquement l'ip du serveur et le port du fichier config.txt
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
    
    def connection(self): # permet de se connecter au serveur 
        if not self.check_pseudo():
            try: 
                message = ["connection", self.pseudo.get()] # stock les informations sous forme de message : connexion + pseudo
                message_json = json.dumps(message) # transformer en json pour l'envoyer au serveur

                self.client_socket.sendto(message_json.encode(), (self.server_ip, self.server_port)) # envoie le message au serveur
                response, _ = self.client_socket.recvfrom(1024) # attendre la réponse du serveur
                response_decoded = json.loads(response.decode())

                print("Dans connection, réponse serveur :", response.decode()) # afficher la réponse du serveur
                if response_decoded[0] == "already_connected":
                    self.entry_pseudo.delete(0, 'end') # supprimer le pseudo dans l'entrée utilisateur
                    messagebox.showwarning("Erreur", "Vous êtes déjà connecté depuis un autre poste.")
                else: # si la réponse est vrai afficher la page 2
                    self.keep_alive_active =  True # permet continuer l'appel a stayconnected
                    self.show_page_2() 
                    self.stay_connected() # permet de rester connecté

            except Exception as e: # gere exeception si le client n'arrive pas à se connecter
                print(f"Erreur lors de la connexion au serveur : {e}")
        else: # si le pseudo n'est pas valide afficher un message d'erreur
            self.entry_pseudo.delete(0, 'end') # supprimer le pseudo dans l'entrée utilisateur
            messagebox.showwarning("Erreur", "Le pseudo renseigné contient des caractères spéciaux ou n'est pas assez long.")
    
    def check_pseudo(self): # permet de checker si pseudo valide
        forbidden_characters = r"[^\w\s]"
        if len(self.pseudo.get()) < 3 or re.search(forbidden_characters, self.pseudo.get()):
            return True
        else:
            return False
    
    def stay_connected(self):
        try:
            # Envoyer un message au serveur pour indiquer que le client est toujours actif
            message = ["alive"]
            message_json = json.dumps(message) # transformer en json pour l'envoyer au serveur
            
            self.client_socket.sendto(message_json.encode(), (self.server_ip, self.server_port)) # envoie le message au serveur
            print("Envoi du message anti-afk")
            response, _ = self.client_socket.recvfrom(1024)
            print("Réponse serveur :", response.decode()) # afficher dans terminal
        except Exception as e:
            print(f"Erreur lors de l'envoi du message de présence : {e}")
        
        if self.keep_alive_active:
            self.keep_alive_id = self.root.after(10000, self.stay_connected) # permet de maintenir la connexion au serveur
            
            
    def join_queue(self): # permet de rejoindre la file d'attente
        try:
            message = ["recherche partie"] # message pour rejoindre la file d'attente
            message_json = json.dumps(message) 

            self.client_socket.sendto(message_json.encode(), (self.server_ip, self.server_port))
            response, _ = self.client_socket.recvfrom(1024)
            print("Dans join_queue, réponse du serveur :", response.decode()) # afficher la réponse du serveur
            
            
            # Vue que le client n'écoute pas en permanence le serveur, il doit envoyer un message pour savoir si la partie a été trouvée
            if response: # si le serveur répond au client
                self.keep_game_search_active = True  # maintenir la recherche de partie active
                self.game_search() # permet de chercher une partie 

        except Exception as e:
            print(f"Erreur lors de la tentative d'entrée dans la file d'attente: {e}")
    
    def quit_queue(self): # permet de quitter la file d'attente quand on clique sur le bouton quitter la file d'attente
        try:
            message = ["quitter file attente"]  # message pour quitter la file d'attente
            message_json = json.dumps(message) # transformer en json pour l'envoyer au serveur
            print(f"Tentative de retrait de la file d'attente") # afficher dans le terminal
            self.client_socket.sendto(message_json.encode(), (self.server_ip, self.server_port)) # envoie le message au serveur
            response, _ = self.client_socket.recvfrom(1024) # reponse du serveur 
            if response: # si le serveur répond au client
                print("Dans quit_queue, reponse serveur : ", response.decode()) # afficher la réponse du serveur
                self.keep_game_search_active = False # DESACTIVER LA RECHERCHE DE PARTIE
                self.root.after_cancel(self.keep_game_search_id) # ARRETER LE PROCESSUS DE RECHERCHE DE PARTIE
                self.enable_btn_find_game() # activer le bouton pour trouver une partie

        except Exception as e:
            print(f"Erreur lors de la tentative de retrait de la file d'attente: {e}")
    
    def game_search(self):
        try:
            print("Partie trouvée ?")
            # Envoyer un message au serveur pour indiquer que le client est toujours actif
            message = ["partie trouvee"]
            message_json = json.dumps(message)
            self.client_socket.sendto(message_json.encode(), (self.server_ip, self.server_port))

            response, _ = self.client_socket.recvfrom(1024)
            response_decoded = json.loads(response.decode()) # permet de decoder le message reçu DU SERVEUR EST STOCKÉ DANS UNE VARIABLE

            if response_decoded[0] == "Oui": # si le message reçu est "oui"
                print("Réponse serveur : Oui") 
                self.player_symbol.config(text=f"Connecté en tant que : {self.pseudo_client}, Symbole : {response_decoded[2]}") # permet de savoir le symbole du joueur
                self.enable_btn_find_game()
                self.show_page_3() # afficher la partie de manière graphique
                self.last_update_partie = time.time() # quand a t'on maj la partie la dernière fois
                self.currentPlayer = response_decoded[1] # permet de savoir qui doit jouer
                self.update_current_player() # permet de mettre à jour le joueur qui doit jouer
                self.keep_update_game_active = True # permet de maintenir la mise à jour de la partie active
                self.update_game() # permet de mettre à jour la partie

                self.keep_get_full_board_active = True
                self.get_full_board()

                self.keep_update_chat_active = True # permet de maintenir la mise à jour du chat active
                self.update_chat() # permet de mettre à jour le chat

                self.keep_game_search_active = False # permet de désactiver la recherche de partie quand une partie est lancée
            else:
                print("Réponse serveur : Non")
                if self.keep_game_search_active: # si non on continue la recherche de partie
                    self.keep_game_search_id = self.root.after(1000, self.game_search) # permet de continuer la recherche de partie

        except Exception as e:
            print(f"Erreur lors de la demande: {e}")
    
    def play(self, row, col): # permet de jouer à une case (appeler quand on clique sur une des 9 cases du morpion)
        try:
            print(f"Je peux jouer ici {row}, {col}")  # afficher dans le terminal
            # Envoyer un message au serveur pour indiquer que le client est toujours actif
            message = ["jouer ici", row, col] 
            message_json = json.dumps(message) 
            self.client_socket.sendto(message_json.encode(), (self.server_ip, self.server_port)) # envoie au serveur la position du coup

        except Exception as e:
            print(f"Erreur lors de la demande pour jouer à cette case: {e}")

    def update_game(self):
        try:
            # Envoyer un message au serveur pour savoir si une action à été effectué dans la partie
            message = ["maj partie", self.last_update_partie]  # intutilé pour identifier la dernière action de la partie avec le timestamp
            message_json = json.dumps(message) # transformer en json pour l'envoyer au serveur 
            
            self.client_socket.sendto(message_json.encode(), (self.server_ip, self.server_port)) # envoie le message au serveur
            response, _ = self.client_socket.recvfrom(1024) 
            
            if response: # si le serveur répond au client
                response_decoded = json.loads(response.decode())
                if response_decoded[0] == "partie_lost": # si la partie est perdue
                    self.force_quit_game() # forcer à quitter la partie
                if response_decoded[0] == "nouvelle action":
                    for actions in response_decoded[1]: # [1] permet de récupérer les actions de la partie depuis la dernière maj
                        row, col, txt, game_state, winner, loser, current_Player = actions # permet de récupérer les informations de la partie
                        self.currentPlayer = response_decoded[2] # troisème parametre du message donc le joueur current
                        self.update_current_player() # permet de mettre à jour le joueur qui doit jouer
                        self.buttons[row][col].config(text=txt) # viens modifier le texte du bouton pour afficher le symbole du joueur
                        if game_state: 
                            if winner == None: 
                                messagebox.showinfo("Fin de partie", "Match nul!")
                            else:
                                if winner == self.pseudo_client:
                                    text = f"Le joueur {winner} a gagné!\nVous avez gagné!"
                                else:
                                    text = f"Le joueur {winner} a gagné!\nVous avez perdu!"
                                messagebox.showinfo("Fin de partie", text)
                            
                            # self.keep_update_game_active = False
                        self.last_update_partie = time.time() # permet de savoir la dernière action de la partie
                
                if response_decoded[0] == "zero nouvelle action": 
                    pass 

        except Exception as e:
            print(f"Erreur lors de la mise à jour de la partie : {e}")
        
        if self.keep_update_game_active: # si la mise à jour de la partie est active
            self.keep_update_game_id = self.root.after(1000, self.update_game) # permet de continuer la mise à jour de la partie

    def get_full_board(self):
        try:
            message = ["board"] 
            message_json = json.dumps(message) 
            self.client_socket.sendto(message_json.encode(), (self.server_ip, self.server_port)) # envoie au serveur la position du coup
            response, _ = self.client_socket.recvfrom(1024) 
            if response: # si le serveur répond au client
                response_decoded = json.loads(response.decode())
                board_game = response_decoded[1]
                for i in range(3):
                    for j in range(3):
                        button_text = self.buttons[i][j].cget('text')
                        board_value = board_game[i][j]
                        if button_text != board_value:
                            self.buttons[i][j].config(board_value)
                            print(f"Difference at position ({i},{j}): Button has '{button_text}' but board has '{board_value}'")
                        else:
                            print(f"Match at position ({i},{j}): Both have '{button_text}'")

        except Exception as e:
            print(f"Erreur lors de la mise à jour complète du board: {e}")

        if self.keep_get_full_board_active: # si la mise à jour de la partie est active
            self.keep_get_full_board_id = self.root.after(10000, self.get_full_board) # permet de continuer la mise à jour de la partie

    def update_chat(self):
        try:
            # Envoyer un message au serveur pour indiquer que le client est toujours actif
            message = ["upd_chat", self.last_update_msg]
            message_json = json.dumps(message)
            
            self.client_socket.sendto(message_json.encode(), (self.server_ip, self.server_port))
            response, _ = self.client_socket.recvfrom(1024)
            
            if response:
                response_decoded = json.loads(response.decode()) 
                if response_decoded[0] == "new_msg":
                    for msg in response_decoded[1]: # permet de récupérer les messages depuis la dernière maj
                        self.chat_display.configure(state=NORMAL) # permet de modifier le chat
                        if self.pseudo.get() == msg[0]:
                            txt = (f"{msg[0]} (Vous) : {msg[1]}\n") # permet de savoir si le message est du joueur
                        else:
                            txt = (f"{msg[0]} : {msg[1]}\n") # permet de savoir si le message est de l'adversaire
                        start_index = f"{END}-{len(txt)+1}c" # permet de modifier les styles du texte'
                        self.chat_display.insert(END, txt) # permet d'ajouter le texte à la fin du chat
                        self.chat_display.tag_configure('default', foreground='black', font=('Helvetica', 10)) # configurer le texte
                        self.chat_display.tag_add('default', start_index, END)
                        self.chat_display.configure(state=DISABLED) # LE joueur ne peux pas ecrire dans l'endroit ou le chat est affiché
                        self.chat_display.see(END)  # Faire défiler vers le bas
                        self.last_update_msg = time.time() 
                
                if response_decoded[0] == "ras": # rien a signaler :)
                    pass

        except Exception as e:
            print(f"Erreur lors de la mise à jour du chat : {e}")
        if self.keep_update_chat_active:
            self.keep_update_chat_id = self.root.after(1000, self.update_chat)
    
    def send_message_chat(self):
        if not self.check_message_chat(): # si le message contient des caractères interdits
            try:
                message = ["chat", self.message_chat.get()]  # permet de stocker le message
                message_json = json.dumps(message) # transformer en json pour l'envoyer au serveur

                self.client_socket.sendto(message_json.encode(), (self.server_ip, self.server_port)) # envoie le message au serveur
                self.entry_msg.delete(0, 'end') # permet de supprimer le message dans l'entrée utilisateur

            except Exception as e:
                print(f"Erreur lors de la connexion au serveur : {e}")
        else:
            self.entry_msg.delete(0, 'end')
            messagebox.showwarning("Erreur", "Votre message contient des caractères interdits ou est trop court.")
    
    def check_message_chat(self): # permet de checker si le message contient des caractères interdits
        forbidden_characters = r"[:\\;{}]"
        if re.search(forbidden_characters, self.message_chat.get()) or len(self.message_chat.get()) <= 1:
            return True # si le message contient des caractères interdits
        else:
            return False # si le message ne contient pas des caractères interdits
    
    def force_quit_game(self): # permet de forcer à quitter la partie
        self.keep_update_game_active = False
        self.root.after_cancel(self.keep_update_game_id) # permet d'annuler la mise à jour de la partie

        self.keep_get_full_board_active = False
        self.root.after_cancel(self.keep_get_full_board_id)

        self.keep_update_chat_active = False
        self.root.after_cancel(self.keep_update_chat_id) # permet d'annuler la mise à jour du chat

        self.return_page_2()    # permet de revenir à la page recherche de partie
               
    def quit_game(self): # permet de quitter la partie quand on clique sur le bouton quitter la partie
        try :
            message = ["quitter partie"]
            message_json = json.dumps(message)

            self.client_socket.sendto(message_json.encode(), (self.server_ip, self.server_port))
            response, _ = self.client_socket.recvfrom(1024)
            if response :
                self.keep_update_game_active = False # permet d'annuler la mise à jour de la partie 
                self.root.after_cancel(self.keep_update_game_id) # permet d'annuler la mise à jour de la partie

                self.keep_get_full_board_active = False
                self.root.after_cancel(self.keep_get_full_board_id)

                self.keep_update_chat_active = False 
                self.root.after_cancel(self.keep_update_chat_id) # permet d'annuler la mise à jour du chat
                print("Client quitte la partie", response.decode()) # afficher dans le terminal
                self.return_page_2()
                
        except Exception as e:
            print(f"Erreur lors de la tentative de quitter la partie : {e}")
    
    def disconnection(self): # permet de se déconnecter DU SERVEUR QUAND ON CLIQUE SUR LE BOUTON DECONNEXION
        try :
            message = ["deconnexion", self.pseudo.get()]
            message_json = json.dumps(message)

            self.client_socket.sendto(message_json.encode(), (self.server_ip, self.server_port))
            response, _ = self.client_socket.recvfrom(1024)
            print("Dans connexion, réponse du serveur :", response.decode())
            if response:
                self.keep_alive_active = False
                self.root.after_cancel(self.keep_alive_id)
                self.keep_game_search_active = False

                if self.keep_game_search_id:
                    self.root.after_cancel(self.keep_game_search_id)
                
                # self.stop_requesting()
                self.return_page_1()
        
        except Exception as e:
            print(f"Erreur lors de la tentative de déconnexion : {e}")

    ######## Méthodes avec actions sur la fenetre tkinter
    def on_validate(self, P): # permet de valider le message du chat
        return len(P) <= 25 # permet de limiter le message à 25 caractères

    def return_page_1(self):
        self.enable_btn_find_game()
        self.page_2.pack_forget()
        self.page_1.pack() # permet de revenir à la page 1
        self.root.geometry("400x200")

    def show_page_2(self):
        self.page_1.pack_forget() # permet de cacher la page 1
        self.page_2.pack()
        self.root.geometry("400x300")
    
    def return_page_2(self):
        self.page_3.pack_forget()
        self.page_2.pack()
        self.root.geometry("400x300") 
        for i in range(3): # permet de réinitialiser les boutons du morpion
            for j in range(3): #
                self.buttons[i][j].config(text="") # remet les cases à vides
        
        self.chat_display.configure(state=NORMAL) # clear le chat
        self.chat_display.delete(1.0, END) # pareil
        self.chat_display.configure(state=DISABLED) # pareil
    
    def show_page_3(self):
        self.page_2.pack_forget()
        self.page_3.pack()
        self.root.geometry("600x600")
        self.initialize_chat()
    
    def initialize_chat(self):
        self.chat_display.configure(state=NORMAL) # 
        txt = "Espace chat, veuillez rester respectueux envers votre adversaire sous peine de sanction\n"
        self.chat_display.insert(END, txt)
        start_index = f"{END}-{len(txt)+1}c"
        self.chat_display.tag_configure('gris_italique', foreground='grey', font=('Helvetica', 10, 'italic'))
        self.chat_display.tag_add('gris_italique', start_index, END)
        
        self.chat_display.configure(state=DISABLED)
    
    def change_pseudo_client(self):
        self.pseudo_client = self.pseudo.get()
        self.label_pseudo.config(text=f"Connecté en tant que : {self.pseudo_client}")
    
    def disable_btn_find_game(self):
        self.btn_find_game.config(state="disabled")
        self.btn_cancel_find_game.config(state="enabled")
    
    def enable_btn_find_game(self):
        self.btn_cancel_find_game.config(state="disabled")
        self.btn_find_game.config(state="enable")



    def update_current_player(self):
        self.label_current_player.config(text=f"C'est à : {self.currentPlayer} de jouer ")
        
    def run(self):
        self.read_server_info_from_file()
        self.root = Tk()
        self.root.geometry("400x200")
        self.root.title("TIC TAC TOE")

        # Création des pages
        self.page_1 = Frame(self.root)
        self.page_2 = Frame(self.root)
        self.page_3 = Frame(self.root)
        self.page_1.pack()


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
        self.entry_pseudo = Entry(self.page_1, textvariable=self.pseudo)

        btn_connection = Button(self.page_1, text="Se connecter", command=lambda:[self.change_pseudo_client(), self.connection()])
        # btn_connexion.config(width=20, height=2)

        btn_quit_app = Button(self.page_1, text="Quitter", command=lambda: self.root.destroy())
        # btn_quit_app.config(width=20, height=2)

        #----------Pack widget
        Label(self.page_1, text="Page 1").pack()
        Label(self.page_1, text="Pseudo").pack()
        self.entry_pseudo.pack()
        btn_connection.pack()
        btn_quit_app.pack()


        #-----------PAGE 2--------------
        # Création variable
        

        #----------Création et config widgets
        self.btn_find_game = Button(self.page_2, text="Trouver une partie", command=lambda:[self.join_queue(), self.disable_btn_find_game()])
        self.btn_cancel_find_game = Button(self.page_2, text="Quitter la file d'attente", state="disabled", command=lambda:[self.quit_queue()])
        self.btn_disconnection = Button(self.page_2, text="Déconnexion", command=lambda:[self.disconnection()])
        
        #----------Pack widget
        Label(self.page_2, text="Page 2").pack()
        self.label_pseudo = Label(self.page_2, text="")
        self.label_pseudo.pack()
        self.btn_find_game.pack()
        self.btn_cancel_find_game.pack()
        self.btn_disconnection.pack()


        #-----------PAGE 3--------------
        # Création variable
        self.message_chat = StringVar()

        #----------Création et config widgets
        self.chat_display = Text(self.page_3, height=8, width=25, state=DISABLED)
        self.validate_cmd = self.page_3.register(self.on_validate)
        self.entry_msg = Entry(self.page_3, textvariable=self.message_chat, validate="key", validatecommand=(self.validate_cmd, "%P"))
        self.entry_msg.grid(row=5, column=1, columnspan=2, sticky="ew")
        
        self.btn_send_message_chat = Button(self.page_3, text="Envoyer", command=lambda:[self.send_message_chat()])
        self.btn_quit_game = Button(self.page_3, text="Quitter la partie", command=self.quit_game) #self.return_page_2()
        # self.btn_rejouer = Button(self.page_3, text="Rejouer", state="disabled", command=lambda:[])

        #----------Grid widget
        self.label_current_player = Label(self.page_3, text="")
        self.label_current_player.grid(row=0, column=1, columnspan = 3, sticky = "ew")
        self.chat_display.grid(row=4, column=0, columnspan=3, sticky="ew")
        # Label(self.page_3, text="Connecté").grid(row=5, column=0, columnspan=3, sticky="ew")
        Label(self.page_3, text="Entrez votre message ci-dessous :").grid(row=5, column=0, columnspan=3, sticky="ew")
        self.entry_msg.grid(row=6, column=0, columnspan=2, sticky="ew")
        self.btn_send_message_chat.grid(row=6, column=2, sticky="ew")
        self.btn_quit_game.grid(row=7, column=0, sticky="w")

        self.player_symbol = Label(self.page_3, text="")
        self.player_symbol.grid(row=8, column=0, columnspan = 3, sticky = "ew")
        
        self.buttons = [[None for _ in range(3)] for _ in range(3)]

        for i in range(3):
            for j in range(3):
                button = Button(self.page_3, text=" ", style="Case.TButton", command=lambda row=i, col=j: self.play(row, col))
                button.grid(row=i+1, column=j, ipady=10, ipadx=10)
                self.buttons[i][j] = button


        self.root.mainloop()

# Utilisation du serveur
if __name__ == "__main__":
    udp_client = UDPClient()
    udp_client.run()

