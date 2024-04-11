# -*- coding: utf-8 -*-

import socket

# Paramètres du serveur
SERVER_HOST = '10.34.0.248'  # Adresse IP du serveur
SERVER_PORT = 12345        # Port du serveur

# Message à envoyer
message = "Bonjour, serveur !"

# Création d'un socket UDP
client_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

# Envoi du message au serveur
client_socket.sendto(message.encode(), (SERVER_HOST, SERVER_PORT))

# Recevoir la réponse du serveur
response, _ = client_socket.recvfrom(1024)
print("Réponse du serveur:", response.decode())

# Fermer le socket client
client_socket.close()
