import socket
import threading
import sqlite3
import time
import json
import random
import bcrypt
import string
import os
from morpionServeur import MorpionServeur

class UDPServer:
    """
    Classe UDPServer

    Attributs : 
        server_ip (str) : Adresse IP du serveur
        server_port (int) : Port de communication du serveur
        client_socket (socket) : Socket de communication du serveur

        connected_clients (dict) : Stocke les clients actuellement connectés au serveur
        queue (list) : Stocke les joueurs en recherche d'une partie (file d'attente)
        is_running (bool) : Condition de marche du serveur
    """
    def __init__(self):
        self.server_ip = ""
        self.server_port = 0
        self.read_server_info_from_file()
        self.server_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.server_socket.bind((self.server_ip, self.server_port))

        self.connected_clients = {} # Exemple de format : ('192.168.1.100', 12345): [0: dorian (=pseudo(str)), 1: 1000 (=mmr(int)), 2: 0(=en_recherche(bool)), 
                                                                                    # 3: None (=id_partie(str)), 4: 1647831000.0 (=timestamp(float))]
        self.queue = [] # Exemple de format : [('192.168.1.75', 42105), ('192.168.1.100', 54236)]
        self.games = {} # Exemple format : "G55phai2": MorpionServeur()
        self.is_running = True  # Condition d'arrêt
        print(f"Serveur UDP en écoute sur {self.server_ip}:{self.server_port}")
    
    def read_server_info_from_file(self, filename='../config.txt'):
        """
        Lis le fichier config.txt afin d'en extraire l'IP et le Port du serveur et attribut les données à server_ip et server_port

        Paramètre :
        filename (str) : Nom du fichier
        """
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
    
    def start_server(self):
        """
        Démarre le serveur en lançant plusieurs threads.
        """
        try:
            threading.Thread(target=self.receive_messages).start() # Démarre un thread pour recevoir les messages des clients
            threading.Thread(target=self.remove_inactive_clients).start() # Démarre un thread pour supprimer les clients inactifs
            threading.Thread(target=self.update_queue).start() # Démarrer un thread pour mettre à jour la file d'attente

            while self.is_running : # Garde le programme en cours d'exécution si la condition est vraie
                time.sleep(1)
        
        except KeyboardInterrupt:
            self.stop_server()
    
    def receive_messages(self):
        """
        Écoute en permanence les messages envoyés par les clients.
        Fait différentes actions en fonction de l'intitulé du message.
        """
        while self.is_running:
            try:
                self.server_socket.settimeout(1)
                connection = sqlite3.connect("fusion.sqlite") # Se connecte avec la base de données
                cursor = connection.cursor() # Crée un curseur sur la base de données
                message_json, client_address = self.server_socket.recvfrom(1024) # Stocke le message du client dans message_json et stocke la provenant (IP/Port) du client dans un tuple client_address
                if message_json:
                    message = json.loads(message_json.decode()) # Stocke le message json décodé
                    match message[0]:
                        case "connection": # Si l'intitulé du message est "connection"
                            already_connected = any(message[1] in valeurs for valeurs in self.connected_clients.values()) # Vérifie si le clients est déjà connecté sur le serveur
                            if already_connected :
                                reponse = ["already_connected"] # Création d'un message avec l'intitulé "already_connected"
                                reponse_json = json.dumps(reponse) # Transforme les données en json
                                self.server_socket.sendto(reponse_json.encode(), client_address) # Envoie la réponse au client qui lui a envoyé le message
                            else:
                                password_bytes = message[2].encode('utf-8') # Encore le mot de passe en utf-8 et le stocke 
                                password_hashed = bcrypt.hashpw(password_bytes, bcrypt.gensalt()) # Chiffre le mot de passe avec bcrypt et le stocke

                                # Mise en forme d'une requête SQL
                                sql = ''' 
                                SELECT 1
                                FROM Joueur
                                WHERE pseudo = ?
                                LIMIT 1
                                '''
                                cursor.execute(sql, (message[1],)) # Exécute la requête SQL en remplaçant le "?" par le second paramètre, ici le tuple (message[1],)
                                                                    # message contient le pseudo du client
                                result = cursor.fetchone() # Récupère une valeur
                                if result: # Si une valeur est récupéré, c'est que le client est déjà enregistré dans le base de donnée
                                    print(f"Le joueur {message[1]} existe dans la base de données.")
                                    cursor.execute("SELECT Mot_de_passe FROM Joueur WHERE Pseudo = ?", (message[1],))
                                    result = cursor.fetchone() # Récupère le mot de passe du client
                                    if result and bcrypt.checkpw(password_bytes, result[0]) : # Vérifie si le mot de passe rentré par le client correspond au mot de passe déchiffré enregistré dans la base de données
                                        sql = '''
                                        UPDATE Joueur
                                        SET IP = ?, Port = ?
                                        WHERE Pseudo = ?
                                        '''
                                        data = (client_address[0], client_address[1], message[1]) # Mise à jour de l'IP/Port du client grâce à son pseudo
                                        cursor.execute(sql, data)
                                        connection.commit()
                                            
                                        infos = [message[1], 1000, 0, None, time.time()] # pseudo, MMR, en_recherche, id_partie, timestamp
                                        self.connected_clients[client_address] = infos # Stocke le client connecté dans le dictionnaire

                                        reponse = ["connected"] # Crée l'intitulé de la réponse 
                                        reponse_json = json.dumps(reponse) # Transforme les données en json
                                        self.server_socket.sendto(reponse_json.encode(), client_address) # Envoie de la réponse
                                    else : # Si les mots de passe ne correspondent pas
                                        reponse = ["rejected"]
                                        reponse_json = json.dumps(reponse)
                                        self.server_socket.sendto(reponse_json.encode(), client_address)
                                    
                                else : # Le client n'existe pas dans la base de données, première connexion
                                    print(f"Le joueur {message[1]} est un nouvel utilisateur")
                                    # Mise en forme d'une requête INSERT INTO
                                    sql = '''
                                    INSERT INTO Joueur (Pseudo, Mot_de_passe, IP, Port, MMR)
                                    VALUES (?, ?, ?, ?, ?)
                                    '''
                                    data = (message[1], password_hashed, client_address[0], client_address[1], 1000) # Ajoute le pseudo, mot de passe, IP, Port et MMR (1000 par défaut)
                                    cursor.execute(sql, data)
                                    connection.commit() # Enregistre les modifications

                                    infos = [message[1], 1000, 0, None, time.time()]
                                    self.connected_clients[client_address] = infos

                                    reponse = ["connected"]
                                    reponse_json = json.dumps(reponse)
                                    self.server_socket.sendto(reponse_json.encode(), client_address)
                                
                                password_bytes = None # Supprime le mot de passé encodé afin de ne pas le garder en mémoire
                                password_hashed = None # Supprime le mot de passé chiffré afin de ne pas le garder en mémoire

                        case "alive" : # Si l'intitulé du message est "connection"
                            self.connected_clients[client_address][4] = time.time() # Mise à jour du timestamp du client
                            print(f"Message reçu de {client_address}: {message_json.decode()}")
                            self.server_socket.sendto("Vous êtes toujours connecté".encode('utf-8'), client_address) # Réponse au client
                            
                        case "search_game":
                            # Mise en forme d'une requête SQL pour récupérer le MMR du client
                            sql = '''
                            SELECT MMR
                            FROM Joueur
                            WHERE pseudo = ?
                            '''
                            cursor.execute(sql, (self.connected_clients[client_address][0],))

                            mmr_client = cursor.fetchone()[0]
                            self.connected_clients[client_address][1] = mmr_client # Mise à jour du MMR du client

                            print(f"MMR de {self.connected_clients[client_address][0]} est : mmr_client = {mmr_client}, clients[clients_address] = {self.connected_clients[client_address][1]}")
                            
                            self.connected_clients[client_address][2] = 1 # Passe le client en recherche de partie
                            
                            reponse = ["search_game", "Vous etes en recherche de partie"]
                            reponse_json = json.dumps(reponse)
                            self.server_socket.sendto(reponse_json.encode(), client_address)
                        
                        case "quit_queue":
                            self.connected_clients[client_address][2] = 0 # Le client n'est plus en recherche de partie
                            if client_address in self.queue : # Si le client est présent dans la file d'attente
                                self.queue.remove(client_address) # Retrait de la file d'attente
                            print(f"Retrait du joueur {self.connected_clients[client_address][0]} de la file d'attente ({self.connected_clients[client_address]})")
                            reponse = ["retrait file attente"]
                            reponse_json = json.dumps(reponse)
                            self.server_socket.sendto(reponse_json.encode(), client_address)

                        case "game_found":
                            if self.connected_clients[client_address][3] != None : # Si le client a un id_partie attribué 
                                # Crée une réponse avec l'intitulé "Yes" ainsi que le joueur qui doit joué et le pseudo de l'adversaire
                                reponse = ["Yes", self.games[self.connected_clients[client_address][3]].current_player, self.games[self.connected_clients[client_address][3]].joueurs[self.connected_clients[client_address][0]]] 
                                reponse_json = json.dumps(reponse)
                                self.server_socket.sendto(reponse_json.encode(), client_address)
                                
                            else:
                                # Crée une réponse avec l'intitulé "No"
                                reponse = ["No"]
                                reponse_json = json.dumps(reponse)
                                self.server_socket.sendto(reponse_json.encode(), client_address)
                        
                        case "play_here":
                            # Appel de la méthode jouer() de la partie dans laquelle le client est 
                            self.games[self.connected_clients[client_address][3]].jouer(message[1], message[2], self.connected_clients[client_address][0]) # row, col, addr_joueur,)

                        case "update_game":
                            if self.connected_clients[client_address][3] not in self.games : # Si la partie de laquelle le client demande une mise à jour n'existe plus
                                reponse = ["game_lost"]
                                reponse_json = json.dumps(reponse)
                                self.server_socket.sendto(reponse_json.encode(), client_address)
                                self.connected_clients[client_address][3] = None # Supprime l'id_partie dans laquelle le client était
                                
                            else : # Si la partie de laquelle le client demande une mise à jour existe toujours
                                # Si le timestamp de la dernière action dans la partie dans laquelle le client est, est supérieur au timestamp de la dernière mise à jour du client
                                if self.games[self.connected_clients[client_address][3]].temps_derniere_action > message[1] : 
                                    current_player = self.games[self.connected_clients[client_address][3]].current_player # Récupère le pseudo du joueur qui doit jouer
                                    actions = self.games[self.connected_clients[client_address][3]].get_actions_after_time(message[1]) # Récupère toutes les actions depuis la dernière mise à jour avec la méthode get_actions_after_time()
                                    if actions[len(actions)-1][3] is True : # Si la partie est finie
                                        new_mmr = 1000
                                        if self.connected_clients[client_address][0] == actions[len(actions)-1][4] : # Si le client est le gagnant
                                            new_mmr = self.connected_clients[client_address][1] + 5 # Stocke son MMR + 5 
                                        elif self.connected_clients[client_address][0] == actions[len(actions)-1][5] : # Si le client est le perdant
                                            new_mmr = self.connected_clients[client_address][1] - 5 # Stocke son MMR - 5
                                        else : # S'il y a match nul
                                            new_mmr = self.connected_clients[client_address][1] # Aucune modification au MMR
                                        
                                        # Mise en forme d'une requête SQL pour mettre à jour le MMR du joueur
                                        sql = '''
                                        UPDATE Joueur
                                        SET MMR = ?
                                        WHERE Pseudo = ?
                                        '''
                                        data = (new_mmr, self.connected_clients[client_address][0])
                                        cursor.execute(sql, data)
                                        connection.commit()

                                    reponse = ["new_action", actions, current_player]
                                    reponse_json = json.dumps(reponse)
                                    self.server_socket.sendto(reponse_json.encode(), client_address)
                                else:
                                    reponse = ["no_new_actions"]
                                    reponse_json = json.dumps(reponse)
                                    self.server_socket.sendto(reponse_json.encode(), client_address)

                        case "get_board":
                            board = self.games[self.connected_clients[client_address][3]].get_board() # Récupère le plateau de jeu de la partie sur le serveur dans laquelle est le client
                            reponse = ["full_board", board]
                            reponse_json = json.dumps(reponse)
                            self.server_socket.sendto(reponse_json.encode(), client_address)
                        
                        case "update_chat":
                            if self.connected_clients[client_address][3] in self.games : # Si la partie de laquelle le client demande une mise à jour du chat existe toujours
                                # Si le timestamp du dernier message dans la partie dans laquelle le client est, est supérieur au timestamp de la dernière mise à jour du chat du client
                                if self.games[self.connected_clients[client_address][3]].chat.last_updated > message[1]:  
                                    messages = self.games[self.connected_clients[client_address][3]].chat.get_messages_after_time(message[1]) # Récupère les nouveaux messages
                                    reponse = ["new_msg", messages]
                                    reponse_json = json.dumps(reponse)
                                    self.server_socket.sendto(reponse_json.encode(), client_address)
                                else: # Pas de nouveau message
                                    reponse = ["ras"]
                                    reponse_json = json.dumps(reponse)
                                    self.server_socket.sendto(reponse_json.encode(), client_address)
                            else:
                                reponse = ["ras"]
                                reponse_json = json.dumps(reponse)
                                self.server_socket.sendto(reponse_json.encode(), client_address)

                        case "new_chat_message":
                            print(f"Dans chat {client_address} Pseudo : {self.connected_clients[client_address][0]}")
                            # Ajoute le message dans le chat de la partie dans laquelle le joueur est 
                            self.games[self.connected_clients[client_address][3]].chat.add_message(self.connected_clients[client_address][0], message[1])
                            # Mise en place d'une requête SQL pour stocker le message envoyé
                            sql = '''
                            INSERT INTO HistoriqueMessages (Pseudo, Id_Partie, Contenu)
                            VALUES (?, ?, ?)
                            '''
                            data = (self.connected_clients[client_address][0], self.connected_clients[client_address][3], message[1]) # Le pseudo du joueur, dans quelle partie et le contenu du message
                            cursor.execute(sql, data)
                            connection.commit()
                    
                        case "quit_game":
                            reponse = ["left_game"]
                            reponse_json = json.dumps(reponse)
                            self.server_socket.sendto(reponse_json.encode(), client_address)
                            del self.games[self.connected_clients[client_address][3]] # Supprime la partie du dictionnaire
                            self.connected_clients[client_address][3] = None # Retire l'id_partie du client

                        case "disconnect":
                            del self.connected_clients[client_address] # Supprime le client du dictionnaire des clients connectés
                            if client_address in self.queue : # Si le joueur était en recherche de partie (dans la file d'attente)
                                self.queue.remove(client_address) # Retire le joueur de la file d'attente
                            self.server_socket.sendto(f"Pseudo : {message[1]}, vous êtes déconnecté.".encode('utf-8'), client_address)
                            print(f"Client {client_address} supprimé pour déconnexion.")
                        
                        case _:
                            print(f"Message {message[0]} non géré ")
                    
                connection.close() # Ferme la connexion avec la base de données

            except socket.timeout:
                continue

            except Exception as e:
                print(f"Erreur lors de la réception du message : {e}")

    def remove_inactive_clients(self):
        """
        Supprime les clients qui n'ont pas envoyé de message depuis plus de 15 secondes.
        (C'est ici que sert la fonction stay_connected() de UDPClient, si un message n'est pas envoyé régulièrement et que l'utilisateur ne fait pas d'action, il serait déconnecté.
        Permet également de libérer l'adversaire si le client a fermé son client ou a perdu la connexion avec le serveur.)
        """
        while self.is_running:
            try:
                current_time = time.time() # Récupère le timestamp actuel
                inactive_clients = [address for address, values in self.connected_clients.items() if current_time - values[4] > 15] # Liste de tous les clients inactifs
                for address in inactive_clients: # Pour chaque client inactif 
                    if address in self.queue:
                        self.queue.remove(address) # Supprime de la file d'attente
                    
                    if self.connected_clients[address][3] in self.games :
                        del self.games[self.connected_clients[address][3]] # Supprime la partie dans laquelle le joueur était connecté
                    
                    del self.connected_clients[address] # Supprime le client du dictionnaire des clients connectés

                    print(f"Client {address} supprimé pour inactivité.")
                time.sleep(1)

            except Exception as e:
                print(f"Erreur lors de la suppression des clients inactifs : {e}")
    
    def update_queue(self):
        """
        Met à jour la file d'attente en ajoutant les clients qui sont en recherche de partie et en supprimant les clients qui ne le sont plus.
        """
        while self.is_running:
            for client_address, values in self.connected_clients.items():
                if values[2] == 1: # Si le boléen "en_recherche" est vraie
                    if not client_address in self.queue:
                        self.queue.append(client_address)
                        print(f"Joueur {self.connected_clients[client_address][0]} a été ajouté à la file d'attente")
                
                else: # Inutile si on retire correctement les joueurs quand ils ne recherchent plus une partie ou bien s'ils sont déjà dans une partie
                    if client_address in self.queue:
                        self.queue.remove(client_address)
                        print(f"Joueur {self.connected_clients[client_address][0]} a été retiré de la file d'attente")

            print(f"Nombre de joueurs dans la file d'attente {len(self.queue)}")
            self.find_matching_players() # Appel la méthode find_matching_players() afin de créer des parties 
            time.sleep(1)
    
    def find_matching_players(self):
        """
        Recherche des clients qui recherche une partie et ayant un MMR proche afin de créer des parties
        """
        for client_address in self.queue: # Parcours les clients en recherche de partie
            for other_client_address in self.queue: # Parcours à nouveau les clients en recherche de partie
                mmr_p1 = self.connected_clients[client_address][1] # Récupère le MMR du premier client
                mmr_p2 = self.connected_clients[other_client_address][1] # Récupère le MMR du deuxième client
                diff_mmr = abs(mmr_p1 - mmr_p2) # Calcule la différence de MMR entre les deux clients
                # Si la différence de MMR est inférieure à 51 et que ceux sont deux clients différents
                if client_address != other_client_address and self.connected_clients[client_address][0] != self.connected_clients[other_client_address][0] and diff_mmr < 51:
                    generated_id_partie = self.generate_id_unique() # Stocke un id de partie généré avec la méthode generate_id_unique()
                    partie = MorpionServeur(generated_id_partie, self.connected_clients[client_address][0], self.connected_clients[other_client_address][0]) # Crée une partie
                    self.games[partie.id_partie] = partie # Stocke la partie dans le dictionnaire games

                    # Attribue aux deux clients l'id de leur partie
                    self.connected_clients[client_address][3] = generated_id_partie 
                    self.connected_clients[other_client_address][3] = generated_id_partie

                    # Retire les deux clients qui viennent de trouver une partie de la liste d'attente
                    self.queue.remove(client_address)
                    self.queue.remove(other_client_address)

                    # Modifie le statut d'attente des deux clients pour dire qu'ils ne sont plus en attente d'une partie
                    self.connected_clients[client_address][2] = 0
                    self.connected_clients[other_client_address][2] = 0
                    print("Partie créée")
                else: 
                    print("Aucune partie créée")

    def generate_id_unique(self):
        """
        Génère un ID de partie unique de 8 caractères tant que l'ID en question n'est pas unique (qui n'a jamais existé dans la base de données).
        """
        connection = sqlite3.connect("fusion.sqlite")
        cursor = connection.cursor()
        while True:
            id_partie = ''.join(random.choices(string.ascii_letters + string.digits, k=8)) # Génère un ID aléatoire
            cursor.execute("SELECT Id_Partie FROM HistoriqueParties WHERE Id_Partie = ?", (id_partie,)) # Vérifie si l'identifiant existe déjà dans la base de données
            result = cursor.fetchone()
            if not result: # Si l'identifiant n'existe pas, retourner l'identifiant généré
                connection.close()
                return id_partie

    def stop_server(self):
        """
        Arrête le serveur.
        """
        self.is_running = False # Passe la condition de marche à False
        self.server_socket.close() # Ferme le socket
        print("Serveur arrêté")


if __name__ == "__main__":
    server = UDPServer() # Crée un objet UDPServer
    server.start_server() # Démarre le serveur
