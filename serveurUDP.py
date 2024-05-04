import socket
import threading
import time
import json
import random
from chat import Chat

class UDPServer:
    def __init__(self, host, port):
        self.SERVER_HOST = host
        self.SERVER_PORT = port
        self.clients = {} # Exemple format : ('192.168.1.100', 12345): [dorian, 1000, 0, None, 1647831000.0]
        self.liste_attente = []
        self.parties = {} # Exemple format : 1: Partie
        self.server_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.server_socket.bind((self.SERVER_HOST, self.SERVER_PORT))
        self.chat = Chat()
        print(f"Serveur UDP en écoute sur {self.SERVER_HOST}:{self.SERVER_PORT}")

    def receive_messages(self):
        while True:
            try:
                data, client_address = self.server_socket.recvfrom(1024)
                message_received = json.loads(data.decode())
                if data:
                    if message_received[0] == "alive":
                        # Mettre à jour le timestamp du client
                        self.clients[client_address][4] = time.time()
                        self.server_socket.sendto("Vous êtes toujours connecté".encode('utf-8'), client_address)
                        print(f"Message reçu de {client_address}: {data.decode()}")

                    if message_received[0] == "connexion":
                        infos = [message_received[1], message_received[2], 0, None, time.time()]
                        self.clients[client_address] = infos
                        self.server_socket.sendto(f"Joueur {self.clients[client_address][0]} est connecté.".encode('utf-8'), client_address)
                    
                    if message_received[0] == "chat":
                        print(f"Dans chat {client_address} Pseudo : {self.clients[client_address][0]}")
                        self.chat.add_message(self.clients[client_address][0], message_received[1])

                    if message_received[0] == "upd_chat":
                        if self.chat.last_updated > message_received[1]:
                            messages = self.chat.get_messages_after_time(message_received[1])
                            reponse = ["new_msg", messages]
                            reponse_json = json.dumps(reponse)
                            self.server_socket.sendto(reponse_json.encode(), client_address)
                        else:
                            reponse = ["ras"]
                            reponse_json = json.dumps(reponse)
                            self.server_socket.sendto(reponse_json.encode(), client_address)
                    
                    if message_received[0] == "recherche partie":
                        self.clients[client_address][2] = 1
                        reponse = ["recherche partie", "Vous etes en recherche de partie"]
                        reponse_json = json.dumps(reponse)
                        self.server_socket.sendto(reponse_json.encode(), client_address)
                    
                    if message_received[0] == "partie trouvee":
                        # print(f"{}{self.clients[client_address][3]}")
                        if self.clients[client_address][3] != None :
                            reponse = ["Oui"]
                            reponse_json = json.dumps(reponse)
                            self.server_socket.sendto(reponse_json.encode(), client_address)
                        else:
                            reponse = ["Non"]
                            reponse_json = json.dumps(reponse)
                            self.server_socket.sendto(reponse_json.encode(), client_address)

                    if message_received[0] == "deconnexion":
                        del self.clients[client_address]
                        if client_address in self.liste_attente:
                            self.liste_attente.remove(client_address)
                        self.server_socket.sendto(f"Pseudo : {message_received[1]}, vous êtes déconnecté.".encode('utf-8'), client_address)
                        print(f"Client {client_address} supprimé pour déconnexion.")

            except Exception as e:
                print(f"Erreur lors de la réception du message : {e}")

    def remove_inactive_clients(self):
        while True:
            try:
                # Supprimer les clients qui n'ont pas envoyé de message depuis plus de 30 secondes
                current_time = time.time()
                inactive_clients = [address for address, values in self.clients.items() if current_time - values[4] > 10]
                for address in inactive_clients:
                    del self.clients[address]
                    if address in self.liste_attente:
                        self.liste_attente.remove(address)
                    print(f"Client {address} supprimé pour inactivité.")
                time.sleep(10)
            except Exception as e:
                print(f"Erreur lors de la suppression des clients inactifs : {e}")
    
    def maj_file_dattente(self):
        while True:
            for adresse_joueur, values in self.clients.items():
                if values[2] == 1:
                    if not adresse_joueur in self.liste_attente:
                        self.liste_attente.append(adresse_joueur)
                        print(f"Joueur {self.clients[adresse_joueur][0]} a été ajouté à la file d'attente")
                ## Inutile si on retire correctement les joueurs quand ils ne recherchent plus une partie
                ## ou bien s'ils sont déjà dans une partie
                else:
                    if adresse_joueur in self.liste_attente:
                        self.liste_attente.remove(adresse_joueur)
                        print(f"Joueur {self.clients[adresse_joueur][0]} a été retiré de la file d'attente")

            print(f"Nombre de joueurs dans la file d'attente {len(self.liste_attente)}")
            self.find_matching_players()
            time.sleep(10)
    
    def find_matching_players(self):
        # Parcourir les clients pour comparer les MMR
        for client_address in self.liste_attente:
            # Parcourir à nouveau les clients pour comparer les MMR avec les autres clients
            for other_client_address in self.liste_attente:
                # Vérifier si les adresses sont différentes et si les MMR sont égaux
                if client_address != other_client_address and self.clients[client_address][0] != self.clients[other_client_address][0] and self.clients[client_address][1] == self.clients[other_client_address][1]:
                    # Ajouter les adresses des joueurs ayant le même MMR à la liste temporaire
                    id_partie = random.randint(999, 10000)
                    # partie = Morpion(id_partie, client_address, other_client_address)
                    # self.parties[partie.id_partie] = partie
                    self.clients[client_address][3] = id_partie #self.clients[client_address][3] = partie.id_partie
                    self.clients[other_client_address][3] = id_partie #self.clients[other_client_address][3] = partie.id_partie
                    # Retire les deux joueurs qui viennent de trouver une partie de la liste d'attente
                    self.liste_attente.remove(client_address)
                    self.liste_attente.remove(other_client_address)
                    # Modifie le statut d'attente des deux joueurs pour dire qu'ils ne sont plus en attente d'une partie
                    self.clients[client_address][2] = 0
                    self.clients[other_client_address][2] = 0
                    print("Partie créée")
                else: 
                    print("Aucune partie créée")

    def start_server(self):
        # Démarrer un thread pour recevoir les messages des clients
        threading.Thread(target=self.receive_messages).start()
        # Démarrer un thread pour supprimer les clients inactifs
        threading.Thread(target=self.remove_inactive_clients).start()
        threading.Thread(target=self.maj_file_dattente).start()
        # Garder le programme en cours d'exécution
        while True:
            time.sleep(1)

# Utilisation du serveur
if __name__ == "__main__":
    # server = UDPServer('10.34.0.248', 12345)
    server = UDPServer('192.168.1.45', 12345)
    server.start_server()
