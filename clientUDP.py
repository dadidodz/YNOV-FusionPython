# UTILISER CE CLIENT

import socket
import tkinter as tk
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
                    self.next_page()
                    self.stay_connected()
                    self.update_chat()

            except Exception as e:
                print(f"Erreur lors de la connexion au serveur : {e}")
        else:
            self.input.delete(0, 'end')
    
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
            self.input2.delete(0, 'end')

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
    
    def next_page(self):
        self.page1.pack_forget()  # Masquer le cadre actuel
        self.page2.pack()
    
    def previous_page(self):
        self.page2.pack_forget()
        self.page1.pack()
    
    def deconnexion(self):
        message = ["deconnexion", self.pseudo.get()]
        message_json = json.dumps(message)

        self.client_socket.sendto(message_json.encode(), (self.server_ip, self.server_port))
        response, _ = self.client_socket.recvfrom(1024)
        print("Dans connexion, réponse du serveur :", response.decode())
        self.stop_requesting()
        self.previous_page()
        # self.client_socket.close()
    
    def on_validate(self, P):
        # Limiter à 10 caractères
        return len(P) <= 10

    def on_entry_click(self, event):
        if self.input.get() == self.placeholder:
            self.input.delete(0, "end")
            self.input.config(fg="black")

    def on_focus_out(self, event):
        if not self.input.get():
            self.input.insert(0, self.placeholder)
            self.input.config(fg="grey")
    
    def run(self):
        self.read_server_info_from_file()
        self.root = tk.Tk()
        self.root.geometry("600x600")
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

        self.placeholder = "Entrez votre pseudo ici"
        self.input = tk.Entry(self.page1, textvariable=self.pseudo, fg="grey")

        self.input.insert(0, self.placeholder)
        self.input.bind("<FocusIn>", self.on_entry_click)
        self.input.bind("<FocusOut>", self.on_focus_out)
        self.input.pack()

        self.scan_button1 = tk.Button(self.page1, text="Connexion", command=lambda:[self.connexion()])
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
        self.label_2.pack()

        # Zone de texte pour afficher les messages
        self.chat_display = tk.Text(self.page2, height=25, width=50, state=tk.DISABLED)
        self.chat_display.pack()

        self.message2 = tk.StringVar()
        self.validate_cmd = self.page2.register(self.on_validate)
        self.input2 = tk.Entry(self.page2, textvariable=self.message2, validate="key", validatecommand=(self.validate_cmd, "%P"))
        self.input2.pack()

        self.btn_envoi_msg = tk.Button(self.page2, text="Envoyer", command=lambda:[self.send_msg()])  # Masquer le cadre suivant et afficher le cadre actuel
        self.btn_envoi_msg.pack()

        self.bouton_retour = tk.Button(self.page2, text="Déconnexion", command=lambda:[self.deconnexion()])  # Masquer le cadre suivant et afficher le cadre actuel
        self.bouton_retour.pack()
        
        # self.start_sending_messages()
        self.root.mainloop()

udp_client = UDPClient()
udp_client.run()
