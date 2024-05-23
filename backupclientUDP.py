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

        self.keep_game_search_active = False
        self.keep_game_search_id = None

        self.keep_update_chat_active = False
        self.keep_update_chat_id = None

        self.keep_update_game_active = False
        self.keep_update_game_id = None

        self.last_update_msg = time.time()
        self.last_update_partie = None

        self.pseudo_client = ""
    
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
    
    def connection(self):
        if not self.check_pseudo():
            try:
                message = ["connection", self.pseudo.get()]
                message_json = json.dumps(message)

                self.client_socket.sendto(message_json.encode(), (self.server_ip, self.server_port))
                response, _ = self.client_socket.recvfrom(1024)
                
                print("Dans connection, réponse serveur :", response.decode())
                if response:
                    self.keep_alive_active = True
                    self.show_page_2()
                    self.stay_connected()

            except Exception as e:
                print(f"Erreur lors de la connexion au serveur : {e}")
        else:
            self.entry_pseudo.delete(0, 'end')
            messagebox.showwarning("Erreur", "Le pseudo renseigné contient des caractères spéciaux ou n'est pas assez long.")
    
    def check_pseudo(self):
        forbidden_characters = r"[^\w\s]"
        if len(self.pseudo.get()) < 3 or re.search(forbidden_characters, self.pseudo.get()):
            return True
        else:
            return False
    
    def stay_connected(self):
        try:
            # Envoyer un message au serveur pour indiquer que le client est toujours actif
            message = ["alive"]
            message_json = json.dumps(message)
            
            self.client_socket.sendto(message_json.encode(), (self.server_ip, self.server_port))
            print("Envoi du message anti-afk")
            response, _ = self.client_socket.recvfrom(1024)
            print("Réponse serveur :", response.decode())
        except Exception as e:
            print(f"Erreur lors de l'envoi du message de présence : {e}")
        
        if self.keep_alive_active:
            self.keep_alive_id = self.root.after(10000, self.stay_connected)
    
    def join_queue(self):
        try:
            message = ["recherche partie"]
            message_json = json.dumps(message)

            self.client_socket.sendto(message_json.encode(), (self.server_ip, self.server_port))
            response, _ = self.client_socket.recvfrom(1024)
            print("Dans join_queue, réponse du serveur :", response.decode())
            if response:
                self.keep_game_search_active = True
                self.game_search()

        except Exception as e:
            print(f"Erreur lors de la tentative d'entrée dans la file d'attente: {e}")
    
    def quit_queue(self):
        try:
            # self.keep_game_search_active = False
            # self.root.after_cancel(self.keep_game_search_id)
            message = ["quitter file attente"]
            message_json = json.dumps(message)
            print(f"Tentative de retrait de la file d'attente")
            self.client_socket.sendto(message_json.encode(), (self.server_ip, self.server_port))
            response, _ = self.client_socket.recvfrom(1024)
            if response:
                print("Dans quit_queue, reponse serveur : ", response.decode())
                self.keep_game_search_active = False
                self.root.after_cancel(self.keep_game_search_id)
                self.enable_btn_find_game()

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
            message_received = json.loads(response.decode())

            if message_received[0] == "Oui":
                print("Réponse serveur : Oui")
                self.enable_btn_find_game()
                self.show_page_3()
                self.last_update_partie = time.time()

                self.keep_update_game_active = True
                self.update_game()

                self.keep_update_chat_active = True
                self.update_chat()

                self.keep_game_search_active = False
            else:
                print("Réponse serveur : Non")
                if self.keep_game_search_active:
                    self.keep_game_search_id = self.root.after(1000, self.game_search)

        except Exception as e:
            print(f"Erreur lors de la demande: {e}")
    
    def update_game(self):
        try:
            # Envoyer un message au serveur pour savoir si une action à été effectué dans la partie
            message = ["maj partie", self.last_update_partie]
            message_json = json.dumps(message)
            
            self.client_socket.sendto(message_json.encode(), (self.server_ip, self.server_port))
            response, _ = self.client_socket.recvfrom(1024)
            
            if response:
                response_decoded = json.loads(response.decode())
                if response_decoded[0] == "partie_lost":
                    self.force_quit_game()
                if response_decoded[0] == "nouvelle action":
                    for actions in response_decoded[1]:
                        row, col, txt, game_state, winner, loser = actions
                        self.buttons[row][col].config(text=txt)
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
                        self.last_update_partie = time.time()
                
                if response_decoded[0] == "zero nouvelle action":
                    pass

        except Exception as e:
            print(f"Erreur lors de la mise à jour de la partie : {e}")
        
        if self.keep_update_game_active:
            self.keep_update_game_id = self.root.after(1000, self.update_game)
    
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
                    for msg in response_decoded[1]:
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
                
                if response_decoded[0] == "ras":
                    pass

        except Exception as e:
            print(f"Erreur lors de la mise à jour du chat : {e}")
        if self.keep_update_chat_active:
            self.keep_update_chat_id = self.root.after(1000, self.update_chat)
    
    def send_message_chat(self):
        if not self.check_message_chat():
            try:
                message = ["chat", self.message_chat.get()]
                message_json = json.dumps(message)

                self.client_socket.sendto(message_json.encode(), (self.server_ip, self.server_port))
                self.entry_msg.delete(0, 'end')

            except Exception as e:
                print(f"Erreur lors de la connexion au serveur : {e}")
        else:
            messagebox.showwarning("Erreur", "Le message contient des caractères interdits.")
    
    def check_message_chat(self):
        forbidden_characters = r"[:\\;{}]"
        if re.search(forbidden_characters, self.message_chat.get()):
            return True
        else:
            return False
    
    def play(self, row, col):
        try:
            print(f"Je peux jouer ici {row}, {col}")
            # Envoyer un message au serveur pour indiquer que le client est toujours actif
            message = ["jouer ici", row, col]
            message_json = json.dumps(message)
            self.client_socket.sendto(message_json.encode(), (self.server_ip, self.server_port))

        except Exception as e:
            print(f"Erreur lors de la demande pour jouer à cette case: {e}")
        
    def force_quit_game(self):
        self.keep_update_game_active = False
        self.root.after_cancel(self.keep_update_game_id)

        self.keep_update_chat_active = False
        self.root.after_cancel(self.keep_update_chat_id)

        self.return_page_2()   
               
    def quit_game(self):
        try :
            # self.keep_update_game_active = False
            # self.root.after_cancel(self.keep_update_game_id)

            # self.keep_update_chat_active = False
            # self.root.after_cancel(self.keep_update_chat_id)

            message = ["quitter partie"]
            message_json = json.dumps(message)

            self.client_socket.sendto(message_json.encode(), (self.server_ip, self.server_port))
            response, _ = self.client_socket.recvfrom(1024)
            if response :
                self.keep_update_game_active = False
                self.root.after_cancel(self.keep_update_game_id)

                self.keep_update_chat_active = False
                self.root.after_cancel(self.keep_update_chat_id)
                print("Client quitte la partie", response.decode())
                self.return_page_2()
                
        except Exception as e:
            print(f"Erreur lors de la tentative de quitter la partie : {e}")
    
    def disconnection(self):
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
    def on_validate(self, P):
        return len(P) <= 25

    def return_page_1(self):
        self.enable_btn_find_game()
        self.page_2.pack_forget()
        self.page_1.pack()
        self.root.geometry("400x200")

    def show_page_2(self):
        self.page_1.pack_forget()
        self.page_2.pack()
        self.root.geometry("400x300")
    
    def return_page_2(self):
        self.page_3.pack_forget()
        self.page_2.pack()
        self.root.geometry("400x300")
        for i in range(3):
            for j in range(3):
                self.buttons[i][j].config(text="")
        
        self.chat_display.configure(state=NORMAL)
        self.chat_display.delete(1.0, END)
        self.chat_display.configure(state=DISABLED)
    
    def show_page_3(self):
        self.page_2.pack_forget()
        self.page_3.pack()
        self.root.geometry("600x600")
        self.initialize_chat()
    
    def initialize_chat(self):
        self.chat_display.configure(state=NORMAL)
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

    def run(self):
        self.read_server_info_from_file()
        self.root = Tk()
        self.root.geometry("400x200")
        self.root.title("Client UDP")

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
        self.btn_send_message_chat = Button(self.page_3, text="Envoyer", command=lambda:[self.send_message_chat()])
        self.btn_quit_game = Button(self.page_3, text="Quitter la partie", command=self.quit_game) #self.return_page_2()
        # self.btn_rejouer = Button(self.page_3, text="Rejouer", state="disabled", command=lambda:[])

        #----------Grid widget
        Label(self.page_3, text="Page 3").grid(row=0, column=1)
        # self.label_pseudo = Label(self.page_2, text="")
        # self.label_pseudo.pack()

        self.chat_display.grid(row=4, column=0, columnspan=3, sticky="ew")
        Label(self.page_3, text="Connecté").grid(row=5, column=0, columnspan=3, sticky="ew")
        self.entry_msg.grid(row=6, column=0, columnspan=2, sticky="ew")
        self.btn_send_message_chat.grid(row=6, column=2, sticky="ew")
        self.btn_quit_game.grid(row=7, column=0, sticky="w")

        self.buttons = [[None for _ in range(3)] for _ in range(3)]

        for i in range(3):
            for j in range(3):
                button = Button(self.page_3, text="", style="Case.TButton", command=lambda row=i, col=j: self.play(row, col))
                button.grid(row=i+1, column=j, ipady=10, ipadx=10)
                self.buttons[i][j] = button


        self.root.mainloop()

# Utilisation du serveur
if __name__ == "__main__":
    udp_client = UDPClient()
    udp_client.run()

