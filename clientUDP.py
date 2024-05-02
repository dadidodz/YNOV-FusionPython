# UTILISER CE CLIENT

import socket
import tkinter as tk
import json

SERVER_IP = '10.34.0.248'  # Adresse IP du serveur
SERVER_PORT = 12345        # Port sur lequel le serveur écoute

class UDPClient:
    def __init__(self, server_ip, server_port):
        self.server_ip = server_ip
        self.server_port = server_port
        self.client_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.keep_alive_active = True
        self.keep_alive_id = None
    
    def still_connected(self):
        try:
            # Envoyer un message au serveur pour indiquer que le client est toujours actif
            alive = ["alive"]
            alive_json = json.dumps(alive)
            
            self.client_socket.sendto(alive_json.encode(), (self.server_ip, self.server_port))
            print("Message de présence envoyé au serveur.")
            response, _ = self.client_socket.recvfrom(1024)
            print("Dans still_connected, réponse du serveur :", response.decode())
        except Exception as e:
            print(f"Erreur lors de l'envoi du message de présence : {e}")
        
        if self.keep_alive_active:
            # Planifier l'appel à la fonction toutes les 10 secondes
            self.keep_alive_id = self.root.after(10000, self.still_connected)
    
    def update_chat(self):
        try:
            # Envoyer un message au serveur pour indiquer que le client est toujours actif
            chat = ["chat"]
            chat_json = json.dumps(chat)
            
            self.client_socket.sendto(chat_json.encode(), (self.server_ip, self.server_port))
            print("Message de présence envoyé au serveur.")
            response, _ = self.client_socket.recvfrom(1024)
            print("Dans still_connected, réponse du serveur :", response.decode())
        except Exception as e:
            print(f"Erreur lors de l'envoi du message de présence : {e}")

    def connexion(self):
        self.message = ["connexion", self.pseudo.get()]
        self.message_json = json.dumps(self.message)

        self.client_socket.sendto(self.message_json.encode(), (self.server_ip, self.server_port))
        response, _ = self.client_socket.recvfrom(1024)
        print("Dans connexion, réponse du serveur :", response.decode())
        # client_socket.close()
        if response.decode():
            self.next_page()

    def next_page(self):
        self.page1.pack_forget()  # Masquer le cadre actuel
        self.page2.pack()
    
    def previous_page(self):
        self.page2.pack_forget()
        self.page1.pack()
    
    def stop_sending_messages(self):
        # Arrêter la planification des appels récurrents
        self.keep_alive_active = False
        # Annuler l'appel planifié
        if self.keep_alive_id:
            self.root.after_cancel(self.keep_alive_id)
            self.keep_alive_id = None
    
    def deconnexion(self):
        self.message = ["deconnexion", self.pseudo.get()]
        self.message_json = json.dumps(self.message)

        self.client_socket.sendto(self.message_json.encode(), (self.server_ip, self.server_port))
        response, _ = self.client_socket.recvfrom(1024)
        print("Dans connexion, réponse du serveur :", response.decode())
        self.stop_sending_messages()
        self.previous_page()
        # self.client_socket.close()
    
    def run(self):
        self.root = tk.Tk()
        self.root.geometry("330x330")
        self.root.title("Client UDP")
        


        # -------------- PAGE 1 --------------------
        # Création du premier cadre (page)
        self.page1 = tk.Frame(self.root)
        self.page1.pack()

        # Contenu du premier cadre
        self.label_1 = tk.Label(self.page1, text="Page 1")
        self.label_1.pack()

        self.label_2 = tk.Label(self.page1, text="Pseudo")
        self.label_2.pack()

        self.pseudo = tk.StringVar()
        self.input = tk.Entry(self.page1, textvariable=self.pseudo)
        self.input.pack()

        self.scan_button1 = tk.Button(self.page1, text="Connexion", command=lambda:[self.still_connected(), self.connexion()])
        self.scan_button1.config(width=20, height=2)
        self.scan_button1.pack()

        self.scan_button2 = tk.Button(self.page1, text="Quitter")
        self.scan_button2.config(width=20, height=2)
        self.scan_button2.pack()


        #-----------PAGE 2--------------
        # Création du deuxième cadre (page)
        self.page2 = tk.Frame(self.root)
        # Contenu du deuxième cadre (page)
        self.label_2 = tk.Label(self.page2, text="Page 2")
        # bouton_retour = tk.Button(page2, text="Déconnexion", command=lambda: page2.pack_forget() or page1.pack())  # Masquer le cadre suivant et afficher le cadre actuel
        self.bouton_retour = tk.Button(self.page2, text="Déconnexion", command=lambda:[self.deconnexion()])  # Masquer le cadre suivant et afficher le cadre actuel
        self.label_2.pack()
        self.bouton_retour.pack()

        # self.start_sending_messages()
        self.root.mainloop()

udp_client = UDPClient(SERVER_IP, SERVER_PORT)
udp_client.run()
