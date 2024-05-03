# UTILISER CE CLIENT

import socket
import tkinter as tk
from tkinter import messagebox
import json
import time

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
        if len(self.pseudo.get()) > 2:
            try:
                message = ["connexion", self.pseudo.get()]
                message_json = json.dumps(message)

                self.client_socket.sendto(message_json.encode(), (self.server_ip, self.server_port))
                response, _ = self.client_socket.recvfrom(1024)
                print("Dans connexion, réponse du serveur :", response.decode())
                if response:
                    self.afficher_page_2()
                    self.stay_connected()
                    self.update_chat()

            except Exception as e:
                print(f"Erreur lors de la connexion au serveur : {e}")
        else:
            self.entry_pseudo.delete(0, 'end')
            messagebox.showwarning("Erreur", "Le pseudo renseigné n'est pas assez long.")
    
    def stay_connected(self):
        try:
            # Envoyer un message au serveur pour indiquer que le client est toujours actif
            alive = ["alive"]
            alive_json = json.dumps(alive)
            
            self.client_socket.sendto(alive_json.encode(), (self.server_ip, self.server_port))
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
            message = ["chat", self.pseudo.get(), self.message2.get()]
            message_json = json.dumps(message)

            self.client_socket.sendto(message_json.encode(), (self.server_ip, self.server_port))
            self.entry_msg.delete(0, 'end')

        except Exception as e:
            print(f"Erreur lors de la connexion au serveur : {e}")
    
    def update_chat(self):
        try:
            # Envoyer un message au serveur pour indiquer que le client est toujours actif
            chat = ["upd_chat", self.last_update_msg]
            chat_json = json.dumps(chat)
            
            self.client_socket.sendto(chat_json.encode(), (self.server_ip, self.server_port))
            response, _ = self.client_socket.recvfrom(1024)
            message_received = json.loads(response.decode())
            if response:
                if message_received[0] == "new_msg":
                    for msg in message_received[1]:
                        self.chat_display.configure(state=tk.NORMAL)
                        # self.chat_display.insert(tk.END, f"{self.pseudo.get()} (You): {msg}\n")
                        self.chat_display.insert(tk.END, f"{msg}\n")
                        self.chat_display.configure(state=tk.DISABLED)
                        self.chat_display.see(tk.END)  # Faire défiler vers le bas
                        self.last_update_msg = time.time()
                
                if message_received[0] == "ras":
                    pass
            # print("Dans update_chat, réponse du serveur :", response.decode())
        except Exception as e:
            print(f"Erreur lors de l'envoi du message de présence : {e}")
        
        if self.keep_alive_active:
            # Planifier l'appel à la fonction toutes les 10 secondes
            self.update_msg_id = self.root.after(500, self.update_chat)
    
    def afficher_page_1(self):
        self.page2.pack_forget()
        self.page1.pack()

    def afficher_page_2(self):
        self.page1.pack_forget()
        self.page2.pack()
    
    def deconnexion(self):
        message = ["deconnexion", self.pseudo.get()]
        message_json = json.dumps(message)

        self.client_socket.sendto(message_json.encode(), (self.server_ip, self.server_port))
        response, _ = self.client_socket.recvfrom(1024)
        print("Dans connexion, réponse du serveur :", response.decode())
        self.stop_requesting()
        self.afficher_page_1()
        # self.client_socket.close()
    
    def on_validate(self, P):
        # Limiter à 10 caractères
        return len(P) <= 10
    
    def run(self):
        self.read_server_info_from_file()
        self.root = tk.Tk()
        self.root.geometry("600x600")
        self.root.title("Client UDP")

        # Création des pages
        self.page1 = tk.Frame(self.root)
        self.page2 = tk.Frame(self.root)
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
        self.message2 = tk.StringVar()

        #----------Création et config widgets
        self.chat_display = tk.Text(self.page2, height=25, width=50, state=tk.DISABLED)
        self.validate_cmd = self.page2.register(self.on_validate)
        self.entry_msg = tk.Entry(self.page2, textvariable=self.message2, validate="key", validatecommand=(self.validate_cmd, "%P"))
        self.btn_envoyer = tk.Button(self.page2, text="Envoyer", command=lambda:[self.send_msg()])
        self.btn_retour = tk.Button(self.page2, text="Déconnexion", command=lambda:[self.deconnexion()])
        
        #----------Pack widget
        tk.Label(self.page2, text="Page 2").pack()
        self.chat_display.pack()
        self.entry_msg.pack()
        self.btn_envoyer.pack()
        self.btn_retour.pack()



        self.root.mainloop()

udp_client = UDPClient()
udp_client.run()
