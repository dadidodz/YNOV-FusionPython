import socket
import json

SERVER_HOST = '10.34.0.248'
SERVER_PORT = 12345

def send_message(message):

    message = f"Pseudo: {pseudo}"
    client_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    client_socket.sendto(message.encode(), (SERVER_HOST, SERVER_PORT))
    response, _ = client_socket.recvfrom(1024)
    print("Réponse du serveur:", response.decode())
    client_socket.close()

def connexion(pseudo):

    #Création d'un tableau avec un booléen True et le pseudo
    #que le joueur a renseigné
    tab = ["connexion", pseudo]
    tab_json = json.dumps(tab)

    client_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    client_socket.sendto(tab_json.encode(), (SERVER_HOST, SERVER_PORT))
    response, _ = client_socket.recvfrom(1024)
    print("Réponse du serveur:", response.decode())
    client_socket.close()

def deconnexion(pseudo):

    #Création d'un tableau avec un booléen True et le pseudo
    #que le joueur a renseigné
    tab = ["deconnexion", pseudo]
    tab_json = json.dumps(tab)

    client_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    client_socket.sendto(tab_json.encode(), (SERVER_HOST, SERVER_PORT))
    response, _ = client_socket.recvfrom(1024)
    print("Réponse du serveur:", response.decode())
    client_socket.close()