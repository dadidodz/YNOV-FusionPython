import socket
import threading
import sqlite3
import time
import json
import random
from chat import Chat
from morpionServeur import MorpionServeur

# A ajouter :   date à laquelle les joueurs rejoingnent la file d'attente
#               information sur à qui est le tour (dans le chat par exemple)
#               lien avec la base de données
# ip ynov dorian = '10.34.0.248'
# ip dorian apaprt = '192.168.1.45'

class UDPServer:
    def __init__(self, server_ip=None, server_port=None):
        self.server_ip = server_ip
        self.server_port = server_port
        self.read_server_info_from_file()
        
        self.clients = {} # Exemple format : ('192.168.1.100', 12345): [dorian, 1000, 0, None, 1647831000.0]
        self.queue = []
        self.parties = {} # Exemple format : 1: Partie
        self.server_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.server_socket.bind((self.server_ip, self.server_port))
        self.chat = Chat()
        self.is_running = True  # Condition d'arrêt

        
        print(f"Serveur UDP en écoute sur {self.server_ip}:{self.server_port}")
    
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

    def receive_messages(self):
        while self.is_running:
            try:
                self.server_socket.settimeout(1)
                connection = sqlite3.connect("fusion.sqlite")
                cursor = connection.cursor()
                message_json, client_address = self.server_socket.recvfrom(1024)
                if message_json:
                    message = json.loads(message_json.decode())
                    match message[0]:
                        case "alive":
                            self.clients[client_address][4] = time.time()
                            self.server_socket.sendto("Vous êtes toujours connecté".encode('utf-8'), client_address)
                            print(f"Message reçu de {client_address}: {message_json.decode()}")
                        
                        case "connection":
                            
                            sql = '''
                            SELECT 1
                            FROM Joueur
                            WHERE pseudo = ?
                            LIMIT 1
                            '''
                            pseudo_client = message[1]
                            cursor.execute(sql, (pseudo_client,))
                            result = cursor.fetchone()
                            if result:
                                print(f"Le joueur {message[1]} existe dans la base de données.")
                                sql = '''
                                UPDATE Joueur
                                SET IP = ?, Port = ?, Connecter = ?
                                WHERE Pseudo = ?
                                '''
                                data = (client_address[0], client_address[1], 1, message[1])
                                cursor.execute(sql, data)
                                connection.commit()

                            else:
                                print(f"Le joueur {message[1]} est un nouvel utilisateur")
                                sql = '''
                                INSERT INTO Joueur (Pseudo, Mot_de_passe, IP, Port, Connecter, MMR, En_attente, Id_partie)
                                VALUES (?, ?, ?, ?, ?, ?, ?, ?)
                                '''
                                data = (message[1], None, client_address[0], client_address[1], 1, 1000, 0, None)
                                cursor.execute(sql, data)
                                connection.commit()
                                connection.close()
                            
                            infos = [message[1], 1000, 0, None, time.time()]
                            self.clients[client_address] = infos
                            self.server_socket.sendto(f"{self.clients[client_address][0]}".encode('utf-8'), client_address)

                        case "chat":
                            print(f"Dans chat {client_address} Pseudo : {self.clients[client_address][0]}")
                            self.parties[self.clients[client_address][3]].chat.add_message(self.clients[client_address][0], message[1])

                        case "upd_chat":
                            if self.clients[client_address][3] in self.parties:
                                if self.parties[self.clients[client_address][3]].chat.last_updated > message[1]: #self.chat.last_updated > message[1]
                                    messages = self.parties[self.clients[client_address][3]].chat.get_messages_after_time(message[1])
                                    # messages = self.chat.get_messages_after_time(message[1])
                                    reponse = ["new_msg", messages]
                                    reponse_json = json.dumps(reponse)
                                    self.server_socket.sendto(reponse_json.encode(), client_address)
                                else:
                                    reponse = ["ras"]
                                    reponse_json = json.dumps(reponse)
                                    self.server_socket.sendto(reponse_json.encode(), client_address)
                            else:
                                reponse = ["ras"]
                                reponse_json = json.dumps(reponse)
                                self.server_socket.sendto(reponse_json.encode(), client_address)
                    
                        case "recherche partie":
                            self.clients[client_address][2] = 1
                            reponse = ["recherche partie", "Vous etes en recherche de partie"]
                            reponse_json = json.dumps(reponse)
                            self.server_socket.sendto(reponse_json.encode(), client_address)
                        
                        case "quitter file attente":
                            self.clients[client_address][2] = 0
                            if client_address in self.queue:
                                self.queue.remove(client_address)
                            print(f"Retrait du joueur {self.clients[client_address][0]} de la file d'attente ({self.clients[client_address]})")
                            reponse = ["retrait file attente"]
                            reponse_json = json.dumps(reponse)
                            self.server_socket.sendto(reponse_json.encode(), client_address)

                        case "partie trouvee":
                            if self.clients[client_address][3] != None :
                                reponse = ["Oui"]
                                reponse_json = json.dumps(reponse)
                                self.server_socket.sendto(reponse_json.encode(), client_address)
                            else:
                                reponse = ["Non"]
                                reponse_json = json.dumps(reponse)
                                self.server_socket.sendto(reponse_json.encode(), client_address)
                        
                        case "maj partie":
                            if self.clients[client_address][3] not in self.parties:
                                reponse = ["partie_lost"]
                                reponse_json = json.dumps(reponse)
                                self.server_socket.sendto(reponse_json.encode(), client_address)
                                self.clients[client_address][3] = None
                            else:
                                if self.parties[self.clients[client_address][3]].temps_derniere_action > message[1]:
                                    actions = self.parties[self.clients[client_address][3]].get_actions_after_time(message[1])
                                    print(actions)
                                    if actions[len(actions)-1][3] is True:
                                        # print(f"Le joueur {actions[len(actions)-1][4]} gagne la partie, il gagne du mmr")

                                        if self.clients[client_address][0] == actions[len(actions)-1][4]:
                                            self.clients[client_address][1] = self.clients[client_address][1] + 5
                                            print(f"MMR de {self.clients[client_address][0]} : {self.clients[client_address][1]}")
                                        
                                        if self.clients[client_address][0] == actions[len(actions)-1][5]:
                                            self.clients[client_address][1] = self.clients[client_address][1] - 5
                                            print(f"MMR de {self.clients[client_address][0]} : {self.clients[client_address][1]}")

                                    reponse = ["nouvelle action", actions]
                                    reponse_json = json.dumps(reponse)
                                    self.server_socket.sendto(reponse_json.encode(), client_address)
                                else:
                                    reponse = ["zero nouvelle action"]
                                    reponse_json = json.dumps(reponse)
                                    self.server_socket.sendto(reponse_json.encode(), client_address)
                        
                        case "jouer ici":
                            self.parties[self.clients[client_address][3]].jouer(message[1], message[2], self.clients[client_address][0]) # row, col, addr_joueur,)
                        
                        case "quitter partie":
                            reponse = ["partie quittee"]
                            reponse_json = json.dumps(reponse)
                            self.server_socket.sendto(reponse_json.encode(), client_address)
                            print(f"Nombre de parties : {len(self.parties)}")
                            del self.parties[self.clients[client_address][3]]
                            self.clients[client_address][3] = None
                            print(f"Nombre de parties : {len(self.parties)}")

                        case "deconnexion":
                            del self.clients[client_address]
                            if client_address in self.queue:
                                self.queue.remove(client_address)
                            self.server_socket.sendto(f"Pseudo : {message[1]}, vous êtes déconnecté.".encode('utf-8'), client_address)
                            print(f"Client {client_address} supprimé pour déconnexion.")
                        
                        case _:
                            print(f"Message {message[0]} non géré ")
            except socket.timeout:
                continue
            except Exception as e:
                print(f"Erreur lors de la réception du message : {e}")

    def remove_inactive_clients(self):
        while self.is_running:
            try:
                # Supprimer les clients qui n'ont pas envoyé de message depuis plus de 30 secondes
                current_time = time.time()
                inactive_clients = [address for address, values in self.clients.items() if current_time - values[4] > 15]
                for address in inactive_clients:
                    
                    if address in self.queue:
                        self.queue.remove(address)
                    
                    if self.clients[address][3] in self.parties :
                        del self.parties[self.clients[address][3]]
                    
                    del self.clients[address]

                    print(f"Client {address} supprimé pour inactivité.")
                time.sleep(1)
            except Exception as e:
                print(f"Erreur lors de la suppression des clients inactifs : {e}")
    
    def update_queue(self):
        while self.is_running:
            for client_address, values in self.clients.items(): #client_address = key; values = values
                if values[2] == 1:
                    if not client_address in self.queue:
                        self.queue.append(client_address)
                        print(f"Joueur {self.clients[client_address][0]} a été ajouté à la file d'attente")
                ## Inutile si on retire correctement les joueurs quand ils ne recherchent plus une partie
                ## ou bien s'ils sont déjà dans une partie
                else:
                    # print("Retrait de la file d'attente")
                    if client_address in self.queue:
                        self.queue.remove(client_address)
                        print(f"Joueur {self.clients[client_address][0]} a été retiré de la file d'attente")

            print(f"Nombre de joueurs dans la file d'attente {len(self.queue)}")
            self.find_matching_players()
            time.sleep(1)
    
    def find_matching_players(self):
        # Parcourir les clients pour comparer les MMR
        for client_address in self.queue:
            # Parcourir à nouveau les clients pour comparer les MMR avec les autres clients
            for other_client_address in self.queue:
                # Vérifier si les adresses sont différentes et si les MMR sont égaux
                diff_mmr = abs(self.clients[client_address][1] - self.clients[other_client_address][1])
                if client_address != other_client_address and self.clients[client_address][0] != self.clients[other_client_address][0] and diff_mmr < 51: #self.clients[client_address][1] == self.clients[other_client_address][1]
                    # Ajouter les adresses des joueurs ayant le même MMR à la liste temporaire
                    id_partie = random.randint(999, 10000)
                    # partie = MorpionServeur(id_partie, client_address, other_client_address, self.clients[client_address][0], self.clients[other_client_address][0])
                    partie = MorpionServeur(id_partie, self.clients[client_address][0], self.clients[other_client_address][0])
                    self.parties[partie.id_partie] = partie
                    self.clients[client_address][3] = id_partie #self.clients[client_address][3] = partie.id_partie
                    self.clients[other_client_address][3] = id_partie #self.clients[other_client_address][3] = partie.id_partie
                    # Retire les deux joueurs qui viennent de trouver une partie de la liste d'attente
                    self.queue.remove(client_address)
                    self.queue.remove(other_client_address)
                    # Modifie le statut d'attente des deux joueurs pour dire qu'ils ne sont plus en attente d'une partie
                    self.clients[client_address][2] = 0
                    self.clients[other_client_address][2] = 0
                    print("Partie créée")
                else: 
                    print("Aucune partie créée")

    def start_server(self):
        # self.read_server_info_from_file()
        try:
            # Démarrer un thread pour recevoir les messages des clients
            threading.Thread(target=self.receive_messages).start()
            # Démarrer un thread pour supprimer les clients inactifs
            threading.Thread(target=self.remove_inactive_clients).start()
            threading.Thread(target=self.update_queue).start()
            # Garder le programme en cours d'exécution
            while self.is_running:
                time.sleep(1)
        
        except KeyboardInterrupt:
            self.stop_server()
    
    def stop_server(self):
        self.is_running = False
        self.server_socket.close()
        print("Serveur arrêté")


# Utilisation du serveur
if __name__ == "__main__":
    # server = UDPServer('10.34.0.248', 12345)
    # server = UDPServer('192.168.1.45', 12345)
    server = UDPServer()
    server.start_server()
