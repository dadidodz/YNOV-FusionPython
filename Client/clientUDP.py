import socket
from tkinter import *
from tkinter import messagebox
from tkinter.ttk import *
import json
import time
import re
import os

class UDPClient: # Objet UDPClient avec les fonctionnalités et l'interface graphique
    """
    Classe UDPClient

    Attributs : 
        server_ip (str) : Adresse IP du serveur
        server_port (int) : Port de communication du serveur
        client_socket (socket) : Socket de communication vers le serveur

        keep_alive_active (bool) : Condition pour continuer d'envoyer une message de présence au serveur
        keep_alive_id (str) : Permet de stocker l'id de l'appel de la fonction associée (stay_connected())

        keep_game_search_active (bool) : Condition pour continuer d'envoyer une message de recherche de partie au serveur
        keep_game_search_id (str) : Permet de stocker l'id de l'appel de la fonction associée (game_search())

        keep_update_game_active (bool) : Condition pour continuer d'envoyer une message de mise à jour de la partie au serveur
        keep_update_game_id (str) : Permet de stocker l'id de l'appel de la fonction associée (update_game())

        keep_update_chat_active (bool) : Condition pour continuer d'envoyer une message de mise à jour de la partie au serveur
        keep_update_chat_id (str) : Permet de stocker l'id de l'appel de la fonction associée (update_chat())

        keep_get_full_board_active (bool) : Condition pour continuer d'envoyer une message de l'état complet du plateau de jeu au serveur
        keep_get_full_board_id (str) : Permet de stocker l'id de l'appel de la fonction associée (get_full_board())

        last_update_game (float) : Stocke le timestamp de la dernier fois où la partie a été mis à jour
        last_update_chat (float) : Stocke le timestamp de la dernier fois où le chat de la partie a été mis à jour

        pseudo_client (str) : Stocke le pseudo sous lequel le joueur s'est connecté
        current_player (str) : Stocke le pseudo du joueur auquelle c'est au tour de jouer
    """
    def __init__(self): 
        """
        Initialise les attributs de UDPClient.
        """
        self.server_ip = ""
        self.server_port = 0
        self.client_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.keep_alive_active = False
        self.keep_alive_id = None
        self.keep_game_search_active = False 
        self.keep_game_search_id = None 
        self.keep_update_game_active = False 
        self.keep_update_game_id = None 
        self.keep_update_chat_active = False
        self.keep_update_chat_id = None 
        self.keep_get_full_board_active = False
        self.keep_get_full_board_id = None
        self.last_update_chat = None
        self.last_update_game  = None 
        self.pseudo_client = ""
        self.current_player = ""

        self.read_server_info_from_file()
        
    def read_server_info_from_file(self, filename='../config.txt'):
        """
        Lis le fichier config.txt afin d'en extraire l'IP et le Port du serveur et attribut les données à server_ip et server_port

        Paramètre :
        filename (str) : Nom du fichier
        """
        try:
            filepath = os.path.join(os.path.dirname(__file__), filename)
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
        """
        Envoie un message au serveur avec un intitulé (message[0] = connection), le pseudo et le mot de passe du joueur.
        Effectue différentes actions en fonction de la réponse du serveur.
        """
        if not self.check_pseudo() and not self.check_password(): # Vérifie si le pseudo et le mot de passe sont valides
            try: 
                message = ["connection", self.pseudo.get(), self.password.get()] # Stocke les informations (intitulé, pseudo, mot de passe) dans une liste
                message_json = json.dumps(message) # Transforme les données en json 
                self.client_socket.sendto(message_json.encode(), (self.server_ip, self.server_port)) # Envoie le message au serveur
                
                response, _ = self.client_socket.recvfrom(1024) # Stocke la réponse du serveur dans response, et ne stocke pas les autres informations
                response_decoded = json.loads(response.decode()) # Decode le message json
                print("Dans connection, réponse serveur :", response.decode()) # Affiche la réponse du serveur dans la console

                if response_decoded[0] == "already_connected": # Si l'intitulé de la réponse du serveur est "already_connected"
                    self.entry_password.delete(0, 'end') # Supprimer le texte rentré dans le champ "mot de passe"
                    messagebox.showwarning("Erreur", "Vous êtes déjà connecté depuis un autre poste.") # Ouvre une fenêtre pour afficher un message d'erreur
                
                if response_decoded[0] == "rejected": # Si l'intitulé de la réponse du serveur est "rejected"
                    self.entry_password.delete(0, 'end') # Supprimer le texte rentré dans le champ "mot de passe"
                    messagebox.showwarning("Erreur", "Pseudo ou mot de passe incorrect.") # Ouvre une fenêtre pour afficher un message d'erreur

                if response_decoded[0] == "connected": # Si l'intitulé de la réponse du serveur est "connected"
                    self.show_page_2() # Affiche la page suivante
                    self.keep_alive_active =  True # Active le booleén "keep_alive_active" afin de resté connecté au serveur
                    self.stay_connected() # Lance la fonction "stay_connected"

            except Exception as e: # Gère l'exception si le client n'arrive pas à se connecter
                print(f"Erreur lors de la connexion au serveur : {e}")

        else: # Le pseudo ou le mot de passe n'est pas valide
            self.entry_password.delete(0, 'end') # Supprimer le texte rentré dans le champ "mot de passe"
            messagebox.showwarning("Erreur", "Pseudo ou mot de passe trop court, ou bien le pseudo renseigné contient des caractères spéciaux interdits.") # Ouvre une fenêtre pour afficher un message d'erreur
    
    def check_pseudo(self):
        """
        Vérifie si le pseudo est valide.

        Retour:
        True : si le pseudo contient des caractères interdits ou fait moins de 3 caractères
        False : si le pseudo ne contient aucun caractère interdit et fait au moins 3 caractères
        """
        forbidden_characters = r"[^\w\s]"
        if len(self.pseudo.get()) < 3 or re.search(forbidden_characters, self.pseudo.get()):
            return True
        else:
            return False
    
    def check_password(self):
        """
        Vérifie si le mot de passe est valide.

        Retour:
        True : si le mot de passe fait moins de 5 caractères
        False : si le mot de passe fait au moins 5 caractères
        """
        if len(self.password.get()) <= 4:
            return True
        else:
            return False
    
    def stay_connected(self):
        """
        Maintient le joueur connecté au serveur.
        """
        try:
            message = ["alive"] 
            message_json = json.dumps(message)

            print("Envoi du message anti-afk")
            self.client_socket.sendto(message_json.encode(), (self.server_ip, self.server_port)) # envoie le message au serveur

            response, _ = self.client_socket.recvfrom(1024)
            print("Réponse serveur :", response.decode()) # Affiche la réponse dans la console
        except Exception as e:
            print(f"Erreur lors de l'envoi du message de présence : {e}")
        
        if self.keep_alive_active:
            self.keep_alive_id = self.root.after(10000, self.stay_connected) # Appel récursif si la condition est vraie
            
            
    def join_queue(self):
        """
        Ajoute le joueur dans la file d'attente sur le serveur.
        """
        try:
            message = ["search_game"]
            message_json = json.dumps(message) 

            self.client_socket.sendto(message_json.encode(), (self.server_ip, self.server_port))
            response, _ = self.client_socket.recvfrom(1024)
            print("Dans join_queue, réponse du serveur :", response.decode()) # afficher la réponse du serveur
            
            # Puisque que le client n'écoute pas en permanence le serveur, il doit envoyer un message pour savoir si la partie a été trouvée
            if response: # Si le serveur répond au client (et donc, qu'il a bien rejoint la file d'attente)
                self.keep_game_search_active = True  # Condition de maintient de recherche de partie
                self.game_search() # Lance la recherche de partie afin de savoir si le joueur a trouvé un partie

        except Exception as e:
            print(f"Erreur lors de la tentative d'entrée dans la file d'attente: {e}")
    
    def quit_queue(self): # permet de quitter la file d'attente quand on clique sur le bouton quitter la file d'attente
        """
        Quitte la file d'attente lorsque le joueur clique sur le bouton "Quitter file d'attente".
        """
        try:
            message = ["quit_queue"] 
            message_json = json.dumps(message)
            print(f"Tentative de retrait de la file d'attente") # afficher dans le terminal
            self.client_socket.sendto(message_json.encode(), (self.server_ip, self.server_port)) # envoie le message au serveur
            response, _ = self.client_socket.recvfrom(1024) # reponse du serveur 
            if response: # Si le serveur répond au client (et donc, qu'il a bien quitter la file d'attente)
                print("Dans quit_queue, reponse serveur : ", response.decode()) # afficher la réponse du serveur
                self.keep_game_search_active = False # Désactive la recherche de partie
                self.root.after_cancel(self.keep_game_search_id) # Arrête le processus de recherche de partie, si un appel est planifié
                self.enable_btn_find_game() # Active le bouton "trouver une partie"

        except Exception as e:
            print(f"Erreur lors de la tentative de retrait de la file d'attente: {e}")
    
    def game_search(self):
        """
        Envoie un message au serveur pour demander si le joueur a trouvé une partie.
        La méthode est rappelée tant que la réponse est "Non" ou bien que le joueur quitte la file d'attente.
        """
        try:
            print("Partie trouvée ?")
            message = ["game_found"]
            message_json = json.dumps(message)

            self.client_socket.sendto(message_json.encode(), (self.server_ip, self.server_port))

            response, _ = self.client_socket.recvfrom(1024)
            if response:
                response_decoded = json.loads(response.decode())
                if response_decoded[0] == "Yes": # Si l'intitulé de la réponse est "Oui"
                    print("Réponse serveur : Oui") 
                    self.keep_game_search_active = False # Désactive la recherche de partie
                    
                    self.player_symbol.config(text=f"Connecté en tant que : {self.pseudo_client}, Symbole : {response_decoded[2]}") # Modifie le texte afin de savoir le symbole du joueur
                    self.enable_btn_find_game() # Réinitialise l'état des boutons "Trouver une partie" et "Quitter file d'attente"
                    self.show_page_3() # Affiche la partie

                    self.last_update_game  = time.time() # Stocke le timestamp de la dernière mise à jour de la partie
                    self.last_update_chat = time.time() # Stocke le timestamp de la dernière mise à jour du chat
                    
                    self.current_player = response_decoded[1] # permet de savoir qui doit jouer
                    self.update_current_player() # permet de mettre à jour le joueur qui doit jouer

                    self.keep_update_game_active = True # Active la condition de mise à jour de la partie
                    self.update_game() # Lance la mise à jour de la partie

                    self.keep_get_full_board_active = True # Active la condition de mise à jour du plateau de jeu
                    self.get_full_board() # Lance la mise à jour du plateau

                    self.keep_update_chat_active = True # permet de maintenir la mise à jour du chat active
                    self.update_chat() # Lance la mise à jour du chat
                    
                else:
                    print("Réponse serveur : Non")
                    if self.keep_game_search_active: # si non on continue la recherche de partie
                        self.keep_game_search_id = self.root.after(5000, self.game_search) # Appel de la méthode game_search() dans 5 secondes

        except Exception as e:
            print(f"Erreur lors de la recherche de partie : {e}")
    
    def play(self, row, col):
        """
        Envoie un message au serveur contenant l'intitulé du message, la ligne et colonne (dans un plateau de jeu 3x3) sur lequel le joueur a cliqué.

        Paramètres :
        row (int) : Ligne du bouton cliqué
        col (int) : Colonne du bouton cliqué
        """
        try:
            print(f"Je peux jouer ici {row}, {col}")
            message = ["play_here", row, col] 
            message_json = json.dumps(message)

            self.client_socket.sendto(message_json.encode(), (self.server_ip, self.server_port))

        except Exception as e:
            print(f"Erreur lors de la demande pour jouer à cette case: {e}")

    def update_game(self):
        """
        Envoie un message au serveur pour savoir si de nouveaux coups ont été joués depuis la dernière mise à jour.
        """
        try:
            message = ["update_game", self.last_update_game ]  # Intitulé du message et le timestamp de la dernière mise à jour
            message_json = json.dumps(message)
            
            self.client_socket.sendto(message_json.encode(), (self.server_ip, self.server_port))
            response, _ = self.client_socket.recvfrom(1024) 
            
            if response: # si le serveur répond au client
                response_decoded = json.loads(response.decode())

                if response_decoded[0] == "game_lost": # Si la partie est perdue, c'est-à-dire, si un des deux joueurs l'a quittée
                    self.force_quit_game() # Force à quitter la partie

                elif response_decoded[0] == "new_action":
                    for actions in response_decoded[1]: # Récupère les actions de la partie
                        row, col, txt, game_state, winner, loser, current_player = actions # Stocke les informations de la partie stockés dans actions (tuple)
                        self.current_player = response_decoded[2] # Récupère le joueur a qui est le tour
                        self.update_current_player() # Met à jour graphiquement le joueur qui doit jouer
                        self.buttons[row][col].config(text=txt) # Modifie le texte du bouton pour afficher le symbole du joueur
                        if game_state: # Si l'état de la partie est autre que "None"
                            if winner == None: 
                                messagebox.showinfo("Fin de partie", "Match nul!")
                            else:
                                if winner == self.pseudo_client:
                                    text = f"Le joueur {winner} a gagné!\nVous avez gagné!"
                                else:
                                    text = f"Le joueur {winner} a gagné!\nVous avez perdu!"
                                messagebox.showinfo("Fin de partie", text) # Ouvre une fenêtre pour afficher le gagnant
                            
                        self.last_update_game  = time.time() # Stocke le timestamp de la dernière mise à jour
                
                elif response_decoded[0] == "no_new_actions": 
                    pass 

        except Exception as e:
            print(f"Erreur lors de la mise à jour de la partie : {e}")
        
        if self.keep_update_game_active: # si la mise à jour de la partie est active
            self.keep_update_game_id = self.root.after(3000, self.update_game) # Appel de la méthode update_game() dans 3 secondes

    def get_full_board(self):
        """
        Récupère l'état de toutes les cases du plateau de jeu.
        Normalement, tous les coups sont récupérés dans update_game(), mais parfois, car nous sommes en communication UDP avec le serveur,
        des informations sont perdus, et des cases sur lesquelles un des deux joueurs à joué, n'apparaît pas graphiquement.
        Cette méthode permet de mettre à jour toutes les cases du plateau de jeu au cas où des coups se soient perdus.
        """
        try:
            message = ["get_board"] 
            message_json = json.dumps(message)

            self.client_socket.sendto(message_json.encode(), (self.server_ip, self.server_port))

            response, _ = self.client_socket.recvfrom(1024) 
            if response:
                response_decoded = json.loads(response.decode())
                board_game = response_decoded[1] # Stocke toutes les cases du plateau du jeu qu'il y a dans la partie sur le serveur
                for i in range(3):
                    for j in range(3):
                        button_text = self.buttons[i][j].cget('text')
                        board_value = board_game[i][j]
                        if button_text != board_value: # S'il y a une différence entre le texte de la case graphique et la case du serveur
                            self.buttons[i][j].config(text=board_value) # Modifie le texte du bouton graphique pour qu'il concorde avec celui sur le serveur

        except Exception as e:
            print(f"Erreur lors de la mise à jour complète du board: {e}")

        if self.keep_get_full_board_active: # si la mise à jour de la partie est active
            self.keep_get_full_board_id = self.root.after(10000, self.get_full_board) # Appel de la méthode get_full_board() dans 10 secondes

    def update_chat(self):
        """
        Envoie un message au serveur pour savoir si de nouveaux messages ont été envoyé depuis la dernière mise à jour du chat.
        """
        try:
            message = ["update_chat", self.last_update_chat]
            message_json = json.dumps(message)
            
            self.client_socket.sendto(message_json.encode(), (self.server_ip, self.server_port))

            response, _ = self.client_socket.recvfrom(1024)
            
            if response:
                response_decoded = json.loads(response.decode()) 
                if response_decoded[0] == "new_msg":
                    for msg in response_decoded[1]: # Récupère les messages depuis la dernière mise à jour du chat
                        self.chat_display.configure(state=NORMAL) # Active la possibilité d'insérer du texte dans le chat graphique
                        if self.pseudo.get() == msg[0]:
                            txt = (f"{msg[0]} (Vous) : {msg[1]}\n") # Permet de savoir si le message est du joueur
                        else:
                            txt = (f"{msg[0]} : {msg[1]}\n") # Permet de savoir si le message est de l'adversaire
                        start_index = f"{END}-{len(txt)+1}c" # Stocke à partie d'où le message doit avec le "tag" (style) appliqué
                        self.chat_display.insert(END, txt) # Ajoute le texte à la fin du chat
                        self.chat_display.tag_configure('default', foreground='black', font=('Helvetica', 10)) # Applique le tag au message
                        self.chat_display.tag_add('default', start_index, END)
                        self.chat_display.configure(state=DISABLED) # Désacctive la possibilité d'insérer du texte dans le chat graphique
                        self.chat_display.see(END)  # Fait défiler vers le bas si le message sort du chat graphique
                        self.last_update_chat = time.time() # Met à jour le timestamp
                
                if response_decoded[0] == "ras": # Rien à signaler :)
                    pass

        except Exception as e:
            print(f"Erreur lors de la mise à jour du chat : {e}")

        if self.keep_update_chat_active:
            self.keep_update_chat_id = self.root.after(1000, self.update_chat) # Appel de la méthode update_chat() dans 1 seconde
    
    def send_message_chat(self):
        """
        Envoie un message contenant le message que le joueur a saisi.
        """
        if not self.check_message_chat(): # Si le message ne contient pas de caractères interdits
            try:
                message = ["new_chat_message", self.message_chat.get()] 
                message_json = json.dumps(message)

                self.client_socket.sendto(message_json.encode(), (self.server_ip, self.server_port)) # envoie le message au serveur

                self.entry_msg.delete(0, 'end') # Supprimer le message dans l'entrée graphique du joueur

            except Exception as e:
                print(f"Erreur lors de la connexion au serveur : {e}")
        else:
            self.entry_msg.delete(0, 'end')
            messagebox.showwarning("Erreur", "Votre message contient des caractères interdits ou est vide.")
    
    def check_message_chat(self):
        """
        Vérifie si le message contient des caractères interdits ou si le message est vide.

        Retour:
        True : si le message contient des caractères interdits ou fait moins de 1 caractère
        False : si le message ne contient pas de caractères interdits ou fait au moins 1
        """
        forbidden_characters = r"[:\\;{}]"
        if re.search(forbidden_characters, self.message_chat.get()) or len(self.message_chat.get()) <= 0:
            return True # si le message contient des caractères interdits
        else:
            return False # si le message ne contient pas des caractères interdits
    
    def force_quit_game(self): # permet de forcer à quitter la partie
        """
        Force à quitter graphiquement la partie et stoppe les conditions et les appels de mise à jour de la partie et du chat.
        """
        self.keep_update_game_active = False # Désactive la condition d'appel à la méthode update_game()
        self.root.after_cancel(self.keep_update_game_id) # Annule l'appel planifié de la mise à jour de la partie

        self.keep_get_full_board_active = False
        self.root.after_cancel(self.keep_get_full_board_id) # Annule l'appel planifié de la mise à jour du plateau de jeu

        self.keep_update_chat_active = False
        self.root.after_cancel(self.keep_update_chat_id) # Annule l'appel planifié de la mise à jour du chat

        self.return_page_2()    # Revient à la page recherche de partie
               
    def quit_game(self):
        """
        Envoie un message afin de quitter la partie lorsque le joueur clique sur le bouton "Quitter la partie".
        """
        try :
            message = ["quit_game"]
            message_json = json.dumps(message)

            self.client_socket.sendto(message_json.encode(), (self.server_ip, self.server_port))

            response, _ = self.client_socket.recvfrom(1024)
            if response :
                self.force_quit_game()
                
        except Exception as e:
            print(f"Erreur lors de la tentative de quitter la partie : {e}")
    
    def disconnection(self):
        """
        Envoie un message afin de se déconnecter du serveur lorsque le joueur clique sur le bouton "Déconnexion".
        """
        try :
            message = ["disconnect", self.pseudo.get()]
            message_json = json.dumps(message)

            self.client_socket.sendto(message_json.encode(), (self.server_ip, self.server_port))

            response, _ = self.client_socket.recvfrom(1024)
            print("Dans connexion, réponse du serveur :", response.decode())
            if response:
                self.keep_alive_active = False # Désactive la condition d'appel à la méthode stay_connected()
                self.root.after_cancel(self.keep_alive_id) # Annule l'appel planifié de la fonction stay_connected()
                self.keep_game_search_active = False # Désactive la condition d'appel à la méthode game_search() si le joueur se déconnecte sans quitter la file d'attente au préalable

                if self.keep_game_search_id:
                    self.root.after_cancel(self.keep_game_search_id) # Annule l'appel planifié de la fonction game_search() si un est planifié

                self.return_page_1() # Retour à la page de connexion
        
        except Exception as e:
            print(f"Erreur lors de la tentative de déconnexion : {e}")

    ######## Méthodes avec actions sur la fenetre tkinter
    def on_validate(self, P):
        """
        Méthode appelé pour bloqué le nombre de caractères rentré dans un message du chat

        Paramètre :
        P (str) : message actuelle dans l'entrée
        """
        return len(P) <= 50 # Limite le message à 50 caractères

    def return_page_1(self):
        """
        Retour à la page 1 de l'application, depuis la page 2.
        """
        self.enable_btn_find_game()
        self.page_2.pack_forget()
        self.page_1.pack() # permet de revenir à la page 1
        self.root.geometry("400x200") # Redimensionne la fenêtre de l'application

    def show_page_2(self):
        """
        Affiche à la page 2 de l'application, depuis la page 1.
        """
        self.entry_password.delete(0, 'end')
        self.page_1.pack_forget() # Cache la page 1
        self.page_2.pack() # Affiche la page 2
        self.root.geometry("400x300")
    
    def return_page_2(self):
        """
        Affiche à la page 2 de l'application, depuis la page 3.
        """
        self.page_3.pack_forget()
        self.page_2.pack()
        self.root.geometry("400x300") 
        for i in range(3): # Réinitialise les boutons du plateau de jeu
            for j in range(3): #
                self.buttons[i][j].config(text="") # Remet les cases à vide
        
        self.chat_display.configure(state=NORMAL) 
        self.chat_display.delete(1.0, END) # Efface tous les messages du chat
        self.chat_display.configure(state=DISABLED) 
    
    def show_page_3(self):
        """
        Affiche à la page 3 de l'application, depuis la page 3.
        """
        self.page_2.pack_forget()
        self.page_3.pack()
        self.root.geometry("600x600")
        self.initialize_chat()
    
    def initialize_chat(self):
        """
        Initialise le chat avec un message.
        """
        self.chat_display.configure(state=NORMAL)
        txt = "Espace chat, veuillez rester respectueux envers votre adversaire sous peine de sanction\n"
        self.chat_display.insert(END, txt)
        start_index = f"{END}-{len(txt)+1}c"
        self.chat_display.tag_configure('gris_italique', foreground='grey', font=('Helvetica', 10, 'italic'))
        self.chat_display.tag_add('gris_italique', start_index, END)
        self.chat_display.configure(state=DISABLED)
    
    def change_pseudo_client(self):
        """
        Modifie le pseudo du jouer dans la page 2.
        """
        self.pseudo_client = self.pseudo.get()
        self.label_pseudo.config(text=f"Connecté en tant que : {self.pseudo_client}")
    
    def disable_btn_find_game(self):
        """
        Désactive le bouton "Rechercher une partie" et active le bouton "Quitter la file d'attente".
        """
        self.btn_find_game.config(state="disabled")
        self.btn_cancel_find_game.config(state="enabled")
    
    def enable_btn_find_game(self):
        """
        Désactive le bouton "Quitter la file d'attente" et active le bouton "Rechercher une partie".
        """
        self.btn_cancel_find_game.config(state="disabled")
        self.btn_find_game.config(state="enable")

    def update_current_player(self):
        """
        Met à jour le pseudo du joueur qui doit jouer.
        """
        self.label_current_player.config(text=f"C'est à : {self.current_player} de jouer ")
        
    def run(self):
        """
        Lance l'application graphique.
        """
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
        self.password = StringVar()

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
        self.entry_password = Entry(self.page_1, show="*", textvariable=self.password)
        btn_connection = Button(self.page_1, text="Se connecter", command=lambda:[self.change_pseudo_client(), self.connection()])
        btn_quit_app = Button(self.page_1, text="Quitter", command=lambda: self.root.destroy())

        #----------Pack widgets
        Label(self.page_1, text="Page de connexion").pack()
        Label(self.page_1, text="Votre pseudo").pack()
        self.entry_pseudo.pack()
        Label(self.page_1, text="Votre mot de passe").pack()
        self.entry_password.pack()
        btn_connection.pack()
        btn_quit_app.pack()

        #-----------PAGE 2--------------
        #----------Création et config widgets
        self.btn_find_game = Button(self.page_2, text="Trouver une partie", command=lambda:[self.join_queue(), self.disable_btn_find_game()])
        self.btn_cancel_find_game = Button(self.page_2, text="Quitter la file d'attente", state="disabled", command=lambda:[self.quit_queue()])
        self.btn_disconnection = Button(self.page_2, text="Déconnexion", command=lambda:[self.disconnection()])
        
        #----------Pack widget
        Label(self.page_2, text="Salon").pack()
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
        self.btn_quit_game = Button(self.page_3, text="Quitter la partie", command=self.quit_game)

        #----------Grid widget
        self.label_current_player = Label(self.page_3, text="")
        self.label_current_player.grid(row=0, column=1, columnspan = 3, sticky = "ew")
        self.chat_display.grid(row=4, column=0, columnspan=3, sticky="ew")
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

if __name__ == "__main__":
    udp_client = UDPClient() # Crée un objet UDPClient
    udp_client.run() # Démarre le client

