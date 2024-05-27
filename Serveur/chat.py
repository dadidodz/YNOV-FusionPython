import time

class Chat:
    """
    Classe Chat

    Attributs : 
        chat_history (list) : Liste permettant de stocker les messages envoyés dans le chat
        last_update (float) : timestamp de la dernière fois où un message a été envoyé
    """
    def __init__(self):
        """
        Initialise les attributs de Chat.
        """
        self.chat_history = []
        self.last_updated = time.time()
    
    def add_message(self, pseudo, message):
        """
        Ajoute un message dans le chat.

        Paramètres :
        pseudo (str) : Pseudo du joueur qui a envoyé le message
        message (str) : Contenu du message
        """
        self.chat_history.append((pseudo, message, time.time()))
        self.last_updated = time.time()
    
    def get_messages_after_time(self, timestamp):
        """
        Récupère les messages envoyé dans le chat depuis la dernière mise à jour du client.

        Paramètre :
        timestamp (float) : timestamp de la dernière fois que le joueur a mis à jour les messages de son chat

        Retour :
        messages_after_time (list) : Liste des nouveaux messages
        """
        messages_after_time = [(psd, msg) for psd, msg, msg_time in self.chat_history if msg_time > timestamp] # Récupérer les messages envoyés après le timestamp donné en paramètre
        return messages_after_time

