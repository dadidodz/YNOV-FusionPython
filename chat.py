import time

class Chat:
    def __init__(self):
        self.historique = []  # Utilisation d'une liste pour stocker les messages
        self.last_updated = time.time()  # Initialisation du timestamp de la dernière modification
    
    def add_message(self, message):
        # Ajouter le message à la liste
        self.historique.append((message, time.time()))
        # Mettre à jour le timestamp de la dernière modification
        self.last_updated = time.time()
    
    def get_messages_after_time(self, timestamp):
        # Récupérer les messages envoyés après le temps donné
        messages_after_time = [msg for msg, msg_time in self.historique if msg_time > timestamp]
        return messages_after_time

