# -*- coding: utf-8 -*-

import socket

# Paramètres du serveur
     # Port du serveur

def hostScan():
    SERVER_HOST = '10.34.0.248'  # Adresse IP du serveur
    SERVER_PORT = 12345   
    message = "Bonjour, serveur !"
    client_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    client_socket.sendto(message.encode(), (SERVER_HOST, SERVER_PORT))
    response, _ = client_socket.recvfrom(1024)
    print("Réponse du serveur:", response.decode())
    client_socket.close()

   
# 