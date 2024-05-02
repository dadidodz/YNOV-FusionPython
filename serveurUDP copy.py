# UTILISER CE SERVEUR
import socket
import threading
import time
import json

# Paramètres du serveur
SERVER_HOST = '10.34.0.248' # Adresse IP du serveur (0.0.0.0 signifie toutes les interfaces)
SERVER_PORT = 12345        # Port sur lequel le serveur écoute

# Dictionnaire pour stocker les adresses IP des clients connectés
clients = {}

# Fonction pour recevoir les messages des clients
def receive_messages(server_socket):
    while True:
        try:
            data, client_address = server_socket.recvfrom(1024)
            message_received = json.loads(data.decode())
            if data :
                if message_received[0] == "alive":
                    # Mettre à jour le timestamp du client
                    clients[client_address] = time.time()
                    server_socket.sendto("Vous êtes toujours connecté".encode('utf-8'), client_address)
                    print(f"Message reçu de {client_address}: {data.decode()}") 
                
                if message_received[0] == "connexion":
                    server_socket.sendto(f"Pseudo : {message_received[1]}, vous êtes connecté.".encode('utf-8'), client_address)
                
                if message_received[0] == "deconnexion":
                    del clients[client_address]
                    server_socket.sendto(f"Pseudo : {message_received[1]}, vous êtes déconnecté.".encode('utf-8'), client_address)
                    print(f"Client {client_address} supprimé pour déconnexion.")

        except Exception as e:
            print(f"Erreur lors de la réception du message : {e}")

# Fonction pour supprimer les clients inactifs
def remove_inactive_clients():
    while True:
        try:
            # Supprimer les clients qui n'ont pas envoyé de message depuis plus de 30 secondes
            current_time = time.time()
            inactive_clients = [address for address, timestamp in clients.items() if current_time - timestamp > 30]
            for address in inactive_clients:
                del clients[address]
                print(f"Client {address} supprimé pour inactivité.")
            time.sleep(30)
        except Exception as e:
            print(f"Erreur lors de la suppression des clients inactifs : {e}")

# Création d'un socket UDP pour le serveur
server_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
server_socket.bind((SERVER_HOST, SERVER_PORT))

print(f"Serveur UDP en écoute sur {SERVER_HOST}:{SERVER_PORT}")

# Démarrer un thread pour recevoir les messages des clients
threading.Thread(target=receive_messages, args=(server_socket,)).start()

# Démarrer un thread pour supprimer les clients inactifs
threading.Thread(target=remove_inactive_clients).start()

# Garder le programme en cours d'exécution
while True:
    time.sleep(1)
