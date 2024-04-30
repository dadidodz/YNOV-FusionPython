# UTILISER CE CLIENT

import socket
import tkinter as tk

SERVER_IP = '10.34.0.248'  # Adresse IP du serveur
SERVER_PORT = 12345        # Port sur lequel le serveur écoute

class UDPClient:
    def __init__(self, server_ip, server_port):
        self.server_ip = server_ip
        self.server_port = server_port
        self.client_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    
    def send_keep_alive_message(self):
        try:
            # Envoyer un message au serveur pour indiquer que le client est toujours actif
            message = "Je suis toujours là !"
            self.client_socket.sendto(message.encode(), (self.server_ip, self.server_port))
            print("Message de présence envoyé au serveur.")
        except Exception as e:
            print(f"Erreur lors de l'envoi du message de présence : {e}")

    def start_sending_messages(self):
        self.send_keep_alive_message()
        # Planifier l'appel à la fonction toutes les 10 secondes
        self.root.after(10000, self.start_sending_messages)

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

        self.message = tk.StringVar()
        self.input = tk.Entry(self.page1, textvariable=self.message)
        self.input.pack()

        self.scan_button1 = tk.Button(self.page1, text="Connexion")
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
        self.bouton_retour = tk.Button(self.page2, text="Déconnexion")  # Masquer le cadre suivant et afficher le cadre actuel
        self.label_2.pack()
        self.bouton_retour.pack()

        # self.start_sending_messages()
        self.root.mainloop()

udp_client = UDPClient(SERVER_IP, SERVER_PORT)
udp_client.run()
