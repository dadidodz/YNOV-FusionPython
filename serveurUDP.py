# coding: utf-8

import socket
import sqlite3

connection = sqlite3.connect("fusion.sqlite")

cursor = connection.cursor()


# Paramètres du serveur
HOST = '10.34.0.248'  # Adresse IP du serveur
PORT = 12345        # Port sur lequel le serveur écoute

# Création d'un socket UDP
server_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

# Lier le socket au port et à l'adresse IP
server_socket.bind((HOST, PORT))

print("Serveur UDP en attente de messages...")

while True:
    # Recevoir les données du client
    data, addr = server_socket.recvfrom(1024)
    print("Message reçu du client:", data.decode())
    if (data):
        cursor.execute(f"INSERT INTO HistoriqueMessage(Id_Joueur, Id_Partie, Contenu, DateHeureEnvoi) VALUES (1, 1, '{data.decode()}', '2024-04-11 17:29:30')")
        # cursor.execute(f"INSERT INTO HistoriqueMessage(Contenu) VALUES ('{data.decode()}')")
        # print(cursor.execute(f"INSERT INTO HistoriqueMessage(Contenu) VALUES ('{data.decode()}')"))
        connection.commit()
        



    # Répondre au client
    server_socket.sendto("Message reçu par le serveur.".encode('utf-8'), addr)

