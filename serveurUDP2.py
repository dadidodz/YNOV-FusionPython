import socket
import sqlite3
import json

class ServeurUDP:
    def __init__(self, host, port):
        self.host = host
        self.port = port
        self.connection = sqlite3.connect("fusion.sqlite")
        self.cursor = self.connection.cursor()
        self.server_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.server_socket.bind((self.host, self.port))
    
    def recevoir_messages(self):
        print("Serveur UDP en attente de messages...")
        while True:
            data, addr = self.server_socket.recvfrom(1024)
            tab_received = json.loads(data.decode())

            for tab in tab_received:
                print("Message reçu du client:", tab)
            
            if data:
                if tab_received[0] == "connexion":
                    self.gerer_connexion(addr, tab_received[1])
                elif tab_received[0] == "reconnexion":
                    self.repondre_reconnexion(addr)
                print(f"Reçu depuis {addr}: {data.decode()}")
    
    def gerer_connexion(self, addr, pseudo):
        self.cursor.execute(f"SELECT COUNT(*) FROM joueur WHERE pseudo = '{pseudo}'")
        resultat = self.cursor.fetchone()[0]
        if resultat:
            pass
        else:
            self.cursor.execute(f"INSERT INTO Joueur(Pseudo, IP, MMR, Mot_de_passe, EnAttente) VALUES ('{pseudo}', '{addr[0]}', 1000, NULL, 1)")
            self.connection.commit()
            self.server_socket.sendto("Joueur ajouté à la base de donnée".encode('utf-8'), addr)
    
    def repondre_reconnexion(self, addr):
        self.server_socket.sendto("Dans reconnexion".encode('utf-8'), addr)

# Utilisation de la classe ServeurUDP
if __name__ == "__main__":
    serveur = ServeurUDP('10.34.0.248', 12345)
    serveur.recevoir_messages()
