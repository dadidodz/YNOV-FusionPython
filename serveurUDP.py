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
    if (data){
        cursor.execute(f"INSERT INTO HistoriqueMessage VALUES (1, 1, {data.dacode()}, '2024-04-11 17:29:30')")
    }


    # Répondre au client
    server_socket.sendto("Message reçu par le serveur.".encode('utf-8'), addr)

