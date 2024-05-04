# UTILISER CE CLIENT

import socket
import tkinter as tk
from tkinter import messagebox
import json
import time
import re
from morpion import Morpion

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
                    self.update_chat()

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
                        self.chat_display.configure(state=tk.NORMAL)
                        if self.pseudo.get() == msg[0]:
                            txt = (f"{msg[0]} (You) : {msg[1]}\n")
                        else:
                            txt = (f"{msg[0]} : {msg[1]}\n")
                        self.chat_display.insert(tk.END, txt)
                        self.chat_display.configure(state=tk.DISABLED)
                        self.chat_display.see(tk.END)  # Faire défiler vers le bas
                        self.last_update_msg = time.time()
                
                if message_received[0] == "ras":
                    pass

        except Exception as e:
            print(f"Erreur lors de l'envoi du message de présence : {e}")
        
        if self.keep_alive_active:
            self.update_msg_id = self.root.after(1000, self.update_chat)
    
    def afficher_page_1(self):
        self.page2.pack_forget()
        self.page1.pack()

    def afficher_page_2(self):
        self.page1.pack_forget()
        self.page2.pack()
    
    def retour_page_2(self):
        self.page3.pack_forget()
        self.page2.pack()
    
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
    
    def on_validate(self, P):
        # Limiter à 10 caractères
        return len(P) <= 10

    def jouer(self):
        self.page2.pack_forget()
        self.page3.pack()
    
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
    
    def partie_trouvee(self):
        try:
            # Envoyer un message au serveur pour indiquer que le client est toujours actif
            request = ["Partie trouvée ?"]
            request_json = json.dumps(request)
            self.client_socket.sendto(request_json.encode(), (self.server_ip, self.server_port))

            response, _ = self.server_socket.recvfrom(1024)
            message_received = json.loads(response.decode())

            if message_received[0] == "Oui":
                self.jouer()
            else:
                if self.keep_alive_active:
                    # Planifier l'appel à la fonction toutes les 10 secondes
                    self.partie_trouvee_id = self.root.after(1000, self.partie_trouvee)
        except Exception as e:
            print(f"Erreur lors de l'envoi du message de présence : {e}")

    def play(self, row, col):
        pass
        # if self.board[row][col] == " ":
        #     try:
        #         request = ["action", row, col]
        #         request_json = json.dumps(request)
                
        #         self.client_socket.sendto(chat_json.encode(), (self.server_ip, self.server_port))

        #         self.board[row][col] = self.current_player
        #         self.buttons[row][col].config(text=self.current_player)
                
        #         if self.check_winner():
        #             messagebox.showinfo("Fin de partie", f"Le joueur {self.current_player} a gagné!")
        #             self.reset_game()
        #         elif self.is_board_full():
        #             messagebox.showinfo("Fin de partie", "Match nul!")
        #             self.reset_game()
        #         else:
        #             self.current_player = "O" if self.current_player == "X" else "X"
    
    def run(self):
        self.read_server_info_from_file()
        self.root = tk.Tk()
        self.root.geometry("600x600")
        self.root.title("Client UDP")

        # Création des pages
        self.page1 = tk.Frame(self.root)
        self.page2 = tk.Frame(self.root)
        self.page3 = tk.Frame(self.root)
        self.page1.pack()


        # -------------- PAGE 1 --------------------
        # Création variable
        self.pseudo = tk.StringVar()
        # self.placeholder = "Entrez votre pseudo ici"
        
        #----------Création et config widgets
        self.entry_pseudo = tk.Entry(self.page1, textvariable=self.pseudo)

        btn_connexion = tk.Button(self.page1, text="Connexion", command=lambda:[self.connexion()])
        btn_connexion.config(width=20, height=2)

        btn_quitter = tk.Button(self.page1, text="Quitter")
        btn_quitter.config(width=20, height=2)

        #----------Pack widget
        tk.Label(self.page1, text="Page 1").pack()
        tk.Label(self.page1, text="Pseudo").pack()
        self.entry_pseudo.pack()
        btn_connexion.pack()
        btn_quitter.pack()


        #-----------PAGE 2--------------
        # Création variable
        

        #----------Création et config widgets
        self.btn_jouer = tk.Button(self.page2, text="Jouer", command=lambda:[self.rejoindre_file_attente()])
        self.btn_retour = tk.Button(self.page2, text="Déconnexion", command=lambda:[self.deconnexion()])
        
        #----------Pack widget
        tk.Label(self.page2, text="Page 2").pack()
        
        self.btn_jouer.pack()
        self.btn_retour.pack()


        #-----------PAGE 3--------------
        # Création variable
        self.message2 = tk.StringVar()

        #----------Création et config widgets
        self.chat_display = tk.Text(self.page3, height=8, width=25, state=tk.DISABLED)
        self.validate_cmd = self.page3.register(self.on_validate)
        self.entry_msg = tk.Entry(self.page3, textvariable=self.message2, validate="key", validatecommand=(self.validate_cmd, "%P"))
        self.btn_envoyer = tk.Button(self.page3, text="Envoyer", command=lambda:[self.send_msg()])
        self.btn_retour = tk.Button(self.page3, text="Retour", command=lambda:[self.retour_page_2()])

        #----------Pack widget
        self.chat_display.grid(row=3, column=0, columnspan=3, sticky="ew")
        self.entry_msg.grid(row=4, column=0, columnspan=2, sticky="ew")
        self.btn_envoyer.grid(row=4, column=2, sticky="ew")
        self.btn_retour.grid(row=5, column=0, sticky="w")



        self.current_player = "X"
        self.board = [[" " for _ in range(3)] for _ in range(3)]

        self.buttons = [[None for _ in range(3)] for _ in range(3)]

        for i in range(3):
            for j in range(3):
                button = tk.Button(self.page3, text="", font=("Helvetica", 24), width=4, height=2,
                                   command=lambda row=i, col=j: self.play(row, col))
                button.grid(row=i, column=j, sticky="ew")
                self.buttons[i][j] = button


        self.root.mainloop()

udp_client = UDPClient()
udp_client.run()
