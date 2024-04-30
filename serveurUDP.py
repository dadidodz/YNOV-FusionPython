# coding: utf-8

import socket
import sqlite3
import json
import threading

connection = sqlite3.connect("fusion.sqlite")

cursor = connection.cursor()

# Serveur()
# Paramètres du serveur
HOST = '10.34.0.248'  # Adresse IP du serveur
PORT = 12345        # Port sur lequel le serveur écoute

# Création d'un socket UDP
server_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

# Lier le socket au port et à l'adresse IP
server_socket.bind((HOST, PORT))

# print("Serveur UDP en attente de messages...")

# def check_connexion():
#     print("ici")
#     cursor.execute(f"SELECT DISTINCT IP FROM joueur")
#     ips = cursor.fetchone()[0]
#     for ip in ips:
#         ip_tuple = (ip, PORT)
#         server_socket.sendto("Dans reconnexion".encode('utf-8'), ip_tuple)
#         response, _ = server_socket.recvfrom(1024)
#         if response == None:
#             print(f"Le joueur n'est plus connecté")

#     threading.Timer(10, check_connexion).start()

while True:
    # Recevoir les données du client
    data, addr = server_socket.recvfrom(1024)
    tab_received = json.loads(data.decode())

    # check_connexion()

    for tab in tab_received:
        print("Message reçu du client:", tab)
    
    if (data):
        if tab_received[0] == "connexion":
            cursor.execute(f"SELECT COUNT(*) FROM joueur WHERE pseudo = '{tab_received[1]}'")
            pseudos = cursor.fetchone()[0]
            if pseudos:
                # print(addr)
                server_socket.sendto("Joueur connecté".encode('utf-8'), addr)
                # cursor.execute(f"SELECT COUNT(*) FROM joueur WHERE pseudo = '{tab_received[1]}'")
            else:
                cursor.execute(f"INSERT INTO Joueur(Pseudo, IP, MMR, Mot_de_passe, EnAttente) VALUES ('{tab_received[1]}', '{addr[0]}', 1000, NULL, 1)")
                connection.commit()
                server_socket.sendto("Joueur ajouté à la base de donnée".encode('utf-8'), addr)
        
        if tab_received[0] == "reconnexion":
            # Répondre au client
            server_socket.sendto("Dans reconnexion".encode('utf-8'), addr)
        
        # Afficher les données reçues et l'adresse du client
        print(f"Reçu depuis {addr}: {data.decode()}")

    server_socket.sendto("Dans reconnexion".encode('utf-8'), addr)
        # cursor.execute(f"INSERT INTO HistoriqueMessage(Id_Joueur, Id_Partie, Contenu, DateHeureEnvoi) VALUES (1, 1, '{data.decode()}', '2024-04-11 17:29:30')")
        # cursor.execute(f"INSERT INTO HistoriqueMessage(Contenu) VALUES ('{data.decode()}')")
        # print(cursor.execute(f"INSERT INTO HistoriqueMessage(Contenu) VALUES ('{data.decode()}')"))
        # connection.commit()

    

