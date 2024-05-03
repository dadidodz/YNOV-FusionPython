import socket
import threading
import time
import json
from chat import Chat

class UDPServer:
    def __init__(self, host, port):
        self.SERVER_HOST = host
        self.SERVER_PORT = port
        self.clients = {}
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
                        self.clients[client_address] = time.time()
                        self.server_socket.sendto("Vous êtes toujours connecté".encode('utf-8'), client_address)
                        print(f"Message reçu de {client_address}: {data.decode()}")

                    if message_received[0] == "connexion":
                        self.server_socket.sendto(f"Pseudo : {message_received[1]}, vous êtes connecté.".encode('utf-8'), client_address)
                    
                    if message_received[0] == "chat":
                        print(f"Dans chat {client_address}: {message_received[1]}")
                        temp = (f"{message_received[1]}: {message_received[2]}")
                        self.chat.add_message(temp)
                        # self.server_socket.sendto(f"{message_received[1]}".encode('utf-8'), client_address)

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

                    if message_received[0] == "deconnexion":
                        del self.clients[client_address]
                        self.server_socket.sendto(f"Pseudo : {message_received[1]}, vous êtes déconnecté.".encode('utf-8'), client_address)
                        print(f"Client {client_address} supprimé pour déconnexion.")

            except Exception as e:
                print(f"Erreur lors de la réception du message : {e}")

    def remove_inactive_clients(self):
        while True:
            try:
                # Supprimer les clients qui n'ont pas envoyé de message depuis plus de 30 secondes
                current_time = time.time()
                inactive_clients = [address for address, timestamp in self.clients.items() if current_time - timestamp > 30]
                for address in inactive_clients:
                    del self.clients[address]
                    print(f"Client {address} supprimé pour inactivité.")
                time.sleep(30)
            except Exception as e:
                print(f"Erreur lors de la suppression des clients inactifs : {e}")

    def start_server(self):
        # Démarrer un thread pour recevoir les messages des clients
        threading.Thread(target=self.receive_messages).start()
        # Démarrer un thread pour supprimer les clients inactifs
        threading.Thread(target=self.remove_inactive_clients).start()
        # Garder le programme en cours d'exécution
        while True:
            time.sleep(1)

# Utilisation du serveur
if __name__ == "__main__":
    # server = UDPServer('10.34.0.248', 12345)
    server = UDPServer('192.168.1.45', 12345)
    server.start_server()
