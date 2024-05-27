import socket
import threading
import sqlite3
import time
import json
import random
import bcrypt
import string
import os
# from chat import Chat
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
        # self.connected_clients = {}
        self.queue = []
        self.parties = {} # Exemple format : 1: Partie
        self.server_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.server_socket.bind((self.server_ip, self.server_port))
        # self.chat = Chat()
        self.is_running = True  # Condition d'arrêt

        print(f"Serveur UDP en écoute sur {self.server_ip}:{self.server_port}")
    
    def read_server_info_from_file(self, filename='../config.txt'):
        try:
            filepath = os.path.join(os.path.dirname(__file__), filename)
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
                        case "connection":
                            # pseudo_client = message[1]

                            already_connected = any(message[1] in valeurs for valeurs in self.clients.values())
                            if already_connected:
                                reponse = ["already_connected"]
                                reponse_json = json.dumps(reponse)
                                self.server_socket.sendto(reponse_json.encode(), client_address)
                            else:
                                password_bytes = message[2].encode('utf-8')
                                password_hashed = bcrypt.hashpw(password_bytes, bcrypt.gensalt())

                                sql = '''
                                SELECT 1
                                FROM Joueur
                                WHERE pseudo = ?
                                LIMIT 1
                                '''
                                cursor.execute(sql, (message[1],))
                                result = cursor.fetchone()
                                if result:
                                    print(f"Le joueur {message[1]} existe dans la base de données.")
                                    cursor.execute("SELECT Mot_de_passe FROM Joueur WHERE Pseudo = ?", (message[1],))
                                    result_2 = cursor.fetchone()
                                    if result_2 and bcrypt.checkpw(password_bytes, result_2[0]):
                                        # response = "ACCEPTED"
                                        sql = '''
                                        UPDATE Joueur
                                        SET IP = ?, Port = ?
                                        WHERE Pseudo = ?
                                        '''
                                        data = (client_address[0], client_address[1], message[1])

                                        cursor.execute(sql, data)
                                        connection.commit()
                                            
                                        infos = [message[1], 1000, 0, None, time.time()]
                                        self.clients[client_address] = infos

                                        reponse = ["connected"]
                                        reponse_json = json.dumps(reponse)
                                        self.server_socket.sendto(reponse_json.encode(), client_address)
                                    else:
                                        reponse = ["rejected"]
                                        reponse_json = json.dumps(reponse)
                                        self.server_socket.sendto(reponse_json.encode(), client_address)
                                    
                                    

                                else:
                                    print(f"Le joueur {message[1]} est un nouvel utilisateur")
                                    sql = '''
                                    INSERT INTO Joueur (Pseudo, Mot_de_passe, IP, Port, MMR)
                                    VALUES (?, ?, ?, ?, ?)
                                    '''
    
                                    data = (message[1], password_hashed, client_address[0], client_address[1], 1000)
                                    cursor.execute(sql, data)
                                    connection.commit()
                                    infos = [message[1], 1000, 0, None, time.time()]
                                    self.clients[client_address] = infos

                                    reponse = ["connected"]
                                    reponse_json = json.dumps(reponse)
                                    self.server_socket.sendto(reponse_json.encode(), client_address)
                                
                                password_bytes = None
                                password_hashed = None

                        case "alive":
                            self.clients[client_address][4] = time.time()
                            self.server_socket.sendto("Vous êtes toujours connecté".encode('utf-8'), client_address)
                            print(f"Message reçu de {client_address}: {message_json.decode()}")

                        case "recherche partie":
                            sql = '''
                            SELECT MMR
                            FROM Joueur
                            WHERE pseudo = ?
                            '''

                            cursor.execute(sql, (self.clients[client_address][0],))
                            mmr_client = cursor.fetchone()[0]
                            self.clients[client_address][1] = mmr_client
                            print(f"MMR de {self.clients[client_address][0]} est : mmr_client = {mmr_client}, clients[clients_address] = {self.clients[client_address][1]}")
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
                            if self.clients[client_address][3] != None : # est ce que le client x a trouvé une partie 
                                
                                reponse = ["Oui", self.parties[self.clients[client_address][3]].current_player, self.parties[self.clients[client_address][3]].joueurs[self.clients[client_address][0]]] # recupéré la personne qui a trouvé la partie en lui attribuant la croix ou le rond
                                reponse_json = json.dumps(reponse)
                                self.server_socket.sendto(reponse_json.encode(), client_address)
                                
                            else:
                                reponse = ["Non"]
                                reponse_json = json.dumps(reponse)
                                self.server_socket.sendto(reponse_json.encode(), client_address)
                        
                        case "jouer ici":
                            self.parties[self.clients[client_address][3]].jouer(message[1], message[2], self.clients[client_address][0]) # row, col, addr_joueur,)

                        case "maj partie":
                            if self.clients[client_address][3] not in self.parties:

                                reponse = ["partie_lost"]
                                reponse_json = json.dumps(reponse)
                                self.server_socket.sendto(reponse_json.encode(), client_address)
                                self.clients[client_address][3] = None
                                
                            else:
                                if self.parties[self.clients[client_address][3]].temps_derniere_action > message[1]:
                                    currentPlayer = self.parties[self.clients[client_address][3]].current_player 
                                    actions = self.parties[self.clients[client_address][3]].get_actions_after_time(message[1])
                                    print(actions)
                                    if actions[len(actions)-1][3] is True:
                                        new_mmr = 1000
                                        if self.clients[client_address][0] == actions[len(actions)-1][4]:
                                            new_mmr = self.clients[client_address][1] + 5
                                        elif self.clients[client_address][0] == actions[len(actions)-1][5]:
                                            new_mmr = self.clients[client_address][1] - 5
                                        else:
                                            new_mmr = self.clients[client_address][1]
                                        
                                        print(new_mmr)
                                        sql = '''
                                        UPDATE Joueur
                                        SET MMR = ?
                                        WHERE Pseudo = ?
                                        '''
                                        data = (new_mmr, self.clients[client_address][0])
                                        cursor.execute(sql, data)
                                        connection.commit()

                                    reponse = ["nouvelle action", actions, currentPlayer]
                                    reponse_json = json.dumps(reponse)
                                    self.server_socket.sendto(reponse_json.encode(), client_address)
                                else:
                                    reponse = ["zero nouvelle action"]
                                    reponse_json = json.dumps(reponse)
                                    self.server_socket.sendto(reponse_json.encode(), client_address)

                        case "board":
                            board = self.parties[self.clients[client_address][3]].get_board()
                            reponse = ["full board", board]
                            reponse_json = json.dumps(reponse)
                            self.server_socket.sendto(reponse_json.encode(), client_address)

                        case "chat":
                            print(f"Dans chat {client_address} Pseudo : {self.clients[client_address][0]}")
                            self.parties[self.clients[client_address][3]].chat.add_message(self.clients[client_address][0], message[1])
                            sql = '''
                            INSERT INTO HistoriqueMessages (Pseudo, Id_Partie, Contenu)
                            VALUES (?, ?, ?)
                            '''
                            data = (self.clients[client_address][0], self.clients[client_address][3], message[1])

                            cursor.execute(sql, data)
                            connection.commit()

                        case "upd_chat":
                            if self.clients[client_address][3] in self.parties:
                                if self.parties[self.clients[client_address][3]].chat.last_updated > message[1]: #self.chat.last_updated > message[1]
                                    messages = self.parties[self.clients[client_address][3]].chat.get_messages_after_time(message[1])
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
                    

                connection.close()
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
                mmr_p1 = self.clients[client_address][1]
                mmr_p2 = self.clients[other_client_address][1]
                diff_mmr = abs(mmr_p1 - mmr_p2)
                if client_address != other_client_address and self.clients[client_address][0] != self.clients[other_client_address][0] and diff_mmr < 51: #self.clients[client_address][1] == self.clients[other_client_address][1]
                    # Ajouter les adresses des joueurs ayant le même MMR à la liste temporaire
                    
                    generated_id_partie = self.generate_id_unique()
                    # id_partie = random.randint(999, 10000)
                    partie = MorpionServeur(generated_id_partie, self.clients[client_address][0], self.clients[other_client_address][0])
                    self.parties[partie.id_partie] = partie
                    self.clients[client_address][3] = generated_id_partie
                    self.clients[other_client_address][3] = generated_id_partie
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
    
    def generate_id_unique(self):
        connection = sqlite3.connect("fusion.sqlite")
        cursor = connection.cursor()
        while True:
            # Générer un identifiant aléatoire
            id_partie = ''.join(random.choices(string.ascii_letters + string.digits, k=8))
            print(type(id_partie))

            # Vérifier si l'identifiant existe déjà dans la base de données
            cursor.execute("SELECT Id_Partie FROM HistoriqueParties WHERE Id_Partie = ?", (id_partie,))
            result = cursor.fetchone()

            # Si l'identifiant n'existe pas, retourner l'identifiant généré
            if not result:
                connection.close()
                return id_partie

    
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
